#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Validator
Validates knowledge artifacts for quality and consistency.
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

logger = logging.getLogger("maha-sales-engine.knowledge.validator")


@dataclass
class ValidationResult:
    is_valid: bool
    score: float
    issues: List[str]
    suggestions: List[str]
    validated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeValidator:
    """
    Knowledge validator that ensures quality and consistency.
    """
    
    def __init__(self):
        self.rules = [
            {"name": "content_length", "min_length": 10, "max_length": 10000},
            {"name": "required_fields", "fields": ["title", "content", "source"]},
            {"name": "source_validation", "allowed_sources": ["optimization", "marketing", "sales", "product", "customer"]}
        ]
    
    def validate(self, knowledge_item: Dict[str, Any]) -> ValidationResult:
        """Validate knowledge item"""
        issues = []
        suggestions = []
        
        # Check content length
        content = knowledge_item.get("content", "")
        if isinstance(content, dict):
            content = json.dumps(content)
        
        if len(content) < 10:
            issues.append("Content too short")
        elif len(content) > 10000:
            issues.append("Content too long")
        
        # Check required fields
        for rule in self.rules:
            if rule["name"] == "required_fields":
                for field in rule["fields"]:
                    if field not in knowledge_item:
                        issues.append(f"Missing required field: {field}")
        
        # Check source
        source = knowledge_item.get("source", "")
        valid_sources = ["optimization", "marketing", "sales", "product", "customer", "system"]
        if source and source not in valid_sources:
            issues.append(f"Invalid source: {source}")
            suggestions.append(f"Use one of: {', '.join(valid_sources)}")
        
        # Calculate score
        score = max(0.0, 1.0 - (len(issues) * 0.2))
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=score,
            issues=issues,
            suggestions=suggestions
        )


def main():
    print("Knowledge Validator loaded")


if __name__ == "__main__":
    main()
