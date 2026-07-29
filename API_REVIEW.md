# API Review - MAHA SALES ENGINE V1

**Review Date:** 2026-07-27
**Reviewer:** Chief Software Architect (Phase 8.5)
**Scope:** All API endpoints across the platform

---

## 1. Executive Summary

The MAHA SALES ENGINE V1 platform has **three separate FastAPI applications** exposing REST APIs, plus a legacy PHP-based API in MAHA-OS. The APIs lack consistent design patterns, authentication, input validation, and error handling. Many endpoints return stub data.

**Overall API Score: 35/100**

| Dimension | Score | Rating |
|-----------|-------|--------|
| Design Consistency | 40 | Poor |
| Completeness | 30 | Poor |
| Error Handling | 35 | Poor |
| Documentation | 45 | Fair |
| Versioning | 50 | Fair |
| Security | 10 | Critical |
| Testing | 20 | Poor |

---

## 2. API Inventory

### 2.1 Commerce API (port 8005)

**File:** `maha-sales-engine/commerce/api/routes.py`

| Method | Endpoint | Status | Returns |
|--------|----------|--------|---------|
| GET | `/health` | ✅ Implemented | Health status |
| GET | `/api/v1/customers` | ✅ Implemented | Customer list |
| POST | `/api/v1/customers` | ✅ Implemented | Create customer |
| GET | `/api/v1/customers/{id}` | ✅ Implemented | Get customer |
| POST | `/api/v1/orders` | ✅ Implemented | Create order |
| GET | `/api/v1/orders/{id}` | ✅ Implemented | Get order |
| PATCH | `/api/v1/orders/{id}/status` | ✅ Implemented | Update status |
| POST | `/api/v1/cart` | ✅ Implemented | Create cart |
| POST | `/api/v1/cart/{id}/items` | ✅ Implemented | Add cart item |
| POST | `/api/v1/checkout` | ✅ Implemented | Checkout |
| POST | `/api/v1/payments/authorize` | ✅ Implemented | Authorize payment |
| POST | `/api/v1/payments/verify/{id}` | ✅ Implemented | Verify payment |
| POST | `/api/v1/licenses` | ✅ Implemented | Issue license |
| POST | `/api/v1/licenses/{id}/activate` | ✅ Implemented | Activate license |
| GET | `/api/v1/licenses/validate/{key}` | ✅ Implemented | Validate license |
| POST | `/api/v1/subscriptions` | ✅ Implemented | Create subscription |
| POST | `/api/v1/subscriptions/{id}/cancel` | ✅ Implemented | Cancel subscription |
| POST | `/api/v1/deliveries` | ✅ Implemented | Create delivery |
| GET | `/api/v1/deliveries/{id}/download` | ✅ Implemented | Get download URL |
| POST | `/api/v1/invoices/generate/{order_id}` | ✅ Implemented | Generate invoice |
| POST | `/api/v1/refunds` | ✅ Implemented | Create refund |
| POST | `/api/v1/coupons/validate` | ✅ Implemented | Validate coupon |
| GET | `/api/v1/promotions/active` | ✅ Implemented | Get promotions |
| GET | `/api/v1/metrics` | ✅ Implemented | Get metrics |
| GET | `/api/v1/audit` | ✅ Implemented | Query audit log |

**Total: 24 endpoints** - All appear implemented but many have no auth.

### 2.2 Marketing Engine API (port 8003)

**File:** `maha-sales-engine/marketing-engine/api/routes.py`

| Method | Endpoint | Status | Returns |
|--------|----------|--------|---------|
| GET | `/health` | ✅ Implemented | Health status |
| POST | `/api/v1/generate` | ✅ Implemented | Queued job |
| POST | `/api/v1/generate/seo` | ✅ Implemented | SEO metadata |
| POST | `/api/v1/generate/keywords` | ✅ Implemented | Keywords |
| POST | `/api/v1/generate/faq` | ⚠️ Stub | `{"faq": [], "product_id": ...}` |
| POST | `/api/v1/generate/landing-page` | ⚠️ Stub | `{"landing_page": {}, "product_id": ...}` |
| POST | `/api/v1/generate/email` | ⚠️ Stub | `{"email": {}, "product_id": ...}` |
| POST | `/api/v1/generate/social` | ⚠️ Stub | `{"social": {}, "platform": ...}` |
| POST | `/api/v1/generate/metadata` | ⚠️ Stub | `{"metadata": {}, "product_id": ...}` |
| POST | `/api/v1/generate/blog` | ⚠️ Stub | `{"blog": {}, "product_id": ...}` |
| POST | `/api/v1/generate/release-notes` | ⚠️ Stub | `{"release_notes": {}, "product_id": ...}` |
| POST | `/api/v1/generate/persona` | ⚠️ Stub | `{"persona": {}, "product_id": ...}` |
| POST | `/api/v1/generate/competitor-analysis` | ⚠️ Stub | `{"competitors": [], "product_id": ...}` |
| GET | `/api/v1/assets` | ⚠️ Stub | `{"assets": [], "count": 0}` |
| GET | `/api/v1/assets/{id}` | ⚠️ Stub | `{"asset_id": id}` |
| POST | `/api/v1/assets/{id}/approve` | ⚠️ Stub | `{"status": "approved"}` |
| GET | `/api/v1/assets/{id}/versions` | ⚠️ Stub | `{"versions": [], "asset_id": id}` |
| POST | `/api/v1/brand` | ✅ Implemented | Create brand rules |
| GET | `/api/v1/brand/{name}` | ✅ Implemented | Get brand rules |
| POST | `/api/v1/ab-tests` | ✅ Implemented | Create A/B test |
| GET | `/api/v1/ab-tests/{id}` | ✅ Implemented | Get A/B test |
| POST | `/api/v1/localize` | ✅ Implemented | Localize content |
| GET | `/api/v1/localize/{id}` | ✅ Implemented | Get localized content |
| POST | `/api/v1/assets/generate` | ✅ Implemented | Generate asset spec |
| GET | `/api/v1/prompts` | ✅ Implemented | List prompts |
| GET | `/api/v1/jobs/{id}` | ✅ Implemented | Get job status |
| GET | `/api/v1/jobs/queue/stats` | ✅ Implemented | Queue statistics |

