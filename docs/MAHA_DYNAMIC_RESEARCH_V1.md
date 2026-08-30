# MAHA Dynamic Research V1

## Runtime

`maha-sales-engine/run_dynamic_bali_research.py` now performs live public-web discovery instead of reading the curated Bali seed list.

```bash
cd maha-sales-engine
python run_dynamic_bali_research.py --limit 10
```

Limits are 1-50 businesses per run.

## Pipeline

```text
Public web search
  -> result enrichment (website/email/phone where publicly exposed)
  -> normalize + deduplicate
  -> transparent qualification
  -> durable CRM
  -> ContentEngine WhatsApp draft
  -> approval queue
```

## CRM lifecycle

Business status:

`new -> researched -> qualified/nurture -> contacted -> replied -> interested -> proposal -> won/lost`

Follow-up state:

`not_started -> awaiting_approval -> scheduled -> sent -> replied/completed/stopped`

## Safety

Research data is treated as unverified until rechecked. No WhatsApp message is sent by the research command. Messages are placed into `sales_approvals` and require an explicit approval before a future sender adapter may execute them.

## Providers

The research layer is provider-based. V1 ships with a public DuckDuckGo HTML adapter. A future provider can implement the same `search(query, limit, enrich)` contract without changing the Agent Runtime.

## Verification

The repository currently has no reported CI status for the latest commit. The local execution environment used for this session could not reliably execute outbound GitHub/web requests, so live end-to-end execution from this environment is not claimed.
