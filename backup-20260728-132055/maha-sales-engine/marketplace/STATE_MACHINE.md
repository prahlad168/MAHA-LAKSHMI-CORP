# MAHA SALES ENGINE V1 - State Machine Documentation

## Overview

The State Machine enforces valid publication status transitions and prevents invalid state changes.

## State Diagram

```
                    ┌─────────┐
                    │  DRAFT   │
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
      ┌─────────┐  ┌─────────┐  ┌─────────┐
      │PREPARING│  │PUBLISHING│ │  FAILED  │
      └────┬────┘  └────┬────┘  └────┬────┘
           │             │            │
           │     ┌───────┴───────┐    │
           │     │               │    │
           ▼     ▼               ▼    ▼
      ┌─────────┐           ┌─────────┐
      │PUBLISHED│           │RETRYING │
      └────┬────┘           └────┬────┘
           │                     │
    ┌──────┼──────┐          ┌───┴───┐
    │      │      │          │       │
    ▼      ▼      ▼          ▼       ▼
┌────────┐ ┌────────┐  ┌────────┐ ┌────────┐
│UPDATING│ │ARCHIVED│  │SYNCING │ │PUBLISHING│
└────────┘ └────┬───┘  └────┬───┘ └────┬────┘
                │           │          │
                ▼           ▼          ▼
           ┌────────┐  ┌────────┐ ┌────────┐
           │PUBLISHED│ │DELETED │ │FAILED  │
           └────────┘  └────────┘ └────────┘
```

## Valid Transitions

| From | To |
|------|-----|
| draft | preparing, publishing, failed |
| preparing | publishing, draft, failed |
| publishing | published, failed, retrying |
| published | updating, archived, syncing, failed |
| updating | published, failed, retrying |
| archived | publishing, draft |
| deleted | (none) |
| syncing | published, failed |
| failed | retrying, preparing, draft, failed |
| retrying | publishing, failed, draft |

## Usage

```python
from core.state_machine import StateMachine, StatusManager

# Check transition validity
valid = StateMachine.can_transition("draft", "publishing")
# True

valid = StateMachine.can_transition("draft", "deleted")
# False

# Get valid targets
targets = StateMachine.get_valid_transitions("published")
# ['updating', 'archived', 'syncing', 'failed']

# Use StatusManager
manager = StatusManager()
mapping = {"publication_status": "draft"}

# Transition
result = manager.transition(mapping, "publishing")
# {"success": True, "old_status": "draft", "new_status": "publishing"}

# Check capabilities
can_publish = manager.can_publish(mapping)
can_update = manager.can_update(mapping)
can_archive = manager.can_archive(mapping)
can_delete = manager.can_delete(mapping)
```

## Validation

```python
validation = StateMachine.validate_transition("draft", "deleted")
# {
#     "valid": False,
#     "from_status": "draft",
#     "to_status": "deleted",
#     "valid_targets": ["preparing", "publishing", "failed"],
#     "error": "Invalid transition from draft to deleted..."
# }
```

## Terminal Statuses

Statuses with no outgoing transitions:
- `deleted`

## Initial Statuses

Valid starting points:
- `draft`
- `failed` (after failure)

## Best Practices

1. Always validate before transitioning
2. Log all transitions
3. Use StatusManager wrapper
4. Handle invalid transitions gracefully
5. Don't bypass state machine