# README.md - MAHA Sales Engine V1 - Product Factory

## Product Factory

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
- Mini Courses (Markdown structure)
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

## New SOP Generator Plugin

Starting with Phase 12, the Product Factory includes a **generic SOP Generator Plugin Architecture**:

### Plugin Architecture

- **Base SOP Generator**: Abstract class for all SOP generators
- **Hospital SOP Generator**: First implementation for healthcare industry
- **Plugin System**: Dynamic discovery and registration of new SOP generators

### New Components

1. **SOP Generator Plugin** (`generators/sop_generator.py`)
   - Generic base class for all SOP generators
   - Plugin discovery and registration system

2. **Hospital SOP Generator** (`generators/hospital_sop.py`)
   - First implementation for healthcare industry
   - Follows international healthcare standards (WHO, ISO 27001, HIPAA)
   - Generates comprehensive hospital SOP templates

3. **SOP Generator Architecture** (`SOP_GENERATOR.md`)
   - Detailed documentation for plugin architecture
   - Implementation guide for new industry-specific plugins

### Phase 12 Features

- **Generic Plugin Architecture**: Extensible framework for multiple industries
- **Hospital SOP Generator**: Healthcare-focused implementation
- **AI Agent Workflow**: Research → Creation → Quality Review → Packaging → Marketing
- **Automated Scheduling**: Daily product generation with configurable schedules
- **API Integration**: Automatic discovery of registered generators
- **Database Extensions**: Support for SOP-specific data

## Documentation

- [PRODUCT_FACTORY.md](PRODUCT_FACTORY.md) - Main documentation
- [PRODUCT_PACKAGE_SPEC.md](PRODUCT_PACKAGE_SPEC.md) - Package specification
- [VERSIONING_GUIDE.md](VERSIONING_GUIDE.md) - Versioning guide
- [QUALITY_ENGINE.md](QUALITY_ENGINE.md) - Quality engine guide
- [SOP_GENERATOR.md](SOP_GENERATOR.md) - SOP Generator plugin architecture

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
| SOP Generator Plugin | ✅ |
| Hospital SOP Generator | ✅ |
| Documentation | ✅ |

**Phase 12 Implementation**: Production-ready SOP generator plugin system

## Version

**Product Factory Core**: 1.0.0  
**SOP Generator Plugin**: 2.0.0 (Phase 12)  
**Created**: 2026-07-27  
**Status**: Active with new Plugin Architecture

**Note**: Enhanced with Plugin Architecture supporting multiple industries starting with Hospital SOP Generator.