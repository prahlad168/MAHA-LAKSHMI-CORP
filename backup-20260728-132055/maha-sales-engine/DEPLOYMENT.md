# MAHA Sales Engine V1 - Production Deployment Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (optional, for caching)
- 2GB+ RAM
- 10GB+ disk space

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd MAHA-LAKSHMI-CORP
```

### 2. Environment Setup
```bash
cd maha-sales-engine
cp .env.example .env
# Edit .env with your configuration
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Tests
```bash
pytest tests/ -v
```

### 5. Start with Docker Compose
```bash
docker-compose up -d
```

### 6. Verify Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/simple
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///data/maha.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | Application secret key | `change-me-in-production` |
| `MAHA_CONFIG_PATH` | Configuration file path | `config/engine.yaml` |
| `API_HOST` | API bind address | `0.0.0.0` |
| `API_PORT` | API bind port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Production Checklist

- [ ] Change default SECRET_KEY
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up Redis for caching
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup procedures
- [ ] Configure rate limiting
- [ ] Set up CI/CD pipeline
- [ ] Run security audit
- [ ] Run penetration testing
- [ ] Load testing
- [ ] Document runbooks

## Security Hardening

1. **Secrets Management**
   - Use environment variables or secret manager
   - Rotate secrets regularly
   - Never commit secrets to git

2. **Network Security**
   - Use HTTPS/TLS in production
   - Configure firewall rules
   - Use VPN for admin access

3. **Authentication**
   - Enable JWT authentication
   - Use strong API keys
   - Implement rate limiting

4. **Database Security**
   - Use parameterized queries (enforced)
   - Regular backups
   - Encrypt sensitive data

## Monitoring

### Health Endpoints
- `GET /health` - Detailed health check
- `GET /health/simple` - Simple health check
- `GET /status` - Service status

### Metrics
- `GET /metrics` - Prometheus metrics

### Logs
- Application logs: `logs/engine.log`
- Error logs: `logs/engine_errors.log`

## Backup Strategy

### Automated Backups
```bash
# Daily backup
python -m shared.backup --type database --source data/maha.db

# Weekly full backup
python -m shared.backup --type full --source data/ logs/ config/
```

### Backup Verification
```bash
# Verify backup integrity
python -m shared.backup --verify backup-id
```

## Scaling

### Horizontal Scaling
- Use multiple API gateway instances
- Load balancer in front (nginx, traefik)
- Shared Redis for caching
- Database connection pooling

### Vertical Scaling
- Increase worker count
- Increase database pool size
- Add more RAM/CPU

## Troubleshooting

### Common Issues

1. **Database locked**
   - Check connection pool settings
   - Increase pool size
   - Check for long-running queries

2. **High memory usage**
   - Enable Redis caching
   - Reduce cache size
   - Optimize queries

3. **Slow API responses**
   - Check database indexes
   - Enable caching
   - Optimize queries

### Logs
```bash
# View application logs
tail -f logs/engine.log

# View error logs
tail -f logs/engine_errors.log
```

## Support

- Documentation: `/docs`
- API Reference: `/redoc`
- Health Check: `/health`