**Total: 28 endpoints** - 13 are stubs returning empty data.

### 2.3 Sales Automation API (port 8004)

**File:** `maha-sales-engine/sales-automation/api/routes.py`

| Method | Endpoint | Status | Returns |
|--------|----------|--------|---------|
| GET | `/health` | ✅ Implemented | Health status |
| GET | `/health/components` | ✅ Implemented | Component health |
| POST | `/api/v1/workflows` | ✅ Implemented | Create workflow |
| GET | `/api/v1/workflows` | ✅ Implemented | List workflows |
| POST | `/api/v1/workflows/{id}/execute` | ✅ Implemented | Execute workflow |
| POST | `/api/v1/publish` | ✅ Implemented | Publish product |
| POST | `/api/v1/publish/bulk` | ✅ Implemented | Bulk publish |
| POST | `/api/v1/sync/product` | ✅ Implemented | Sync product |
| POST | `/api/v1/sync/marketplace/{id}` | ✅ Implemented | Sync marketplace |
| POST | `/api/v1/approvals/{id}/approve` | ✅ Implemented | Approve request |
| GET | `/api/v1/approvals` | ⚠️ Stub | `{"approvals": [], "count": 0}` |
| POST | `/api/v1/rules` | ✅ Implemented | Create rule |
| GET | `/api/v1/rules` | ⚠️ Stub | `{"rules": [], "count": 0}` |
| POST | `/api/v1/campaigns` | ✅ Implemented | Create campaign |
| POST | `/api/v1/campaigns/{id}/start` | ✅ Implemented | Start campaign |
| GET | `/api/v1/campaigns` | ⚠️ Stub | `{"campaigns": [], "count": 0}` |
| GET | `/api/v1/queue/stats` | ✅ Implemented | Queue stats |
| POST | `/api/v1/queue/jobs` | ✅ Implemented | Enqueue job |
| GET | `/api/v1/queue/jobs/{id}` | ✅ Implemented | Get job |
| GET | `/api/v1/metrics` | ✅ Implemented | Get metrics |
| GET | `/api/v1/audit` | ✅ Implemented | Query audit |
| POST | `/api/v1/notifications` | ✅ Implemented | Send notification |
| POST | `/api/v1/webhooks/{id}` | ✅ Implemented | Receive webhook |

**Total: 23 endpoints** - 4 are stubs returning empty data.

### 2.4 App API (port 8000)

**File:** `app/main.py` + `app/api/sales.py`

| Method | Endpoint | Status | Returns |
|--------|----------|--------|---------|
| GET | `/` | ✅ Implemented | Health check |
| GET | `/health` | ✅ Implemented | Health check |
| GET | `/api/health` | ✅ Implemented | API health |
| GET | `/api/alpha/gaurangga/consolidated-status` | ✅ Implemented | Consolidated status |
| POST | `/api/alpha/gaurangga/sync` | ✅ Implemented | Unified sync |
| GET | `/api/alpha/gaurangga/sync-status` | ✅ Implemented | Sync status |
| GET | `/api/alpha/gaurangga/nodes` | ✅ Implemented | Node status |
| GET | `/api/sales/products` | ✅ Implemented | List products |
| GET | `/api/sales/products/{id}` | ✅ Implemented | Get product |
| POST | `/api/sales/orders` | ✅ Implemented | Create order |
| GET | `/api/sales/orders` | ✅ Implemented | List orders |
| GET | `/api/sales/orders/{id}` | ✅ Implemented | Get order |
| POST | `/api/sales/orders/{id}/verify` | ✅ Implemented | Verify payment |
| GET | `/api/sales/reports/daily` | ✅ Implemented | Daily report |
| GET | `/api/sales/reports/transactions` | ✅ Implemented | Transaction history |
| GET | `/api/sales/reports/summary` | ✅ Implemented | Revenue summary |
| GET | `/api/sales/customers` | ✅ Implemented | List customers |

