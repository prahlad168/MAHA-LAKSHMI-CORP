# MAHA SALES ENGINE V1 - Prompt Library Documentation

## Overview

The Prompt Library manages reusable prompt templates with versioning, categories, and A/B testing support.

## Architecture

```
Prompt Library
├── Templates (Versioned)
├── Categories
├── Variables
├── A/B Variants
├── Usage Tracking
└── History
```

## Usage

```python
from prompts.library import PromptLibrary, PromptTemplateFactory

# Create prompt
prompt_id = prompt_library.create_prompt(
    name="SEO Title Generator",
    category="seo",
    content="Generate SEO title for: {product_title}",
    variables=["product_title"],
    tags=["seo", "title"]
)

# Get prompt with variables
content = prompt_library.get_prompt_content(prompt_id, {
    "product_title": "My Product"
})
```

## Built-in Templates

- SEO Title
- Product Description
- SEO Metadata
- Social Media
- Email Campaign
- Landing Page
- FAQ
- Competitor Analysis

## Versioning

Every prompt version includes:
- Version number
- Timestamp
- Author
- Changelog
- Usage count
- Success rate

## Best Practices

1. Use descriptive variable names
2. Include examples in prompts
3. Test variations
4. Track success rates
5. Version frequently