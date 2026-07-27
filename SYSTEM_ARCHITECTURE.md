# SYSTEM ARCHITECTURE - MAHA SALES ENGINE V1

**Version:** 1.0.0  
**Status:** Approved  
**Parent Document:** MASTER_BLUEPRINT.md  
**Created:** 2026-07-27

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Windows Service / Linux Daemon             │
│                  (Auto-start, auto-restart, silent)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Core Engine                            │
│  • Lifecycle management                                       │
│  • Configuration                                              │
│  • Dependency injection                                        │
│  • Logging                                                    │
│  • Health monitoring                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         Scheduler                             │
│  • Job scheduling                                              │
│  • Retry with backoff                                         │
│  • Priority queue                                              │
│  • Background workers                                          │
│  • 24/7 operation                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Business Modules                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Product    │  │     Market   │  │ Marketplace  │       │
│  │   Manager    │  │ Intelligence │  │   Manager    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Content   │  │  Analytics   │  │ Performance  │       │
│  │    Engine    │  │              │  │   Reporter   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Local Database (SQLite)                     │
│  • Products, leads, outreach, transactions, reports, metrics   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 Encrypted HTTPS API (mTLS + JWT)              │
│              mahalaksmi.web.id ← Mission Control              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Module Responsibilities

### 2.1 Core Engine
- Application startup and shutdown
- Configuration loading and validation
- Module registration and lifecycle
- Logging initialization
- Health monitoring
- Signal handling for graceful shutdown

### 2.2 Scheduler
- Time-based job execution
- Retry logic with configurable backoff
- Priority-based job queue
- Worker thread pool
- Job enable/disable controls
- Execution history tracking

### 2.3 Product Manager
- Product CRUD operations
- Category management
- Pricing management (multi-currency)
- Media and version tracking
- Marketplace listing association
- Status management (draft/active/paused/archived)

### 2.4 Market Intelligence
- Market opportunity scoring
- Demand analysis
- Competitor monitoring
- Keyword discovery
- Template optimization
- Targeting optimization

### 2.5 Marketplace Manager
- Integration registry
- Listing creation and updates
- Publication status tracking
- Sync operations
- Statistics aggregation

### 2.6 Content Engine
- Template management
- Personalization engine
- Multi-language support
- SEO keyword integration
- Landing page content generation
- Content calendar generation

### 2.7 Analytics
- Daily/weekly/monthly metrics
- Product performance
- Channel performance
- Country performance
- Revenue trends
- Conversion funnel
- Dashboard summary generation

### 2.8 Performance Reporter
- Heartbeat transmission
- Daily report generation
- Secure HTTPS transmission
- Retry on failure
- Sync log maintenance

---

## 3. Process Model

### 3.1 Main Thread
- Initializes Core Engine
- Registers all modules
- Starts Scheduler
- Blocks on main loop
- Handles shutdown signals

### 3.2 Scheduler Threads
- 1 scheduler loop thread
- N worker threads (default: 4)
- Job queue with priority

### 3.3 Module Threads
Each module may spawn background threads:
- Market Intelligence: daily analysis thread
- Performance Reporter: heartbeat thread, report thread
- Analytics: periodic aggregation thread

---

## 4. Data Flow

### 4.1 Outbound Flow (Node → Dashboard)
```
Heartbeat (every 60s):
  HealthMonitor → PerformanceReporter → HTTPS POST → Dashboard

Daily Report (every 23:59):
  Analytics → PerformanceReporter → HTTPS POST → Dashboard
```

### 4.2 Inbound Flow (Dashboard → Node)
```
Commands (every 30s):
  Dashboard → HTTPS GET → PerformanceReporter → Scheduler → Module
```

### 4.3 Internal Flow
```
Scheduler → ProductManager → Database
Scheduler → MarketIntelligence → Database
Scheduler → MarketplaceManager → External APIs
Scheduler → ContentEngine → Database
Scheduler → Analytics → Database
```

---

## 5. Configuration Model

All configuration is stored in `config/engine.yaml` and loaded at startup.

Key configuration sections:
- `engine` - Node identity, environment
- `dashboard` - Mission Control connection
- `sales` - Targets and product lists
- `channels` - Email, WhatsApp, LinkedIn settings
- `database` - Path and retention
- `logging` - Levels and rotation
- `security` - Certificates and keys
- `marketplaces` - API credentials
- `ai` - Model settings
- `windows_service` - Service metadata

Configuration changes require restart.

---

## 6. Logging Strategy

- Structured logging with consistent format
- Rotating file handlers per module
- Separate log files for:
  - `engine.log` - Core engine events
  - `scheduler.log` - Job execution
  - `sales.log` - Sales activities
  - `errors.log` - Errors only
  - `api.log` - Dashboard communications
- Log retention: 5 files × 10 MB each
- Never log secrets or credentials

---

## 7. Health Monitoring

Health metrics collected:
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Uptime (seconds)
- Active modules count
- Error count
- Warning count

Health check endpoint: `GET /health`  
Dashboard heartbeat: `POST /api/v1/sales-node/heartbeat`

---

## 8. Error Handling

- All public methods must catch and log exceptions
- Scheduler retries failed jobs with exponential backoff
- Failed jobs are logged with full context
- Critical errors trigger alerts
- Graceful shutdown on SIGINT/SIGTERM

---

## 9. Extension Points

New modules can be added by:
1. Implementing `start()` and `stop()` methods
2. Registering with `engine.register_module(name, instance)`
3. Creating scheduled jobs via `scheduler.register_job(job)`

Module dependencies are injected via constructor.

---

## 10. Constraints

- Local database only (SQLite) - no external DB required
- All paths must be relative or configurable for portability
- No hardcoded credentials
- Minimal external dependencies
- Must run on Windows 10+ and Linux

---

**Approved By:** CEO / Lead Architect  
**Date:** 2026-07-27  
**Next Review:** 2026-08-27
