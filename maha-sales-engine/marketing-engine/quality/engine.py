#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Content Quality Engine
Validate and score marketing content quality.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.quality")


@dataclass
class QualityCheck:
    """Individual quality check"""
    name: str
    passed: bool
    score: float
    issues: List[str]


@dataclass
class QualityReport:
    """Quality report"""
    overall_score: float
    passed: bool
    checks: List[QualityCheck]
    issues: List[str]
    recommendations: List[str]


class ContentQualityEngine:
    """Validate and score marketing content"""
    
    CHECKS = [
        "grammar",
        "readability",
        "length",
        "duplicate_content",
        "keyword_density",
        "metadata_completeness",
        "brand_consistency",
        "tone_consistency",
        "formatting"
    ]
    
    def __init__(self, brand_engine):
        self.brand_engine = brand_engine
    
    def validate_content(self, content: str, content_type: str, keywords: List[str], 
                        brand_rules: Dict[str, Any]) -> QualityReport:
        """Validate content quality"""
        try:
            checks = []
            issues = []
            recommendations = []
            total_score = 0.0
            
            # Run checks
            checks.append(self._check_grammar(content))
            checks.append(self._check_readability(content))
            checks.append(self._check_length(content, content_type))
            checks.append(self._check_keyword_density(content, keywords))
            checks.append(self._check_formatting(content))
            checks.append(self._check_brand_consistency(content, brand_rules))
            
            for check in checks:
                total_score += check.score
                if not check.passed:
                    issues.extend(check.issues)
            
            overall_score = total_score / len(checks) if checks else 0.0
            passed = overall_score >= 0.8 and len(issues) == 0
            
            if not passed:
                recommendations = self._generate_recommendations(checks, issues)
            
            return QualityReport(
                overall_score=overall_score,
                passed=passed,
                checks=checks,
                issues=issues,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            return QualityReport(
                overall_score=0.0,
                passed=False,
                checks=[],
                issues=[str(e)],
                recommendations=["Fix validation errors"]
            )
    
    def _check_grammar(self, content: str) -> QualityCheck:
        """Check grammar"""
        issues = []
        
        # Basic checks
        if "  " in content:
            issues.append("Double spaces found")
        
        if content.count("!") > 5:
            issues.append("Too many exclamation marks")
        
        score = 1.0 if not issues else 0.7
        return QualityCheck(
            name="grammar",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _check_readability(self, content: str) -> QualityCheck:
        """Check readability"""
        issues = []
        
        # Simple readability check
        words = content.split()
        sentences = content.split('.')
        
        if len(words) > 0 and len(sentences) > 0:
            avg_words_per_sentence = len(words) / len(sentences)
            if avg_words_per_sentence > 25:
                issues.append("Sentences too long")
        
        score = 1.0 if not issues else 0.8
        return QualityCheck(
            name="readability",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _check_length(self, content: str, content_type: str) -> QualityCheck:
        """Check content length"""
        issues = []
        
        length_requirements = {
            "seo_title": (50, 60),
            "meta_description": (150, 160),
            "product_description": (150, 300),
            "landing_page": (500, 2000),
            "email": (200, 1000)
        }
        
        min_len, max_len = length_requirements.get(content_type, (100, 1000))
        content_len = len(content)
        
        if content_len < min_len:
            issues.append(f"Content too short: {content_len} chars (min: {min_len})")
        elif content_len > max_len:
            issues.append(f"Content too long: {content_len} chars (max: {max_len})")
        
        score = 1.0 if not issues else 0.6
        return QualityCheck(
            name="length",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _check_keyword_density(self, content: str, keywords: List[str]) -> QualityCheck:
        """Check keyword density"""
        issues = []
        
        if not keywords:
            return QualityCheck(name="keyword_density", passed=True, score=1.0, issues=[])
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return QualityCheck(name="keyword_density", passed=False, score=0.0, issues=["Empty content"])
        
        for keyword in keywords[:3]:
            density = content_lower.count(keyword.lower()) / word_count
            if density < 0.005:
                issues.append(f"Low keyword density for '{keyword}': {density:.2%}")
            elif density > 0.03:
                issues.append(f"High keyword density for '{keyword}': {density:.2%}")
        
        score = 1.0 if not issues else 0.7
        return QualityCheck(
            name="keyword_density",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _check_formatting(self, content: str) -> QualityCheck:
        """Check formatting"""
        issues = []
        
        # Check for proper line breaks
        if "\n\n" not in content and len(content) > 500:
            issues.append("Missing paragraph breaks")
        
        # Check for headers (markdown)
        if len(content) > 300 and not content.startswith("#"):
            issues.append("Missing heading")
        
        score = 1.0 if not issues else 0.8
        return QualityCheck(
            name="formatting",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _check_brand_consistency(self, content: str, brand_rules: Dict[str, Any]) -> QualityCheck:
        """Check brand consistency"""
        issues = []
        
        forbidden_terms = brand_rules.get("forbidden_terms", [])
        for term in forbidden_terms:
            if term.lower() in content.lower():
                issues.append(f"Forbidden term used: {term}")
        
        preferred_terms = brand_rules.get("preferred_terms", {})
        for term, replacement in preferred_terms.items():
            if term.lower() in content.lower():
                issues.append(f"Use preferred term: {replacement}")
        
        score = 1.0 if not issues else 0.7
        return QualityCheck(
            name="brand_consistency",
            passed=len(issues) == 0,
            score=score,
            issues=issues
        )
    
    def _generate_recommendations(self, checks: List[QualityCheck], issues: List[str]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for check in checks:
            if not check.passed:
                if check.name == "grammar":
                    recommendations.append("Review and fix grammar issues")
                elif check.name == "readability":
                    recommendations.append("Simplify sentences for better readability")
                elif check.name == "length":
                    recommendations.append("Adjust content length")
                elif check.name == "keyword_density":
                    recommendations.append("Adjust keyword usage")
        
        return recommendations


def main():
    """Test quality engine"""
    engine = ContentQualityEngine(None)
    print("Content Quality Engine initialized")


if __name__ == "__main__":
    main()
