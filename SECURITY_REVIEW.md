# Security Review - MAHA SALES ENGINE V1

**Review Date:** 2026-07-27
**Reviewer:** Chief Software Architect (Phase 8.5)
**Scope:** Full platform security assessment

---

## 1. Executive Summary

The MAHA SALES ENGINE V1 platform has **significant security gaps** that would prevent it from passing even a basic security audit. The most critical issues are the complete absence of authentication/authorization on all API endpoints, hardcoded placeholder credentials in configuration files, and no input validation on any API endpoint.

**Overall Security Score: 28/100**

| Dimension | Score | Rating |
|-----------|-------|--------|
| Authentication | 10 | Critical |
| Authorization | 10 | Critical |
| Input Validation | 15 | Critical |
| Secret Management | 20 | Critical |
| Encryption | 35 | Poor |
| Audit Logging | 40 | Fair |
| Dependency Security | 50 | Fair |
| Configuration Security | 25 | Critical |

---

## 2. Authentication & Authorization

### Critical Finding: No Authentication on Any API Endpoint

All three FastAPI applications (`commerce/api/routes.py`, `marketing-engine/api/routes.py`, `sales-automation/api/routes.py`) expose **all endpoints publicly** with no authentication middleware, no JWT validation, no API key checking, and no mTLS enforcement.

**Evidence:**
- `commerce/api/routes.py:85-87` - `/health` endpoint with no auth
- `commerce/api/routes.py:92-99` - `POST /api/v1/customers` with no auth
- `commerce/api/routes.py:112-119` - `POST /api/v1/orders` with no auth
- `marketing-engine/api/routes.py:91-97` - `/health` endpoint with no auth
- `sales-automation/api/routes.py:80-82` - `/health` endpoint with no auth

**Violation of GLOBAL_EXECUTION_POLICY.md Section 8.2:**
> "All external APIs require authentication"
> "JWT tokens with short expiry (24h max)"
> "API keys with least privilege"
> "Multi-factor authentication for admin access"

### No Authorization Model

There is no RBAC (Role-Based Access Control) implementation. The `MAHA-OS/` directory has a `roles/Role.php` and `auth/Auth.php` but these are PHP-based and not integrated with the Python FastAPI apps.

**Evidence:**
- `MAHA-OS/auth/Auth.php` - PHP auth class, not used by Python apps
- `MAHA-OS/roles/Role.php` - PHP role class, not used by Python apps
- `MAHA-OS/database/005-roles.sql` - SQL schema for roles, not used by Python apps

---

## 3. Input Validation

### Critical Finding: No Input Validation on API Endpoints

FastAPI endpoints accept raw request bodies without validation beyond Pydantic model type checking. There is no:
- Input sanitization
- SQL injection prevention (beyond parameterized queries in some places)
- File upload validation
- Rate limiting
- Request size limits
- Content-type validation

**Evidence:**
- `commerce/api/routes.py:92-99` - `create_customer()` accepts any `CustomerCreate` model without additional validation
- `commerce/api/routes.py:112-119` - `create_order()` accepts any `OrderCreate` model without validation
- `sales-automation/api/routes.py:250-254` - `send_notification()` accepts raw strings without sanitization
- `sales-automation/api/routes.py:259-262` - `receive_webhook()` accepts any payload without signature verification

### SQL Injection Risk

While most database queries use parameterized queries (`cursor.execute("...", (params,))`), there are exceptions:

**Evidence:**
- `commerce/api/routes.py:98-107` - Uses parameterized queries ✅
- `analytics/engine.py:56-58` - Uses parameterized queries ✅
- `product-factory/core/factory.py:291-312` - Uses parameterized queries ✅

However, the `webhooks/gateway.py` endpoint at `sales-automation/api/routes.py:259-262` does not verify webhook signatures, making it vulnerable to forged requests.

---

## 4. Secret Management

### Critical Finding: Placeholder Credentials in Configuration

The `config/engine.yaml` file contains placeholder credentials that are either empty strings or clearly fake values:

```yaml
security:
  api_key: ""
  encryption_key: ""
  cert_path: ""
  key_path: ""
  ca_path: ""
```

```yaml
channels:
  email:
    username: "your-email@gmail.com"
    password: "your-app-password"
  whatsapp:
    token: ""
  linkedin:
    token: ""
```

```yaml
marketplaces:
  gumroad:
    api_key: ""
  shopify:
    api_key: ""
```

**Violation of GLOBAL_EXECUTION_POLICY.md Section 8.1:**
> "Never commit secrets to version control"
> "Use environment variables for secrets"
> "Use encrypted configuration for sensitive data"

### Secrets in Version Control

The `.env.example` file exists but there is no `.env` file in the repository. However, the `engine.yaml` file is committed to the repository with placeholder credentials, which could be accidentally replaced with real credentials.

**Evidence:**
- `.env.example` exists in root directory
- `config/engine.yaml` is committed with placeholder values
- No `.env` file in git (good)
- No secret scanning in CI/CD

---

## 5. Encryption

### HTTPS Enforcement

The `GLOBAL_EXECUTION_POLICY.md` Section 8.3 requires:
> "HTTPS only - no HTTP"
> "TLS 1.3 minimum"
> "Encrypt sensitive data at rest"

**Current Status:**
- The `PerformanceReporter` at `reporter/reporter.py:58-65` has HTTPS code **commented out**
- No TLS configuration is present in `engine.yaml`
- No certificate paths are configured
- The FastAPI apps run without TLS by default

**Evidence:**
- `maha-sales-engine/reporter/reporter.py:59-65` - HTTPS request code is commented out
- `maha-sales-engine/config/engine.yaml:56-61` - Security fields are empty strings
- `app/main.py:44-59` - CORS allows `http://localhost:*` origins

