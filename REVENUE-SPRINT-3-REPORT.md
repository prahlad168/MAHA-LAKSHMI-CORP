# MAHA LAKSHMI CORP — Revenue Sprint 3

**Status:** Complete — product-generation worker foundation, config, email, and PostgreSQL rehearsal delivered

## Completed in this increment

### Product Worker Foundation
- Added migration `007_sprint_3_product_worker.sql`.
  - Defines the missing product and marketplace catalog tables required by the API.
  - Extends generation jobs with ownership, retry count, start, and completion timestamps.
  - Adds composite indexes for queue polling, worker monitoring, product dashboards, and publication lookup.
- Replaced the previously non-executable product-generation enqueue flow with validated request input and collision-safe UUID job IDs.
- Added `GET /api/products/jobs/{job_id}`. A user can query only jobs they created.
- Added `backend.products.worker`, a runnable worker that atomically claims a job, creates a draft product, persists the result, and records failures without claiming that an external AI model was called.

### Secrets and Configuration
- Added `backend/shared/config.py` with centralized `Settings` class.
  - Loads all secrets from environment variables.
  - Provides defaults for development.
  - Used by CORS, SMTP, and future services.

### Email Notifications
- Added `backend/notifications/email.py` with SMTP `EmailService`.
  - Supports plain-text and HTML emails.
  - Gracefully suppresses sending when SMTP is not configured.
  - Wired into `POST /api/auth/password-reset/request` to replace the previous TODO.

### PostgreSQL Migration Rehearsal
- Added `backend/db/models.py` with SQLAlchemy ORM models for core entities.
  - Covers users, products, jobs, marketplace tables, sales, revenue, accounting, payments, payouts, transactions, workers, and audit logs.
  - Compatible with both SQLite and PostgreSQL.
- Added `backend/db/postgres_rehearsal.py` with a safe batch data-copy script.
  - Usage: `python3 -m backend.db.postgres_rehearsal --database-url <postgres_url>`
  - Runs inside a transaction and skips conflicts.

## Validation

`python3 -m pytest backend/tests -q` → **41 passed**.

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `JWT_SECRET_KEY` | JWT signing key | No (auto-generated in dev) |
| `GUMROAD_API_KEY` | Gumroad API access token | For real publishing |
| `WEBHOOK_SECRET` | Gumroad webhook verification | For production webhooks |
| `SMTP_HOST` | SMTP server host | For email delivery |
| `SMTP_PORT` | SMTP server port | No (default `587`) |
| `SMTP_USER` | SMTP username | For email delivery |
| `SMTP_PASSWORD` | SMTP password | For email delivery |
| `SMTP_FROM` | Sender address | No (defaults to `SMTP_USER`) |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |
| `CORS_ORIGINS` | Comma-separated allowed origins | No (defaults to production + localhost) |
| `REDIS_URL` | Redis connection string | No |
| `LOG_LEVEL` | Logging verbosity | No (defaults to `INFO`) |

## Next Steps

- Provision PostgreSQL staging database and run rehearsal: `python3 -m backend.db.postgres_rehearsal --database-url <url>`
- Configure production `GUMROAD_API_KEY`, `WEBHOOK_SECRET`, and SMTP credentials in the deployment secret store.
- Switch deployment behind staging once rehearsal succeeds.