**Total: 17 endpoints** - All appear implemented.

---

## 3. API Design Consistency Issues

### 3.1 Inconsistent URL Patterns

| Issue | Examples |
|-------|----------|
| Mixed path styles | `/api/v1/customers` vs `/api/sales/products` vs `/api/v1/generate/seo` |
| Inconsistent versioning | Some use `/api/v1/`, others use `/api/sales/` |
| Inconsistent nesting | `/api/v1/generate/seo` (nested) vs `/api/v1/customers` (flat) |
| Inconsistent resource naming | `customers` (plural) vs `customer` (singular in path params) |

### 3.2 Inconsistent Error Responses

Different endpoints use different error response formats:

```python
# commerce/api/routes.py
raise HTTPException(status_code=404, detail="Customer not found")

# marketing-engine/api/routes.py
raise HTTPException(status_code=500, detail=str(e))

# sales-automation/api/routes.py
return {"error": "Invalid report type"}  # Not an HTTPException!
```

### 3.3 Inconsistent Response Formats

Some endpoints return `{"data": ...}`, others return the raw object, others return `{"status": "created", "customer_id": ...}`.

### 3.4 Missing Response Models

Many endpoints lack Pydantic response models, making it impossible to validate response shapes.

---

## 4. Error Handling Analysis

### 4.1 Error Handling Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| HTTPException | Common | `raise HTTPException(status_code=404, detail="...")` |
| Try/except with HTTPException | Common | Catch + re-raise as HTTPException |
| Return error dict (not HTTPException) | Rare | `return {"error": "Invalid report type"}` |
| Silent exception swallowing | Present | Some endpoints catch and return empty data |

### 4.2 Missing Error Handling

1. **No global exception handler** - Each endpoint handles errors individually
2. **No validation error handling** - Pydantic validation errors return default FastAPI responses
3. **No 422 response model** - Validation errors are not documented
4. **No 500 response model** - Server errors are not documented

---

## 5. API Versioning

### Current State

All APIs use `/api/v1/` prefix, but:
- The `app/` API uses `/api/sales/` (no version prefix)
- The `app/` API uses `/api/alpha/gaurangga/` (no version prefix)
- No deprecation strategy is documented
- No backward compatibility guarantees

**Violation of GLOBAL_EXECUTION_POLICY.md Section 5.7:**
> "Version all APIs (v1, v2)"
> "Backward compatibility required"
> "Deprecation notices: minimum 30 days"

---

## 6. API Testing

### Test Coverage

| API | Test File | Coverage |
|-----|-----------|----------|
| App API (`app/`) | `tests/test_sales_api.py` | 7 tests covering main endpoints |
| App Health | `tests/test_app_health.py` | 6 tests for health endpoints |
| Commerce API | None | 0% |
| Marketing API | None | 0% |
| Sales Automation API | None | 0% |

**Overall API test coverage: ~10%** (only the `app/` API has tests)

---

## 7. API Documentation

### OpenAPI/Swagger

All three FastAPI apps have `docs_url="/api/docs"` and `redoc_url="/api/redoc"` enabled, providing auto-generated API documentation.

**Issue:** These are enabled in production, which exposes internal API structure to the public.

### Missing Documentation

- No API versioning strategy documented
- No rate limiting documentation
- No authentication documentation
- No error code documentation
- No example request/response payloads for most endpoints

---

## 8. API Security Issues

| Issue | Severity | Location |
|-------|----------|----------|
| No authentication | Critical | All API endpoints |
| No rate limiting | Critical | All API endpoints |
| CORS overly permissive | High | `app/main.py` |
| No input validation | High | All endpoints |
| No HTTPS enforcement | High | All endpoints |
| API docs exposed in production | Medium | All FastAPI apps |
| No request size limits | Medium | All FastAPI apps |
| No response caching headers | Low | All endpoints |

---

## 9. Recommendations

1. **Consolidate into a single FastAPI app** with blueprints for each domain
2. **Add a consistent error response model** across all endpoints
3. **Add authentication middleware** (JWT or API key)
4. **Add rate limiting** middleware
5. **Add input validation** using Pydantic validators
6. **Disable API docs in production** or protect them with authentication
7. **Add OpenAPI security schemes** to the documentation
8. **Add API versioning** with a consistent prefix pattern
9. **Add response caching headers** for read-only endpoints
10. **Add request size limits** to prevent memory exhaustion
11. **Add comprehensive API tests** for all endpoints
12. **Add API documentation** for versioning, deprecation, and error codes

---

*End of API Review*