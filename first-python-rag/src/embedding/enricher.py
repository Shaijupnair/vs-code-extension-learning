"""
Code Enricher using LLM to generate summaries and keywords for code chunks.
"""

import asyncio
import json
import os
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeEnricher:
    """
    Enriches code chunks with LLM-generated summaries and keywords.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_concurrent: int = 5,
        mock_mode: bool = False
    ):
        """
        Initialize the code enricher.
        
        Args:
            api_key: OpenAI API key (or None to use env variable)
            model: Model to use for enrichment
            max_concurrent: Maximum concurrent API calls
            mock_mode: If True, uses mock responses instead of API calls
        """
        self.model = model
        self.max_concurrent = max_concurrent
        self.mock_mode = mock_mode
        
        # Initialize OpenAI client if not in mock mode
        if not mock_mode:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No API key provided. Running in mock mode.")
                self.mock_mode = True
            else:
                self.client = AsyncOpenAI(api_key=api_key)
                logger.info(f"Initialized OpenAI client with model: {model}")
        
        if self.mock_mode:
            logger.info("Running in MOCK MODE - no actual API calls will be made")
    
    async def enrich_batch(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich a batch of code chunks with summaries and keywords.
        
        Args:
            chunks: List of code chunk dictionaries with keys:
                   - method_name, method_signature, method_body, class_context
                   
        Returns:
            List of enriched chunks with added 'summary' and 'keywords' fields
        """
        logger.info(f"Enriching {len(chunks)} code chunks...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Enrich all chunks concurrently
        tasks = [
            self._enrich_single_chunk(chunk, semaphore, idx)
            for idx, chunk in enumerate(chunks)
        ]
        
        enriched_chunks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        successful = []
        failed = 0
        for result in enriched_chunks:
            if isinstance(result, Exception):
                logger.error(f"Enrichment failed: {result}")
                failed += 1
            else:
                successful.append(result)
        
        logger.info(f"Enrichment complete: {len(successful)} successful, {failed} failed")
        return successful
    
    async def _enrich_single_chunk(
        self,
        chunk: Dict[str, Any],
        semaphore: asyncio.Semaphore,
        idx: int
    ) -> Dict[str, Any]:
        """
        Enrich a single code chunk.
        
        Args:
            chunk: Code chunk dictionary
            semaphore: Semaphore for concurrency control
            idx: Index for logging
            
        Returns:
            Enriched chunk with summary and keywords
        """
        async with semaphore:
            if self.mock_mode:
                return await self._mock_enrich(chunk, idx)
            else:
                return await self._llm_enrich(chunk, idx)
    
    async def _llm_enrich(self, chunk: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """
        Enrich using actual LLM API call.
        Adds safety check for oversized chunks.
        """
        # Safety: Check chunk size before processing
        MAX_METHOD_BODY = 50000  # 50KB max (~1250 lines) - catches only extreme cases
        method_body = chunk.get('method_body', '')
        
        if len(method_body) > MAX_METHOD_BODY:
            logger.warning(
                f"Chunk {idx} ({chunk.get('method_name', 'unknown')}) too large "
                f"({len(method_body)} bytes), using fallback enrichment"
            )
            chunk['summary'] = f"Large method: {chunk.get('method_name', 'unknown')} (too large for LLM analysis)"
            chunk['keywords'] = [chunk.get('method_name', 'unknown'), 'large-method', 'auto-generated']
            return chunk
        
        # Construct prompt
        prompt = self._build_prompt(chunk)
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Java code analysis expert. Analyze code and provide concise summaries and search keywords in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse response
            content = response.choices[0].message.content
            enrichment = self._parse_llm_response(content)
            
            # Add enrichment to chunk
            chunk['summary'] = enrichment.get('summary', 'Summary not available')
            chunk['keywords'] = enrichment.get('keywords', [])
            
            logger.debug(f"Enriched chunk {idx}: {chunk['method_name']}")
            return chunk
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for chunk {idx}: {e}")
            return self._add_fallback_enrichment(chunk)
            
        except Exception as e:
            logger.error(f"API error for chunk {idx}: {e}")
            return self._add_fallback_enrichment(chunk)
    
    async def _mock_enrich(self, chunk: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """
        Mock enrichment for testing without API calls.
        """
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        method_name = chunk.get('method_name', 'unknown')
        
        # Generate mock summary
        if method_name == '<Constructor>':
            summary = f"Constructor that initializes a new instance with provided parameters"
        else:
            summary = f"Method {method_name} performs business logic operations"
        
        # Generate mock keywords
        keywords = [
            method_name.lower() if method_name != '<Constructor>' else 'constructor',
            'java',
            'method'
        ]
        
        # Add dependencies as keywords if present
        if 'dependency_types' in chunk and chunk['dependency_types']:
            keywords.extend([dep.lower() for dep in chunk['dependency_types'][:2]])
        
        chunk['summary'] = summary
        chunk['keywords'] = keywords[:5]  # Limit to 5 keywords
        
        logger.debug(f"Mock enriched chunk {idx}: {method_name}")
        return chunk
    
    def _build_prompt(self, chunk: Dict[str, Any]) -> str:
        """
        Build the context-aware enrichment prompt for a code chunk.
        Leverages inheritance, dependencies, and structural information.
        """
        method_name = chunk.get('method_name', 'unknown')
        method_sig = chunk.get('method_signature', '')
        method_body = chunk.get('method_body', '')
        class_context = chunk.get('class_context', '')
        dependencies = chunk.get('dependency_types', [])
        
        # Extract package name from class_context
        package_name = "Unknown"
        if 'Package: ' in class_context:
            # Format: "Package: com.example, Class: ..."
            package_part = class_context.split(',')[0]
            package_name = package_part.replace('Package: ', '').strip()
        
        # Format dependencies
        dependencies_str = ", ".join(dependencies) if dependencies else "None"
        
        # Truncate body if too long (but keep more for better context)
        max_body_length = 800
        if len(method_body) > max_body_length:
            method_body = method_body[:max_body_length] + "\n... (truncated)"
        
        prompt = f"""System: You are a senior Java Architect. I will provide a method, its class context, and its dependencies.
Your goal is to explain the *intent* of this code for a semantic search engine.

--- CONTEXT ---
1. Package: {package_name}
   (Note: Use this to understand the module/component this code belongs to)
2. Class Context: {class_context}
   (Note: Includes fields and inherited methods if applicable)
3. Method Signature: {method_sig}
4. Dependencies: {dependencies_str}
   (Note: Custom types used as parameters - may need instantiation)

--- CODE ---
{method_body}

--- TASK ---
1. Summary: Write a 1-sentence summary of the BUSINESS LOGIC. Do not explain syntax.
   - Good: "Calculates the tax rate based on the transaction type."
   - Bad: "Takes an integer and returns a float."
   - For constructors: Focus on initialization purpose, not implementation details.
2. Keywords: List 3-5 synonyms or technical terms a user might search for to find this code.
   - Use domain-specific terms
   - Include operation verbs (e.g., for 'kill' → ['terminate', 'end', 'stop'])
   - Include class/type names from context and dependencies

--- OUTPUT FORMAT ---
Return ONLY raw JSON (no markdown, no code blocks):
{{
  "summary": "Your 1-sentence business logic summary here",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}
"""
        return prompt
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response with error handling.
        """
        try:
            data = json.loads(content)
            
            # Validate structure
            if 'summary' not in data:
                raise ValueError("Missing 'summary' field")
            if 'keywords' not in data:
                raise ValueError("Missing 'keywords' field")
            if not isinstance(data['keywords'], list):
                raise ValueError("'keywords' must be a list")
            
            # Ensure keywords are strings
            data['keywords'] = [str(k) for k in data['keywords'][:5]]
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {content}")
            raise
            
        except ValueError as e:
            logger.error(f"Invalid response structure: {e}")
            raise
    
    def _add_fallback_enrichment(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add fallback enrichment when LLM call fails.
        """
        method_name = chunk.get('method_name', 'unknown')
        
        chunk['summary'] = f"Method {method_name} - enrichment unavailable"
        chunk['keywords'] = [method_name.lower(), 'java']
        
        return chunk


# Convenience function
async def enrich_code_chunks(
    chunks: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    mock_mode: bool = False
) -> List[Dict[str, Any]]:
    """
    Convenience function to enrich code chunks.
    
    Args:
        chunks: List of code chunks to enrich
        api_key: OpenAI API key
        model: Model to use
        mock_mode: Use mock responses instead of API
        
    Returns:
        Enriched chunks
    """
    enricher = CodeEnricher(api_key=api_key, model=model, mock_mode=mock_mode)
    return await enricher.enrich_batch(chunks)
