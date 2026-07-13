# Web Performance Optimization Guide

## Core Web Vitals (2026)

### What to Measure

| Metric | Target | What It Measures |
|--------|--------|------------------|
| **LCP** | ≤ 2.5s | Largest Contentful Paint |
| **INP** | ≤ 200ms | Interaction to Next Paint |
| **CLS** | ≤ 0.1 | Cumulative Layout Shift |
| **FID** | < 100ms | First Input Delay |

## Frontend Performance

### 1. Optimize Images

```html
<!-- ❌ Bad - No optimization -->
<img src="huge-image.jpg">

<!-- ✅ Good - Responsive images -->
<img src="small.jpg" srcset="small.jpg 500w, medium.jpg 1000w, large.jpg 2000w" 
     sizes="(max-width: 600px) 100vw, 50vw" alt="Description">

<!-- ✅ Modern - WebP with fallback -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description">
</picture>

<!-- ✅ Lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description">
```

### 2. Code Splitting

```javascript
// ✅ React - Lazy load components
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <HeavyComponent />
    </Suspense>
  );
}

// ✅ Next.js - Dynamic imports
import dynamic from 'next/dynamic';
const DynamicComponent = dynamic(() => import('../components/Heavy'), {
  loading: () => <p>Loading...</p>,
  ssr: false // Disable SSR if needed
});
```

### 3. Tree Shaking

```javascript
// ✅ In webpack/vite.config.js
// Tree shaking is automatic with ES modules

// ❌ Import entire library (large bundle)
import _ from 'lodash';

// ✅ Import specific function (small bundle)
import debounce from 'lodash/debounce';

// ✅ Even better - use alternatives
import { debounce } from 'lodash-es'; // ES module version
```

### 4. Caching Strategies

```javascript
// Service Worker for caching
const CACHE_NAME = 'v1';
const urlsToCache = ['/', '/static/js/main.js', '/static/css/main.css'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Cache hit - return response
      if (response) return response;
      return fetch(event.request).then(response => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200) return response;
        return response;
      });
    })
  );
});
```

### 5. Critical CSS

```html
<!-- ✅ Inline critical CSS -->
<head>
  <style>
    /* Critical CSS for above-the-fold content */
    body { margin: 0; font-family: sans-serif; }
    .header { background: #333; color: white; }
  </style>
  <!-- Non-critical CSS loaded async -->
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
</head>
```

## Bundle Size Optimization

### Analyze Bundle

```bash
# Use webpack-bundle-analyzer
npm install --save-dev webpack-bundle-analyzer

# In webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
module.exports = {
  plugins: [
    new BundleAnalyzerPlugin()
  ]
};
```

### Common Size Issues

| Library | Minified | Gzipped | Alternative |
|---------|----------|---------|-------------|
| Moment.js | 71KB | 22KB | date-fns (3KB) |
| Lodash | 531KB | 89KB | lodash-es + tree shake |
| Bootstrap | 180KB | 21KB | Tailwind CSS (10KB) |
| Axios | 13KB | 5KB | fetch (built-in) |

## Backend Performance

### 1. Database Optimization

```sql
-- ✅ Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_created ON posts(created_at);

-- ✅ Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM posts WHERE user_id = 1;

-- ✅ Optimize with proper JOINs
SELECT posts.*, users.name 
FROM posts 
INNER JOIN users ON posts.user_id = users.id 
WHERE posts.published = true;
```

### 2. Caching

```javascript
// ✅ Redis caching example
const redis = require('redis');
const client = redis.createClient();

async function getUser(id) {
  const cacheKey = `user:${id}`;
  const cached = await client.get(cacheKey);
  
  if (cached) {
    return JSON.parse(cached); // Cache hit
  }
  
  // Cache miss - fetch from DB
  const user = await db.users.findById(id);
  
  // Store in cache for 1 hour
  await client.setEx(cacheKey, 3600, JSON.stringify(user));
  
  return user;
}
```

### 3. API Optimization

```javascript
// ✅ Pagination
app.get('/api/posts', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  
  const posts = await db.posts
    .findAll({ limit, offset })
    .sort({ created_at: -1 });
    
  const total = await db.posts.count();
  
  res.json({
    data: posts,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit)
    }
  });
});

// ✅ Compression
import compression from 'compression';
app.use(compression());
```

## Performance Testing Tools

| Tool | Purpose | URL |
|------|---------|-----|
| Lighthouse | Automated auditing | Chrome DevTools |
| PageSpeed Insights | Real-world data | pagespeed.web.dev |
| WebPageTest | Detailed analysis | webpagetest.org |
| GTmetrix | Performance grades | gtmetrix.com |
| Web Vitals | Core Vitals tracking | web.dev/vitals |

## Quick Wins Checklist

- [ ] Optimize and compress images
- [ ] Enable gzip/brotli compression
- [ ] Minify CSS, JS, HTML
- [ ] Use CDN for static assets
- [ ] Implement lazy loading
- [ ] Add cache headers
- [ ] Remove unused code
- [ ] Preload critical resources
- [ ] Reduce HTTP requests
- [ ] Use efficient fonts (WOFF2)
