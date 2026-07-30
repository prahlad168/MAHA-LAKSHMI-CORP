# MAHA SALES ENGINE V1 - Brand Engine Documentation

## Overview

The Brand Engine centralizes brand voice, rules, and consistency checks.

## Brand Rules

- Voice (professional, casual, etc.)
- Tone (confident, friendly, etc.)
- Writing Style
- Forbidden Terms
- Preferred Terms
- Legal Requirements
- Target Audience
- Value Proposition
- Unique Selling Proposition

## Usage

```python
from brand.engine import BrandEngine

engine = BrandEngine(db_manager)

# Create brand rules
engine.create_brand_rules("MyBrand", {
    "voice": "professional",
    "tone": "confident",
    "forbidden_terms": ["cheap", "guarantee"],
    "preferred_terms": {"fast": "quick"}
})

# Validate content
result = engine.validate_content("Content here", "MyBrand")
```

## Validation

Automatically checks:
- Forbidden terms
- Preferred term usage
- Brand consistency
- Legal compliance

## Best Practices

1. Define clear brand rules
2. Review regularly
3. Update as brand evolves
4. Enforce across all content