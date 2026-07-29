#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Document Indexer
Indexes documents from all knowledge sources.
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

logger = logging.getLogger("maha-sales-engine.knowledge.indexer")


@dataclass
class IndexedDocument:
    document_id: str
    source: str
    title: str
    content: str
    metadata: Dict[str, Any]
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DocumentIndexer:
    """
    Document indexer for knowledge platform.
    """
    
    def __init__(self, db_manager, embedding_service):
        self.db = db_manager
        self.embedding_service = embedding_service
        self._documents: Dict[str, IndexedDocument] = {}
    
    def index(self, source: str, title: str, content: str, metadata: Dict[str, Any] = None) -> IndexedDocument:
        """Index document"""
        document_id = f"doc-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        document = IndexedDocument(
            document_id=document_id,
            source=source,
            title=title,
            content=content,
            metadata=metadata or {}
        )
        
        self._documents[document_id] = document
        logger.info(f"Document indexed: {document_id} from {source}")
        return document
    
    def get_document(self, document_id: str) -> Optional[IndexedDocument]:
        """Get document by ID"""
        return self._documents.get(document_id)
    
    def search(self, query: str, source: Optional[str] = None) -> List[IndexedDocument]:
        """Search documents"""
        results = []
        query_lower = query.lower()
        
        for doc in self._documents.values():
            if source and doc.source != source:
                continue
            
            if query_lower in doc.title.lower() or query_lower in doc.content.lower():
                results.append(doc)
        
        return results


def main():
    print("Document Indexer loaded")


if __name__ == "__main__":
    main()
