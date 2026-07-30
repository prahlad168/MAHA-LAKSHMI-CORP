# Mission Control Architecture - MAHA Sales Engine V1

## Overview

Mission Control is architected as a modular, layered system that provides executive oversight for the MAHA Sales Engine V1. It follows clean architecture principles with clear separation of concerns.

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                        │
│  - REST endpoints                                            │
│  - Request/response validation                               │
│  - Authentication middleware                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Layer (Orchestration)                   │
│  - MissionController                                         │
│  - PermissionManager                                         │
│  - Business logic coordination                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (Business Logic)               │
│  - MissionService                                            │
│  - Workflow orchestration                                    │
│  - Integration with existing modules                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer (Data Access)                 │
│  - MissionRepository                                         │
│  - Database operations                                       │
│  - Query optimization                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Layer (Data Structures)              │
│  - MissionContext                                            │
│  - MissionConfig                                             │
│  - MissionMetric                                             │
│  - MissionAlert                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Diagram

### Core Components

```
MissionController
├── MissionConfig (configuration)
├── DatabaseManager (data access)
├── AuthManager (authentication)
├── MissionService (business logic)
└── PermissionManager (authorization)
```

### Service Layer

```
MissionService
├── MissionRepository (data access)
├── DatabaseManager (connection)
└── AuthManager (authorization)
```

### Repository Layer

```
MissionRepository
├── DatabaseManager (connection)
└── SQLite database
    ├── missions table
    ├── mission_metrics table
    ├── mission_alerts table
    └── mission_audit table
```

## Data Flow

### Mission Creation Flow

1. **API Request** → MissionRouter validates request
2. **Permission Check** → PermissionManager validates access
3. **Context Creation** → MissionContext created with user info
4. **Service Layer** → MissionService orchestrates creation
5. **Repository** → MissionRepository persists to database
6. **Response** → JSON response returned to client

### Metrics Collection Flow

1. **Metric Generation** → System generates metric data
2. **Service Layer** → MissionService validates metric
3. **Repository** → MissionRepository stores metric
4. **Cache Update** → In-memory cache updated

## Dependency Diagram

```
External Dependencies:
├── shared.core_engine (CoreEngine)
├── shared.database (DatabaseManager)
├── shared.auth (AuthManager)
└── FastAPI (web framework)

Internal Dependencies:
├── mission_control.models
├── mission_control.repositories
├── mission_control.services
└── mission_control.permissions
```

## Database Schema

### Tables

1. **missions** - Core mission records
   - mission_id (PK)
   - name, status, config, result
   - created_at, updated_at

2. **mission_metrics** - Time-series metrics
   - metric_id (PK)
   - mission_id (FK)
   - name, value, unit, timestamp, tags

3. **mission_alerts** - Alert records
   - alert_id (PK)
   - mission_id (FK)
   - severity, message, source, timestamp, acknowledged

4. **mission_audit** - Audit trail
   - audit_id (PK)
   - mission_id (FK)
   - action, user_id, timestamp, details

## Security Architecture

### Authentication Flow

1. **Token Validation** → PermissionManager.validate_token()
2. **Permission Check** → PermissionManager.check_permission()
3. **Access Control** → Resource-level authorization

### Role Hierarchy

```
CEO (Level 100)
├── All permissions
└── System administration

ADMIN (Level 80)
├── Mission management
├── Metric management
├── Alert management
└── Audit viewing

OPERATOR (Level 60)
├── Mission read/write
├── Metric read/write
├── Alert read/write
└── Audit read

VIEWER (Level 40)
├── Mission read
├── Metric read
└── Alert read
```

## Extension Points

### Adding New Mission Types

1. Define mission configuration schema
2. Implement validation logic in MissionService
3. Register new permission rules
4. Add API endpoints as needed

### Adding New Metrics

1. Define metric schema in models
2. Implement collection logic in MissionService
3. Add repository methods for persistence
4. Expose via API endpoints

### Adding New Alerts

1. Define alert severity levels
2. Implement alert generation logic
3. Add notification channels
4. Configure alert rules

## Performance Considerations

- **Connection Pooling**: Reuse database connections
- **Caching**: In-memory cache for frequently accessed data
- **Indexing**: Database indexes on frequently queried columns
- **Asynchronous Processing**: Non-blocking I/O for better throughput

## Monitoring and Observability

- **Structured Logging**: All operations logged with context
- **Metrics Collection**: Performance and business metrics
- **Health Checks**: System health endpoints
- **Audit Trail**: Complete action history
