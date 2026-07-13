# Web Security Checklist

## Frontend Security

### 1. Cross-Site Scripting (XSS) Prevention

**What is XSS?**
Attacker injects malicious scripts into web pages viewed by other users.

**Prevention:**
```javascript
// ❌ Dangerous - Direct HTML insertion
element.innerHTML = userInput;

// ✅ Safe - Text content
element.textContent = userInput;

// ✅ Safe - DOMPurify for HTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

**Guidelines:**
- Always sanitize user input
- Use Content Security Policy (CSP)
- Encode output (HTML entities)
- Use React/Vue's built-in escaping

### 2. HTTPS Everywhere

```html
<!-- Force HTTPS -->
<meta http-equiv="Strict-Transport-Security" content="max-age=31536000; includeSubDomains">
```

**Guidelines:**
- Always use HTTPS in production
- Redirect HTTP to HTTPS
- Use valid SSL/TLS certificates
- Enable HSTS

### 3. Authentication Security

```javascript
// ✅ Store tokens securely
// Use httpOnly cookies (not localStorage)
// localStorage is vulnerable to XSS

// ❌ Never do this
localStorage.setItem('token', jwtToken);

// ✅ Better approach
// Set httpOnly cookie from backend
// Use Secure flag
document.cookie = "token=xxx; Secure; HttpOnly; SameSite=Strict";
```

**Best Practices:**
- Use secure cookies, not localStorage
- Implement CSRF tokens
- Short token expiration
- Refresh token rotation

### 4. Input Validation

```javascript
// ✅ Always validate on frontend AND backend
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePassword(password) {
  return password.length >= 8 && 
         /[A-Z]/.test(password) &&
         /[0-9]/.test(password);
}
```

## Backend Security

### 1. SQL Injection Prevention

```javascript
// ❌ Dangerous - SQL injection vulnerable
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ✅ Safe - Parameterized query
const query = 'SELECT * FROM users WHERE email = $1';
await db.query(query, [email]);
```

### 2. Rate Limiting

```javascript
// Express rate limiting
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests
  message: 'Too many requests'
});

app.use('/api', limiter);
```

### 3. Security Headers

```javascript
// helmet.js for Express
import helmet from 'helmet';

app.use(helmet());

// Sets:
// - Content-Security-Policy
// - X-Content-Type-Options
// - X-Frame-OPTIONS
// - Strict-Transport-Security
```

### 4. Environment Variables

```bash
# ❌ Never commit these
.env
config.js with secrets

# ✅ Use .env.example (no secrets)
DATABASE_URL=postgres://localhost:5432/db
API_KEY=your_api_key_here

# ✅ In production, use:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Environment injection
```

## OWASP Top 10 (2021) Checklist

### 1. Broken Access Control
- [ ] Implement proper authorization
- [ ] Deny by default
- [ ] Log access control failures
- [ ] Rate limit API access

### 2. Cryptographic Failures
- [ ] Use strong password hashing (bcrypt, Argon2)
- [ ] Encrypt sensitive data at rest
- [ ] Use TLS for data in transit
- [ ] Don't store unnecessary data

### 3. Injection
- [ ] Use parameterized queries
- [ ] Sanitize and validate input
- [ ] Escape special characters
- [ ] Use ORM when possible

### 4. Insecure Design
- [ ] Threat modeling
- [ ] Secure design patterns
- [ ] Limit resource consumption
- [ ] Segregate tenant resources

### 5. Security Misconfiguration
- [ ] Remove debug mode in production
- [ ] Disable directory listing
- [ ] Configure security headers
- [ ] Automated security scanning

### 6. Vulnerable Components
- [ ] Keep dependencies updated
- [ ] Remove unused dependencies
- [ ] Monitor for vulnerabilities (npm audit)
- [ ] Use only official sources

### 7. Authentication Failures
- [ ] Implement multi-factor authentication
- [ ] Don't deploy with default credentials
- [ ] Password recovery should be secure
- [ ] Log authentication failures

### 8. Data Integrity Failures
- [ ] Verify data integrity
- [ ] Use digital signatures
- [ ] Don't trust unsigned data
- [ ] CI/CD integrity verification

### 9. Logging & Monitoring
- [ ] Log all security events
- [ ] Ensure logs are tamper-proof
- [ ] Set up alerting
- [ ] Regular log review

### 10. Server-Side Request Forgery (SSRF)
- [ ] Validate user-provided URLs
- [ ] Use allowlists for URLs
- [ ] Disable HTTP redirections
- [ ] Segment network access

## Quick Security Checklist

### Before Deployment
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Debug mode OFF
- [ ] Error messages don't leak info
- [ ] Dependencies audited (`npm audit`)
- [ ] Environment variables set
- [ ] Rate limiting enabled
- [ ] CORS configured properly

### Code Review Points
- [ ] No hardcoded secrets
- [ ] Input validation everywhere
- [ ] Output encoding
- [ ] Proper authentication
- [ ] Authorization checks
- [ ] Secure cookies
- [ ] SQL injection safe
- [ ] XSS protection
