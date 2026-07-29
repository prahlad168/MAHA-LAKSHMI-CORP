# MAHA SALES ENGINE V1 - Product Factory

## Overview

The AI Product Factory is an autonomous digital product generation pipeline that creates sell-ready digital products without manual intervention.

## Supported Product Types

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

## Architecture

```
Product Factory
├── Core (Factory, Models, Status)
├── Generators (Product type generators)
├── Quality Engine (Automated QA)
├── Versioning (Version control with rollback)
├── Packaging (ZIP, Folder, Manifest)
├── Licenses (License management)
├── Reports (Daily/Weekly reports)
├── API (REST endpoints)
└── Templates (Product templates)
```

## Product Lifecycle

```
Idea → Generating → Review → Approved → Packaged → Archived
```

## Quick Start

```python
from product_factory.core.main import ProductFactoryMain
from pathlib import Path

# Initialize
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

# Generate product
result = factory.generate_product(product_id, "ebook")

# Package product
package = factory.package_product(product_id, "zip")
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/products | Create product |
| GET | /api/v1/products | List products |
| GET | /api/v1/products/{id} | Get product |
| PATCH | /api/v1/products/{id}/status | Update status |
| POST | /api/v1/products/generate | Generate product |
| POST | /api/v1/products/{id}/quality-check | Quality check |
| POST | /api/v1/products/{id}/package | Package product |
| GET | /api/v1/products/{id}/versions | Version history |
| POST | /api/v1/products/{id}/rollback | Rollback version |
| GET | /api/v1/generators | List generators |
| GET | /api/v1/categories | List categories |
| GET | /api/v1/stats | Factory stats |

## Database Schema

### pf_products
- id (PK)
- title, description, category
- status, license_type
- price_usd, price_idr
- author, tags, target_market, language
- file_path, preview_path, thumbnail_path
- version_count, download_count, rating, review_count
- created_at, updated_at, archived_at

### pf_product_versions
- id (PK)
- product_id (FK)
- version_number
- created_at, created_by, changelog
- file_path, file_hash, file_size
- metadata

### pf_product_categories
- id (PK)
- name, description, icon
- created_at

### pf_product_keywords
- id (PK)
- product_id (FK)
- keyword, language
- search_volume, competition
- created_at

### pf_licenses
- id (PK)
- product_id (FK)
- license_type, terms, restrictions
- created_at

### pf_quality_reports
- id (PK)
- product_id (FK), version_id (FK)
- created_at, overall_score
- checks, passed, issues

### pf_generation_jobs
- id (PK)
- product_id (FK)
- status, created_at, started_at, completed_at
- generator_type, parameters
- result_path, error_message, logs

## Product Package Structure

```
ML-20260727-000001/
├── metadata.json
├── description.md
├── license.txt
├── keywords.json
├── pricing.json
├── version.json
├── history.json
├── quality_report.json
├── product/
│   └── [product content files]
├── preview/
│   └── [preview assets]
└── thumbnail/
    └── [thumbnail images]
```

## Quality Checks

The Quality Engine automatically verifies:
- Missing required files
- Broken internal references
- Metadata completeness
- Minimum content size (1KB)
- File naming standards
- Folder structure compliance
- File integrity (JSON validation)
- License file presence
- Description file presence
- Preview assets existence

Minimum quality score: 80% to pass.

## Versioning

Every update creates:
- Version number (semantic: major.minor.patch)
- Timestamp
- Change log
- Rollback support

## License Support

- Personal: Personal use only
- Commercial: Client work and commercial projects
- Extended: Resale and redistribution rights
- Custom: Custom terms

## Testing

Run tests:
```bash
python -m pytest maha-sales-engine/product-factory/tests/
```

## Next Steps

- Phase 4: Marketplace Integration
- Phase 5: Product Analytics
- Phase 6: Automated Marketing