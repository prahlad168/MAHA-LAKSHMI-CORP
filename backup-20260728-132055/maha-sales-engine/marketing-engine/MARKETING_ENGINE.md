# MAHA SALES ENGINE V1 - Marketing Engine Documentation

## Overview

Comprehensive documentation for the AI Marketing Engine.

## Contents

### Core Documentation
- [MARKETING_ENGINE.md](MARKETING_ENGINE.md) - Main engine documentation
- [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md) - Prompt templates and versioning
- [SEO_ENGINE.md](SEO_ENGINE.md) - SEO optimization guide
- [CONTENT_PIPELINE.md](CONTENT_PIPELINE.md) - Pipeline architecture
- [BRAND_ENGINE.md](BRAND_ENGINE.md) - Brand consistency guide
- [LOCALIZATION.md](LOCALIZATION.md) - Multi-language support
- [AB_TESTING.md](AB_TESTING.md) - A/B testing guide

## Quick Start

```python
from marketing_engine.core.engine import MarketingEngine
from pathlib import Path

engine = MarketingEngine(Path(__file__).parent.parent.parent)

# Generate marketing package
result = await engine.generate_marketing_package("ML-20260727-000001", "en")
```

## API Documentation

Start the API server:
```bash
python -m marketing_engine.api.routes
```

API docs available at: http://localhost:8003/api/docs

## Status

| Component | Status |
|-----------|--------|
| AI Provider Abstraction | ✅ |
| Prompt Library | ✅ |
| Content Pipeline | ✅ |
| SEO Engine | ✅ |
| Keyword Engine | ✅ |
| Content Quality Engine | ✅ |
| Brand Engine | ✅ |
| Localization | ✅ |
| A/B Testing | ✅ |
| Asset Generation | ✅ |
| Event Bus | ✅ |
| Job Queue | ✅ |
| REST API | ✅ |
| Tests | ✅ |
| Documentation | ✅ |