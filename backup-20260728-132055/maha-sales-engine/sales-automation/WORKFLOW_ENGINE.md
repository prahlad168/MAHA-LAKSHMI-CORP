# MAHA SALES ENGINE V1 - Workflow Engine Documentation

## Overview

Visual workflow representation, building, and execution for sales automation.

## Workflow Nodes

- **Validation** - Validate inputs and preconditions
- **Decision** - Branch based on conditions
- **Approval** - Human-in-the-loop approval
- **Delay** - Wait for scheduled time
- **Publish** - Execute publication
- **Synchronize** - Sync with marketplace
- **Notification** - Send notifications
- **Retry** - Retry on failure
- **Terminate** - End workflow

## Usage

```python
from workflow.engine import WorkflowBuilder

builder = WorkflowBuilder()
builder.add_node("start", "validation", "Start", {}, ["publish"])
builder.add_node("publish", "publish", "Publish", {}, ["notify"])
builder.add_node("notify", "notification", "Notify", {}, ["end"])
builder.set_entry("start")
builder.set_exit("end")

workflow = builder.build("Product Launch Workflow")
```

## Workflow Definition

```json
{
  "workflow_id": "wf-abc123",
  "name": "Product Launch Workflow",
  "version": "1.0.0",
  "nodes": [...],
  "entry_node": "start",
  "exit_node": "end"
}
```

## Features

- Visual node representation
- Versioned workflows
- Rollback support
- Export/Import
- Execution tracking