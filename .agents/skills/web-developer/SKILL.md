---
name: web-developer
description: This skill should be used when the user asks about web development, frontend, backend, React, Vue, Angular, HTML, CSS, JavaScript, web design, website creation, or any web application development tasks. Use for building websites, web apps, and understanding modern web technologies.
---

# Web Developer Skill

## Overview

Web development encompasses building websites and web applications, divided into:
- **Frontend** - User interface (HTML, CSS, JavaScript, frameworks)
- **Backend** - Server-side logic (databases, APIs, server)
- **Full-Stack** - Both frontend and backend combined

## Modern Web Development Best Practices (2026)

### Core Principles (7 Pillars)

1. **Performance**
   - LCP ≤ 2.5 seconds
   - INP ≤ 200ms (75th percentile)
   - Minimize bundle size
   - Use lazy loading

2. **Security**
   - Zero-trust architecture
   - OWASP Top 10 compliance
   - Input validation
   - XSS, SQL injection, CSRF protection

3. **Accessibility (WCAG 2.2 AA)**
   - Semantic HTML
   - ARIA labels
   - Keyboard navigation
   - Color contrast

4. **SEO**
   - SSR/ISR for search indexing
   - Schema.org markup
   - Meta tags optimization

5. **Mobile-First**
   - Responsive design
   - Touch-friendly interfaces
   - Performance on mobile

6. **Clean Code**
   - Strict TypeScript
   - Component architecture
   - Storybook for components

7. **CI/CD Automation**
   - Daily deploys
   - Auto-rollback
   - Automated testing

## Frontend Technologies

### Core Stack
- **HTML5** - Structure
- **CSS3** - Styling (Flexbox, Grid, Custom Properties)
- **JavaScript (ES6+)** - Interactivity
- **TypeScript** - Type safety

### Popular Frameworks (2024-2026)

| Framework | Type | Best For | Learning Curve |
|-----------|------|----------|----------------|
| React | Library | SPAs, Flexibility | Medium |
| Next.js | Meta-framework | SSR, SEO | Medium |
| Vue.js | Framework | Simplicity, Adaptable | Low-Medium |
| Angular | Framework | Enterprise, Large apps | High |
| Svelte | Compiler | Performance | Low |

### Key Concepts

1. **Component-Based Architecture**
   - Reusable UI components
   - Props for data passing
   - State management

2. **Server-Side Rendering (SSR)**
   - Next.js, Nuxt.js
   - Better SEO
   - Faster initial load

3. **Static Site Generation (SSG)**
   - Gatsby, Astro
   - Pre-built HTML
   - Maximum performance

## Backend Technologies

### Server Options
- **Node.js** - JavaScript runtime
- **Python (Django, Flask)** - Rapid development
- **Go** - Performance
- **Rust** - Safety & speed

### Databases
- **PostgreSQL** - Relational
- **MongoDB** - Document store
- **Redis** - Caching

### APIs
- REST APIs
- GraphQL
- WebSocket (real-time)

## Security Best Practices

### Frontend Security
- Sanitize user input
- HTTPS everywhere
- CSP (Content Security Policy)
- JWT tokens (stored securely)

### Backend Security
- Parameterized queries (prevent SQL injection)
- Rate limiting
- Input validation
- CSRF tokens

### OWASP Top 10 (2021)
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Auth Failures
8. Data Integrity Failures
9. Logging Failures
10. SSRF

## Performance Optimization

### Frontend
- Code splitting
- Tree shaking
- Image optimization
- CDN usage
- Caching strategies

### Backend
- Database indexing
- Query optimization
- Caching (Redis)
- Load balancing

## Resources

### Reference Files
- **`references/frameworks-comparison.md`** - Detailed framework comparison
- **`references/security-checklist.md`** - Security checklist
- **`references/performance-guide.md`** - Performance optimization guide

### Tools
- Lighthouse - Performance auditing
- PageSpeed Insights - Speed testing
- WebPageTest - Detailed analysis

## Common Tasks

1. **Build React App**: `npx create-react-app my-app` or `npm create vite@latest`
2. **Build Vue App**: `npm create vue@latest`
3. **Build Next.js App**: `npx create-next-app@latest`

## Indonesian Context

Indonesian web developers often:
- Focus on mobile-first (high mobile usage)
- Use Bootstrap or Tailwind CSS
- Target Indonesian market (local SEO)
- Consider Gojek/Grab integration
