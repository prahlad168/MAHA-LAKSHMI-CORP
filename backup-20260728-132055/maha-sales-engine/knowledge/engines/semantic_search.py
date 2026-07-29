#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Semantic Search
Natural-language search across documentation, policies, past decisions, experiments, recommendations, and operational events.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.semantic")


@dataclass
class SearchResult:
    result_id: str
    knowledge_id: str
    score: float
    snippet: str
    metadata: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SemanticSearch:
    """
    Semantic search engine for knowledge platform.
    """
    
    def __init__(self, embedding_service, db_manager):
        self.embedding_service = embedding_service
        self.db = db_manager
        self._index: Dict[str, List[float]] = {}
    
    def index_document(self, knowledge_id: str, text: str, metadata: Dict[str, Any] = None):
        """Index document for semantic search"""
        embedding = self.embedding_service.embed(text)
        self._index[knowledge_id] = embedding
        logger.info(f"Document indexed: {knowledge_id}")
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Semantic search"""
        query_embedding = self.embedding_service.embed(query)
        
        # Calculate similarities
        similarities = []
        for knowledge_id, embedding in self._index.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((knowledge_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = []
        for knowledge_id, score in similarities[:top_k]:
            results.append(SearchResult(
                result_id=f"result-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}",
                knowledge_id=knowledge_id,
                score=score,
                snippet=f"Document {knowledge_id}",
                metadata={"knowledge_id": knowledge_id}
            ))
        
        return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x * x for x in a) ** 0.5
        magnitude_b = sum(x * x for x in b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)


def main():
    print("Semantic Search loaded")


if __name__ == "__main__":
    main()
