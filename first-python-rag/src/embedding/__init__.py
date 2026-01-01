"""Embedding module for code enrichment and vector generation."""

from .enricher import CodeEnricher, enrich_code_chunks

__all__ = ['CodeEnricher', 'enrich_code_chunks']
