# MAHA SALES ENGINE V1 - Localization Documentation

## Overview

Multi-language content support with 10 languages.

## Supported Languages

| Language | Code |
|----------|------|
| English | en |
| Indonesian | id |
| Chinese | zh |
| Spanish | es |
| Arabic | ar |
| Hindi | hi |
| Thai | th |
| Vietnamese | vi |
| Portuguese | pt |
| Russian | ru |

## Usage

```python
from localization.engine import LocalizationEngine

engine = LocalizationEngine(db_manager, ai_manager)

# Localize content
result = engine.localize_content(
    content_id="content-123",
    target_language="id",
    content="Original content",
    context={"product_id": "prod-123", "content_type": "description"}
)
```

## Features

- Machine translation
- Region-specific formatting
- Currency adaptation
- Cultural adaptation
- Translation versioning
- Review workflow

## Best Practices

1. Review machine translations
2. Consider cultural nuances
3. Localize keywords
4. Adapt formatting
5. Test with native speakers