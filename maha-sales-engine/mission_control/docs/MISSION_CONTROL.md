# Mission Control - MAHA Sales Engine V1

## Purpose

Mission Control is the executive oversight system for MAHA Sales Engine V1. It provides:

- Centralized monitoring of all sales engine operations
- Executive dashboard for CEO and administrators
- Real-time system health and performance metrics
- Audit logging for all critical operations
- Role-based access control for mission-critical functions

## Module Structure

```
mission-control/
├── __init__.py                 # Package initialization
├── core/                       # Core business logic
│   ├── __init__.py
│   └── mission_controller.py  # Main controller
├── models/                     # Data models and schemas
│   ├── __init__.py
│   └── models.py              # MissionContext, MissionConfig, etc.
├── services/                   # Business services
│   ├── __init__.py
│   └── mission_service.py     # Mission orchestration service
├── repositories/               # Data access layer
│   ├── __init__.py
│   └── mission_repository.py  # Database operations
├── api/                        # REST API endpoints
│   ├── __init__.py
│   └── mission_router.py      # API router
├── permissions/                # Access control
│   ├── __init__.py
│   └── permission_manager.py  # RBAC implementation
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_mission_control.py # Unit and integration tests
└── docs/                       # Documentation
    └── __init__.py
```

## Architecture

Mission Control follows a layered architecture:

1. **API Layer**: FastAPI endpoints for external access
2. **Core Layer**: Business logic orchestration
3. **Service Layer**: Business operations and workflows
4. **Repository Layer**: Data access and persistence
5. **Model Layer**: Data structures and schemas

## Integration

Mission Control integrates with existing MAHA Sales Engine modules:

- **Core Engine**: Lifecycle management and dependency injection
- **Database**: Shared database utilities for data persistence
- **Authentication**: Shared auth manager for user management
- **Logging**: Shared logging utilities for observability

## Extension Points

Mission Control is designed for extensibility:

- New mission types can be added via configuration
- Additional metrics can be registered dynamically
- Custom permission rules can be defined
- New API endpoints can be added to the router

## Security

- Role-based access control (RBAC)
- Permission validation for all operations
- Audit logging for all actions
- Token-based authentication
