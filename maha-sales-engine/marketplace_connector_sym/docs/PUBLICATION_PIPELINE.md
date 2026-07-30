# MAHA SALES ENGINE V1 - Publication Pipeline

Automated product publication pipeline from AI Product Factory to Gumroad.

## Pipeline Stages

1. **LOAD** - Load product package from storage
2. **VALIDATE_STRUCTURE** - Verify package structure
3. **VALIDATE_FILES** - Check required files exist
4. **VALIDATE_METADATA** - Validate metadata completeness
5. **BUILD_PAYLOAD** - Build provider-specific payload
6. **UPLOAD_PRODUCT** - Upload product ZIP file
7. **UPLOAD_THUMBNAIL** - Upload thumbnail image
8. **UPLOAD_PREVIEW** - Upload preview assets (optional)
9. **CREATE_LISTING** - Create marketplace product listing
10. **APPLY_DESCRIPTION** - Apply product description
11. **APPLY_PRICING** - Apply pricing configuration
12. **APPLY_TAGS** - Apply product tags
13. **PUBLISH** - Publish listing
14. **STORE_IDS** - Save marketplace identifiers
15. **GENERATE_REPORT** - Generate publication report
16. **NOTIFY** - Notify downstream systems

## Usage

```python
from marketplace_connector.publication.publication_pipeline import PublicationPipeline

pipeline = PublicationPipeline(provider, validation_engine, db_manager)

result = await pipeline.execute("/path/to/product", {
    "product_id": "prod-001",
    "provider": "gumroad",
    "title": "Digital Product",
    "description": "Product description",
    "price": 29.99,
    "currency": "USD",
    "tags": ["digital"]
})
```

## Error Handling

If any stage fails:
- Pipeline stops immediately
- Error is recorded in publication context
- Publication status is set to FAILED
- Retry engine may enqueue for retry
- Audit log captures failure details

## Monitoring

Each stage execution is logged with:
- Timestamp
- Stage name
- Success/failure status
- Error details (if failed)
- Execution duration