### Data at Rest

- SQLite database is unencrypted
- No encryption at rest for the database file
- No encryption for log files that may contain sensitive data

**Evidence:** `maha-sales-engine/db/schema.sql` - No encryption directives

### Data in Transit

- No TLS configured for any API endpoint
- No mTLS for node-to-dashboard communication
- The `PerformanceReporter` has mTLS code commented out

---

## 6. Audit Logging

### Partial Audit Implementation

The `commerce/` module has an `audit/engine.py` and `commerce_audit_log` table in the database schema. However, it is unclear if this is actually used by the API endpoints.

**Evidence:**
- `commerce/db/schema.sql:367-379` - `commerce_audit_log` table exists
- `commerce/api/routes.py:294-297` - `/api/v1/audit` endpoint exists
- But no audit logging is called from `create_customer()`, `create_order()`, etc.

### Missing Audit for Critical Operations

The following operations have **no audit trail**:
1. Order creation
2. Payment processing
3. Customer data modification
4. Product status changes
5. Marketplace listing changes
6. API key usage

---

## 7. Dependency Security

### Known Vulnerabilities

The `requirements.txt` has loose version pins (`>=`) which means dependency versions are not pinned. This could lead to:
- Supply chain attacks via compromised dependencies
- Inconsistent builds across environments
- Unpredictable security patch levels

**Evidence:** `maha-sales-engine/requirements.txt:5-31` - All deps use `>=` pinning

### Unused Dependencies

The following dependencies are listed but their usage is unclear or unused:
- `openai>=1.0` - Listed as optional, not imported in any core file
- `anthropic>=0.7` - Listed as optional, not imported in any core file
- `gumroad-api>=0.1` - Listed as optional, not imported
- `shopify_python_api>=5.0` - Listed as optional, not imported
- `etsy-api>=0.1` - Listed as optional, not imported

---

## 8. Configuration Security

### CORS Misconfiguration

The `app/main.py` CORS middleware allows all origins, methods, and headers:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mahalaksmi.web.id",
        "https://www.mahalaksmi.web.id",
        "https://admin.mahalaksmi.web.id",
        "https://bayar.mahalaksmi.web.id",
        "https://gaurangga.mahalaksmi.web.id",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue:** `allow_methods=["*"]` and `allow_headers=["*"]` are overly permissive. The `allow_credentials=True` combined with wildcard origins (though not wildcard here) is a security risk.

### Debug Mode

The `engine.yaml` has `debug: false` in the engine config, but the FastAPI apps have `docs_url="/api/docs"` and `redoc_url="/api/redoc"` enabled, which exposes API documentation in production.

**Evidence:**
- `commerce/api/routes.py:37-38` - `docs_url="/api/docs"`, `redoc_url="/api/redoc"`
- `marketing-engine/api/routes.py:34-35` - Same
- `sales-automation/api/routes.py:29-30` - Same

---

## 9. Security Findings Summary

### Critical (Must Fix Before Production)

| # | Finding | Location | Impact |
|---|---------|----------|--------|
| C1 | No authentication on any API endpoint | All `api/routes.py` files | Unauthorized access to all data |
| C2 | No input validation/sanitization | All API endpoints | Injection attacks |
| C3 | Placeholder credentials in config | `config/engine.yaml` | Credential exposure |
| C4 | HTTPS code commented out | `reporter/reporter.py:59-65` | Data in transit unprotected |
| C5 | No webhook signature verification | `sales-automation/api/routes.py:259-262` | Forged webhook requests |
| C6 | CORS allows all methods and headers | `app/main.py:44-59` | Cross-site request forgery |

### High (Should Fix)

| # | Finding | Location | Impact |
|---|---------|----------|--------|
| H1 | No rate limiting on API endpoints | All `api/routes.py` files | DoS attacks |
| H2 | No RBAC implementation | Entire platform | Unauthorized data access |
| H3 | No encryption at rest | SQLite database | Data exposure if file stolen |
| H4 | No audit logging for critical operations | All API endpoints | No accountability |
| H5 | FastAPI docs enabled in production | All `api/routes.py` files | Information disclosure |
| H6 | Loose dependency version pinning | `requirements.txt` | Supply chain risk |

### Medium

| # | Finding | Location | Impact |
|---|---------|----------|--------|
| M1 | No database connection timeout | `core/engine.py:177-182` | Connection exhaustion |
| M2 | No request size limits | All FastAPI apps | Memory exhaustion |
| M3 | No security headers on HTTP responses | All FastAPI apps | XSS/CSRF |
| M4 | No secret scanning in CI/CD | No CI/CD pipeline | Accidental secret commits |

---

## 10. Recommendations

1. **Implement JWT authentication** on all API endpoints per GLOBAL_EXECUTION_POLICY.md Section 8.2
2. **Add input validation** using Pydantic validators and sanitization
3. **Move all secrets to environment variables** and remove from `engine.yaml`
4. **Enable HTTPS** with proper TLS certificates
5. **Add webhook signature verification** to the webhook gateway
6. **Restrict CORS** to specific origins, methods, and headers
7. **Disable FastAPI docs** in production (remove `docs_url` and `redoc_url`)
8. **Implement rate limiting** on all API endpoints
9. **Add audit logging** to all critical operations
10. **Enable encryption at rest** for the SQLite database
11. **Pin all dependencies** with exact versions in `requirements.txt`
12. **Add security headers** (CSP, HSTS, X-Content-Type-Options) to all responses
13. **Implement RBAC** using the existing `MAHA-OS/roles/Role.php` as a reference
14. **Add secret scanning** to the CI/CD pipeline

---

*End of Security Review*