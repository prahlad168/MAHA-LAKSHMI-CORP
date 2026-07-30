# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-30

### Added

- MAHA AI Command Center (MACC) CEO dashboard
- Product Factory with autonomous digital product generation
- Marketing Engine with AI-powered content creation
- Sales Automation Engine with workflow orchestration
- Business Execution Pipeline with daily automation
- Marketplace integration framework (Gumroad, Shopify, Etsy, etc.)
- Scheduler with retry and queue management
- Health monitoring and metrics collection
- Docker production deployment configuration
- CI/CD pipeline with GitHub Actions
- Database migration system with rollback support
- API gateway with authentication and authorization
- Comprehensive test suite (339 passing tests)

### Changed

- Consolidated all modules under unified `maha-sales-engine` repository
- Standardized module naming conventions
- Centralized configuration management
- Unified logging and monitoring

### Fixed

- Windows-specific test cleanup issues
- Circular import resolution across modules
- Database connection lifecycle management
- Scheduler startup reliability

### Security

- JWT authentication implementation
- API key management
- Rate limiting
- Input validation and sanitization
- SQL injection prevention

### Documentation

- Production deployment guide
- API documentation
- Installation instructions
- Docker setup guide
- Environment variable reference

## [0.9.0] - 2026-07-21

### Added

- Initial product factory implementation
- Basic marketing automation
- Sales automation core
- Marketplace connector prototype

### Changed

- Architecture refinement
- Module reorganization

### Fixed

- Initial bug fixes and stability improvements

---

**Release Notes**: See [RELEASE_NOTES.md](RELEASE_NOTES.md) for detailed v1.0.0 release information.
