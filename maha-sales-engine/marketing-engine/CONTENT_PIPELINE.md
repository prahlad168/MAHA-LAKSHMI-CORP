# MAHA SALES ENGINE V1 - Content Pipeline Documentation

## Overview

The Content Pipeline manages the end-to-end content generation process.

## Pipeline Stages

1. **Research** - Gather product information
2. **Keyword Discovery** - Find relevant keywords
3. **Audience Analysis** - Understand target audience
4. **Competitor Analysis** - Analyze competitors
5. **Content Planning** - Plan content structure
6. **Generation** - Generate content using AI
7. **Quality Review** - Validate content quality
8. **SEO Optimization** - Optimize for search
9. **Compliance Review** - Check brand compliance

## State Machine

Valid transitions:
- Draft → Researching/Generating
- Researching → Generating/Draft/Failed
- Generating → Reviewing/Failed
- Reviewing → Optimizing/Approved/Rejected/Draft/Failed
- Optimizing → Approved/Rejected/Failed
- Approved → Archived
- Rejected → Draft/Generating
- Failed → Draft/Generating

## Usage

```python
from pipeline.state_machine import ContentPipeline

result = await pipeline.generate_marketing_content(
    product_id="ML-20260727-000001",
    content_types=["seo_title", "product_description", "landing_page"],
    locale="en"
)
```

## Monitoring

Track pipeline metrics:
- Generation time per stage
- Success rate
- Quality scores
- Retry count