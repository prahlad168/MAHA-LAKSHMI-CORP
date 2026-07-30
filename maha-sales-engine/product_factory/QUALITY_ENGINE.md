# MAHA SALES ENGINE V1 - Quality Engine Guide

## Overview

The Quality Engine automatically verifies every generated product meets minimum quality standards before it can be sold.

## Quality Checks

### 1. Missing Files
**Description**: Check for missing required files

**Required files**:
- metadata.json
- description.md
- license.txt
- version.json
- history.json

**Pass criteria**: All files present

### 2. Broken References
**Description**: Check for broken internal references

**Checks**:
- metadata.json file_path exists
- metadata.json preview_path exists
- metadata.json thumbnail_path exists

**Pass criteria**: All referenced paths exist

### 3. Metadata Completeness
**Description**: Check metadata completeness

**Required fields**:
- product_id
- title
- description
- category
- version
- author
- license

**Pass criteria**: All fields present and non-empty

### 4. Minimum Content Size
**Description**: Check minimum content size

**Minimum**: 1KB (1024 bytes) total in product/

**Pass criteria**: Total size >= 1KB

### 5. Naming Standards
**Description**: Check file naming standards

**Rules**:
- No spaces in filenames (except where required)
- Use snake_case
- Descriptive names

**Pass criteria**: No violations

### 6. Folder Structure
**Description**: Check folder structure compliance

**Required directories**:
- product/
- preview/
- thumbnail/

**Pass criteria**: All directories exist

### 7. File Integrity
**Description**: Check file integrity

**Checks**:
- All JSON files are valid JSON
- No corrupt files

**Pass criteria**: All JSON files valid

### 8. License Presence
**Description**: Check license file exists

**Pass criteria**: license.txt exists

### 9. Description Presence
**Description**: Check description file exists

**Pass criteria**: description.md exists

### 10. Preview Assets
**Description**: Check preview assets exist

**Pass criteria**: preview/ and thumbnail/ have content

## Quality Score Calculation

Each check has a weight:
- Critical checks (missing files, metadata, folder structure): 100% weight
- Important checks (license, description, content size): 100% weight
- Standard checks (naming, references, integrity): 100% weight
- Enhancement checks (preview assets): 100% weight

**Overall Score** = Average of all check scores

**Pass threshold**: >= 80% overall score AND no critical issues

## Quality Report

```json
{
  "product_id": "ML-20260727-000001",
  "overall_score": 0.9,
  "passed": true,
  "checks": [
    {
      "name": "missing_files",
      "description": "Check for missing required files",
      "passed": true,
      "score": 1.0,
      "issues": []
    }
  ],
  "issues": [],
  "recommendation": "APPROVED",
  "created_at": "2026-07-27T00:00:00"
}
```

## Recommendations

- **APPROVED**: Quality score >= 80%, no issues
- **NEEDS_REVIEW**: Quality score 50-79%, or minor issues
- **REJECTED**: Quality score < 50%, or critical issues

## Integration with Product Lifecycle

```
Generate → Quality Check → Review → Approved → Packaged
              ↓
         FAILS?
              ↓
         Regenerate
```

## Running Quality Checks

### Automatic (during generation)
```python
quality_report = quality_engine.run_quality_check(product_id)
```

### Manual
```python
quality_report = quality_engine.run_quality_check(product_id)
```

## Improving Quality

### Common Issues

1. **Missing files**: Ensure all required files are created
2. **Invalid JSON**: Validate JSON syntax
3. **Missing metadata**: Include all required fields
4. **Small content**: Add more content to reach 1KB
5. **Missing previews**: Add preview and thumbnail assets

### Quality Gates

Products cannot proceed to "Approved" status without passing quality check.

## Monitoring

Track quality metrics:
- Average quality score
- Pass/fail rate
- Common failure reasons
- Quality by generator type

Use this data to improve generators.