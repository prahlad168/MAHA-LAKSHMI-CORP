# MAHA SALES ENGINE V1 - Sync Engine

Synchronizes product data between internal system and Gumroad marketplace.

## Sync Types

### Manual Sync
Triggered via API:
```bash
POST /marketplace/sync
POST /marketplace/sync/{productId}
```

### Scheduled Sync
Configured via cron or scheduler:
```python
await sync_engine.sync(SyncType.SCHEDULED)
```

### Bulk Sync
Sync all products:
```python
await sync_engine.sync(SyncType.BULK)
```

### Inventory Sync
Sync product inventory and availability:
```python
await sync_engine.sync(SyncType.INVENTORY)
```

### Publication Refresh
Refresh publication status:
```python
await sync_engine.sync(SyncType.PUBLICATION_REFRESH)
```

## Conflict Detection

When syncing, the engine detects conflicts between:
- Internal product data
- Marketplace product data
- Previous sync state

Conflicts are logged and can be resolved via:
- Accept marketplace version
- Accept internal version
- Manual merge

## Status Reconciliation

After sync, statuses are reconciled:
- Published on both sides → OK
- Internal published, marketplace draft → Update marketplace
- Marketplace published, internal draft → Update internal
- Failed on both sides → Investigate

## Usage

```python
from marketplace_connector.sync.sync_engine import SyncEngine, SyncType

sync_engine = SyncEngine(provider, db_manager)

# Single product sync
job = await sync_engine.sync(SyncType.SINGLE_PRODUCT, "prod-001")

# Bulk sync
job = await sync_engine.sync(SyncType.BULK)
```

## Job Status

- `pending` - Queued for sync
- `running` - Currently syncing
- `completed` - Sync successful
- `failed` - Sync failed
- `partial` - Partial success
