# MAHA SALES ENGINE V1 - Versioning Guide

## Overview

The Product Factory versioning system provides complete version control with rollback support for all digital products.

## Version Numbering

We use Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

Format: `MAJOR.MINOR.PATCH`

Examples:
- `1.0.0` - Initial release
- `1.1.0` - Added new chapter
- `1.1.1` - Fixed typo
- `2.0.0` - Major rewrite

## Version Creation

Every significant change creates a new version:

```python
version_id = version_manager.create_version(
    product_id,
    product_dir,
    changelog="Added new chapter on AI marketing"
)
```

### What Gets Versioned
- All files in product/, preview/, thumbnail/
- metadata.json
- description.md
- license.txt
- keywords.json
- pricing.json
- version.json
- history.json

### What Does NOT Get Versioned
- quality_report.json (regenerated each time)
- versions/ directory (circular)
- backup/ directory

## Version Storage

```
{PRODUCT_ID}/
├── versions/
│   └── VER-{PRODUCT_ID}-{TIMESTAMP}/
│       ├── [versioned files]
│       └── version_metadata.json
└── backup/
    └── {TIMESTAMP}/
        └── [backup files]
```

## Version Metadata

```json
{
  "version_id": "VER-ML-20260727-000001-20260727120000",
  "product_id": "ML-20260727-000001",
  "version_number": "1.1.0",
  "created_at": "2026-07-27T12:00:00",
  "created_by": "system",
  "changelog": "Added new chapter on AI marketing",
  "file_path": "/path/to/version",
  "file_hash": "sha256hash",
  "file_size": 15360
}
```

## Rollback Process

### When to Rollback
- Quality check failure after deployment
- Critical bug discovered
- Customer complaint about content
- Legal issue with content

### Rollback Steps
1. Create backup of current version
2. Copy files from target version
3. Update version.json
4. Update history.json
5. Log rollback action
6. Notify stakeholders

### Rollback Code
```python
success = version_manager.rollback_version(
    product_id,
    target_version_id
)
```

## Version History Query

```python
versions = version_manager.get_version_history(product_id)
# Returns list of versions sorted by date (newest first)
```

## Best Practices

1. **Create versions frequently**: After every significant change
2. **Write clear changelogs**: Future you will thank you
3. **Test before versioning**: Don't version broken products
4. **Keep versions**: Don't delete old versions
5. **Use rollback sparingly**: Fix forward when possible
6. **Tag releases**: Use version.json to mark stable releases

## Database Schema

### pf_product_versions

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Primary key (version_id) |
| product_id | TEXT | Foreign key to products |
| version_number | TEXT | Semantic version |
| created_at | TEXT | ISO timestamp |
| created_by | TEXT | Creator identifier |
| changelog | TEXT | Change description |
| file_path | TEXT | Version directory path |
| file_hash | TEXT | SHA256 hash of all files |
| file_size | INTEGER | Total size in bytes |
| metadata | TEXT | JSON metadata |

## Troubleshooting

### Version creation fails
- Check disk space
- Check file permissions
- Check product directory exists

### Rollback fails
- Check version directory exists
- Check product directory is writable
- Check backup directory is writable

### Version history empty
- Check database connection
- Check product_id is correct
- Check versions exist in filesystem