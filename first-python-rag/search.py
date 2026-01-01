"""
RAG Search Interface for Java Code.
Supports query expansion, semantic search, and formatted results.
Configuration is loaded from config.ini file.
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import configparser

# Load environment variables
load_dotenv()

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.vector_store import VectorStore


class CodeSearchEngine:
    """
    Search engine for Java code with query expansion.
    """
    
    def __init__(
        self,
        db_path: str = "./data/lancedb",
        use_query_expansion: bool = True,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize search engine.
        
        Args:
            db_path: Path to vector database
            use_query_expansion: Enable LLM query expansion
            model: OpenAI model for query expansion
        """
        self.db_path = db_path
        self.use_query_expansion = use_query_expansion
        self.model = model
        
        # Initialize vector store
        print("Initializing search engine...")
        self.vector_store = VectorStore(db_path=db_path)
        
        # Initialize OpenAI client for query expansion
        if use_query_expansion:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                print("✓ Query expansion enabled")
            else:
                print("⚠️  No API key found, query expansion disabled")
                self.use_query_expansion = False
        
        # Get database stats
        stats = self.vector_store.get_stats()
        print(f"✓ Connected to database: {stats['count']} code chunks indexed")
    
    async def expand_query(self, query: str) -> List[str]:
        """
        Expand user query into multiple variations using LLM.
        
        Args:
            query: Original user query
            
        Returns:
            List of query variations (including original)
        """
        if not self.use_query_expansion:
            return [query]
        
        prompt = f"""You are helping expand a search query for a Java code search engine.

Original query: "{query}"

Generate 2-3 alternative phrasings of this query that might help find relevant Java code.
Focus on:
- Technical synonyms (e.g., "click" → "select", "activate")
- Different abstraction levels (e.g., "widget" → "UI element", "control")
- Common Java terminology

Return ONLY a JSON array of strings, no explanation.

Example:
["original query variation 1", "technical variation 2", "abstraction variation 3"]
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Java code search expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Handle both array and object responses
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    variations = parsed
                elif isinstance(parsed, dict):
                    # Try to extract array from dict
                    variations = parsed.get('queries', parsed.get('variations', [query]))
                else:
                    variations = [query]
                
                # Always include original query
                if query not in variations:
                    variations.insert(0, query)
                
                return variations[:3]  # Limit to 3 variations
                
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse query expansion, using original")
                return [query]
        
        except Exception as e:
            print(f"⚠️  Query expansion failed: {e}, using original")
            return [query]
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        expand: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for code matching the query.
        
        Args:
            query: User search query
            limit: Number of results
            expand: Use query expansion
            
        Returns:
            List of search results with metadata
        """
        print(f"\n🔍 Searching for: \"{query}\"")
        
        # Expand query if enabled
        if expand and self.use_query_expansion:
            print("   Expanding query...")
            queries = await self.expand_query(query)
            print(f"   Variations: {len(queries)}")
            for i, q in enumerate(queries, 1):
                print(f"     {i}. \"{q}\"")
        else:
            queries = [query]
        
        # Search with all query variations and combine results
        all_results = []
        seen_ids = set()
        
        for query_var in queries:
            # Use retrieval.query task for query embedding
            results = self.vector_store.search(
                query_var,
                limit=limit * 2,  # Get more to deduplicate
                task="retrieval.query"
            )
            
            # Add unique results
            for result in results:
                result_id = result.get('id')
                if result_id not in seen_ids:
                    seen_ids.add(result_id)
                    all_results.append(result)
        
        # Sort by distance (lower is better) and limit
        all_results.sort(key=lambda x: x.get('_distance', float('inf')))
        
        return all_results[:limit]
    
    def format_result(self, result: Dict[str, Any], rank: int) -> str:
        """
        Format a search result for display.
        
        Args:
            result: Search result dictionary
            rank: Result rank (1-based)
            
        Returns:
            Formatted string
        """
        # Parse metadata
        metadata = result.get('metadata_parsed', {})
        if not metadata and 'metadata' in result:
            try:
                metadata = json.loads(result['metadata'])
            except:
                metadata = {}
        
        # Extract fields
        method_name = metadata.get('method_name', 'Unknown')
        package = metadata.get('package', 'Unknown')
        signature = metadata.get('signature', 'Unknown')
        file_path = metadata.get('file_path', 'Unknown')
        dependencies = metadata.get('dependencies', [])
        inherited_methods = metadata.get('inherited_methods', [])
        
        # Get summary from search_text or metadata
        search_text = result.get('search_text', '')
        summary = "No summary available"
        if 'Summary:' in search_text:
            summary_start = search_text.index('Summary:') + len('Summary:')
            summary_end = search_text.find('|', summary_start)
            if summary_end > 0:
                summary = search_text[summary_start:summary_end].strip()
        
        # Get code
        code = result.get('code', 'Code not available')
        
        # Calculate similarity score (inverse of distance)
        distance = result.get('_distance', 0)
        score = max(0, 1 - distance)  # Simple normalization
        
        # Build formatted output
        output = f"""
{'=' * 80}
Result #{rank} - {method_name}
{'=' * 80}

📊 Relevance Score: {score:.2%}
📦 Package: {package}
✍️  Signature: {signature}
📁 File: {file_path}

💡 Summary:
{summary}
"""
        
        # Add dependencies if present
        if dependencies:
            output += f"\n🔗 Dependencies: {', '.join(dependencies)}"
        
        # Add inherited methods if present
        if inherited_methods:
            inherited_str = ', '.join(inherited_methods[:5])
            if len(inherited_methods) > 5:
                inherited_str += f" (+{len(inherited_methods) - 5} more)"
            output += f"\n👨‍👦 Inherited Methods: [{inherited_str}]"
        
        # Add code
        output += f"\n\n💻 Code:\n```java\n{code}\n```"
        
        return output
    
    async def interactive_search(self):
        """
        Run interactive search loop.
        """
        print("\n" + "=" * 80)
        print("Java Code Search Engine")
        print("=" * 80)
        print("Enter your search query (or 'quit' to exit)")
        print("Examples:")
        print("  - How do I click a widget?")
        print("  - Find perspective by label")
        print("  - Process transaction validation")
        print("=" * 80)
        
        while True:
            try:
                query = input("\n🔍 Query: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                # Search
                results = await self.search(query, limit=5)
                
                # Display results
                print(f"\n📋 Found {len(results)} results:")
                
                if not results:
                    print("\n   No results found. Try a different query.")
                    continue
                
                for i, result in enumerate(results, 1):
                    print(self.format_result(result, i))
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point - reads configuration from config.ini."""
    
    # Read configuration from config.ini
    DB_PATH = config.get('Paths', 'database_path', fallback='./data/lancedb')
    USE_QUERY_EXPANSION = config.getboolean('Search', 'use_query_expansion', fallback=True)
    SEARCH_LIMIT = config.getint('Search', 'search_results_limit', fallback=5)
    
    # Create search engine
    search_engine = CodeSearchEngine(
        db_path=DB_PATH,
        use_query_expansion=USE_QUERY_EXPANSION
    )
    
    # Check if running with command line query
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        results = await search_engine.search(query, limit=SEARCH_LIMIT)
        
        print(f"\n📋 Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(search_engine.format_result(result, i))
    else:
        # Interactive mode
        await search_engine.interactive_search()


if __name__ == "__main__":
    asyncio.run(main())
