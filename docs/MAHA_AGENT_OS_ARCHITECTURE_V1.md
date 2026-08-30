# MAHA Agent OS Architecture V1

Status: Implementation blueprint
Date: 2026-08-30

## Objective

Turn the existing MAHA Sales Engine into a reliable agent runtime without rewriting the business modules that already exist.

Core loop:

```text
User Request
  -> Task
  -> Director
  -> Agent / Skill
  -> Structured Action
  -> Validator
  -> Executor
  -> Result
  -> Event Log
  -> Director
```

## Components

- **Task Runtime**: persistent task state and lifecycle.
- **Director**: chooses the next agent/skill/action; it does not execute business operations directly.
- **Agent Registry**: role-based agents loaded dynamically.
- **Skill Registry**: versioned operating procedures.
- **Action Registry**: typed actions with validation and controlled execution.
- **Event Log**: append-only audit trail for task progress.
- **Model Router**: provider-neutral interface; model selection depends on task complexity.
- **Knowledge Hub**: retrieves only relevant material instead of injecting large files into model context.

## First vertical slice

The first implementation is intentionally small:

```text
research request
  -> task creation
  -> director dispatch
  -> research/lead-generation skill
  -> structured result
  -> persisted task/event history
  -> report
```

Only after this is reliable should sales outreach, payment, delivery, and other high-impact actions be automated.

## Existing modules to preserve

- `maha-sales-engine/business/`
- `maha-sales-engine/commerce/`
- `maha-sales-engine/content/`
- `maha-sales-engine/analytics/`
- `maha-sales-engine/core/`

These become domain capabilities behind the agent/action boundary.

## Governance

LLMs are decision-makers, not unrestricted executors. High-impact operations require explicit action policies, schema validation, authorization, rate limits, and audit events.

## OpenMAIC patterns adopted

- director/state-machine orchestration
- role-based agents
- structured actions
- durable sessions/tasks
- skills
- provider abstraction
- event history

OpenMAIC classroom-specific components are intentionally not adopted.

## Target

```text
                     MAHA OS
                        |
                    Director
                        |
              +---------+---------+
              |         |         |
            Sales    Research   Content
            Agent      Agent      Agent
              |         |         |
              +---------+---------+
                        |
                  Skills / Tools
                        |
                   Action Engine
                        |
              +---------+---------+
              |         |         |
             CRM      Orders    Content
                        |
                      Revenue
```
