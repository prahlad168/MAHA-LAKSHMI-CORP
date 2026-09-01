# MAHA Business Passport V1

A zero/near-zero-cost, self-distributing product for small businesses.

## Product promise

A business creates a public **Business Passport** containing:

- a simple digital-growth score;
- three prioritized improvement actions;
- business category and location;
- a shareable public URL;
- WhatsApp sharing.

The score is explicitly a heuristic. It is not a Google ranking, investment recommendation, certification, or guarantee of business quality.

## Growth loop

`Create Passport → receive useful result → share Passport → recipient sees value → recipient creates a Passport → new user`

The product must earn distribution because the artifact is useful. It must not require spam.

## Current V1

The static MVP is implemented in `web/index.html` and works without a backend. It supports:

1. Business input.
2. Deterministic heuristic scoring.
3. Prioritized actions.
4. Public/shareable query-string Passport URLs.
5. Copy-link and WhatsApp sharing.
6. Mobile-friendly presentation.

The MVP intentionally avoids storing personal/business data until the persistence and abuse controls are ready.

## Cloudflare deployment

The Worker is configured in `wrangler.jsonc` and serves the static site from `web/`.

For a Cloudflare Workers Git deployment, set the repository root directory to:

`maha-growth-loop`

Build command: leave empty.

Deploy command:

`npx wrangler deploy`

The Worker is `src/worker.js`.

Cloudflare currently supports Workers Static Assets and Python/FastAPI, but V1 deliberately uses a tiny JavaScript asset Worker because the product is static and does not need a Python runtime yet.

## Supabase production schema

`supabase/schema.sql` contains the planned persistence model for businesses and referrals. Public reads are enabled; public writes are intentionally disabled. Production writes should go through a server-side API or Supabase Edge Function with validation and rate limiting.

## Next production gate

Do not add payment or expensive AI analysis until the free loop is tested with real users.

Minimum validation:

- 10 real businesses complete a Passport;
- 5 publish/share it;
- 3 referred visitors arrive;
- 1 referred visitor creates a Passport;
- at least 1 user expresses willingness to pay.

## Future monetization

Potential paid layers, to be validated rather than assumed:

- deeper diagnostics;
- score history and rescans;
- monitoring/alerts;
- branded reports;
- multiple business profiles;
- premium discovery/lead tools.

Potential pricing is a hypothesis only. Revenue claims are not made until real payment evidence exists.
