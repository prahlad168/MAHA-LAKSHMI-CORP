# MAHA Staging Verification

## Purpose

Staging is a safe environment for validating the MAHA Agent Runtime and research/CRM pipeline before production side effects are enabled.

## Required GitHub Actions secrets

- `STAGING_HEALTH_URL`: public HTTPS URL for the staging `/health` endpoint.
- `PRODUCTION_HEALTH_URL`: public HTTPS URL for the production `/health` endpoint.

## Verification chain

```text
CI
  -> unit tests
  -> integration tests
  -> restart/resume test
  -> research/enrichment smoke test
  -> dependency audit
  -> staging health
  -> production health
```

The WhatsApp sender remains disabled for smoke verification. A message must pass the human approval gate before any external send adapter may be invoked.
