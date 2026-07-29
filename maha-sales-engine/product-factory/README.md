# Product Factory

AI-powered autonomous digital product generation pipeline for MAHA Sales Engine V1.

## Purpose

Generates sell-ready digital products automatically. Does NOT publish products - responsibility ends when a sell-ready product package has been created.

## Supported Products

- eBooks (PDF)
- Prompt Packs
- AI System Prompts
- Checklists
- Templates
- Business Documents
- SOP Packages
- Notion Templates
- Excel Templates
- Canva Asset Packages
- SVG/Icon Packs
- Social Media Content Packs
- Printable Products
- Mini Courses (Markdown)
- Source Code Templates
- Documentation Packs

## Quick Start

```python
from product_factory.core.main import ProductFactoryMain
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
factory = ProductFactoryMain(base_dir)

# Create product
product_id = factory.create_product(
    title="My eBook",
    category="ebook",
    description="A great eBook",
    price_usd=19.0,
    price_idr=285000
)

# Generate
result = factory.generate_product(product_id, "ebook")

# Package
package = factory.package_product(product_id, "zip")
```

## Documentation

- [PRODUCT_FACTORY.md](PRODUCT_FACTORY.md) - Main documentation
- [PRODUCT_PACKAGE_SPEC.md](PRODUCT_PACKAGE_SPEC.md) - Package specification
- [VERSIONING_GUIDE.md](VERSIONING_GUIDE.md) - Versioning guide
- [QUALITY_ENGINE.md](QUALITY_ENGINE.md) - Quality engine guide

## API

Start API server:
```bash
python -m product_factory.api.routes
```

API docs: http://localhost:8001/api/docs

## Status

| Component | Status |
|-----------|--------|
| Core Factory | ✅ |
| Generators | ✅ |
| Quality Engine | ✅ |
| Versioning | ✅ |
| Packaging | ✅ |
| Licenses | ✅ |
| Reports | ✅ |
| API | ✅ |
| Tests | ✅ |
| Documentation | ✅ |
