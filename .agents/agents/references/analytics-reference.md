# Analytics Deep Knowledge - For analytics-agent

## Google Analytics 4 Setup

### 1. GA4 Installation

```html
<!-- Google tag (gtag.js) -->
<!-- Add this to every page, right after <head> tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  
  // Basic config
  gtag('config', 'G-XXXXXXXXXX');
  
  // Or with additional config
  gtag('config', 'G-XXXXXXXXXX', {
    '送send_page_view': false  // Manual page view
  });
</script>
```

### 2. Event Tracking

```javascript
// Manual page view
gtag('event', 'page_view', {
  'page_title': document.title,
  'page_location': window.location.href,
  'page_path': window.location.pathname
});

// Custom events
gtag('event', 'login', {
  'method': 'google' // or 'email', 'facebook', etc.
});

gtag('event', 'purchase', {
  'currency': 'IDR',
  'transaction_id': 'T12345',
  'value': 299000,
  'tax': 29900,
  'shipping': 15000,
  'items': [
    {
      'item_id': 'SKU123',
      'item_name': 'Produk A',
      'item_category': 'Elektronik',
      'item_variant': 'Hitam',
      'price': 250000,
      'quantity': 1
    },
    {
      'item_id': 'SKU456',
      'item_name': 'Produk B',
      'item_category': 'Aksesoris',
      'price': 49000,
      'quantity': 1
    }
  ]
});

// Enhanced ecommerce tracking
gtag('event', 'view_item', {
  'currency': 'IDR',
  'value': 250000,
  'items': [{
    'item_id': 'SKU123',
    'item_name': 'Produk A',
    'item_category': 'Elektronik',
    'item_brand': 'Brand A',
    'price': 250000,
    'quantity': 1
  }]
});

gtag('event', 'add_to_cart', {
  'currency': 'IDR',
  'value': 250000,
  'items': [{
    'item_id': 'SKU123',
    'item_name': 'Produk A',
    'price': 250000,
    'quantity': 1
  }]
});

gtag('event', 'begin_checkout', {
  'currency': 'IDR',
  'value': 299000
});

gtag('event', 'sign_up', {
  'method': 'Google'
});
```

### 3. React GA4 Integration

```javascript
// hooks/useGA4.js
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export function useGA4(measurementId) {
  const location = useLocation();
  
  useEffect(() => {
    if (!measurementId) return;
    
    // Load gtag
    const script = document.createElement('script');
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    script.async = true;
    document.head.appendChild(script);
    
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() {
      dataLayer.push(arguments);
    };
    gtag('js', new Date());
    gtag('config', measurementId);
    
    return () => {
      document.head.removeChild(script);
    };
  }, [measurementId]);
  
  // Track page views
  useEffect(() => {
    if (window.gtag) {
      window.gtag('event', 'page_view', {
        page_path: location.pathname,
        page_search: location.search,
        page_hash: location.hash
      });
    }
  }, [location]);
}

// Custom hook for events
export function useTrackEvent() {
  const trackEvent = (eventName, parameters = {}) => {
    if (window.gtag) {
      window.gtag('event', eventName, parameters);
    }
  };
  
  return {
    trackEvent,
    trackPurchase: (data) => trackEvent('purchase', data),
    trackLogin: (method) => trackEvent('login', { method }),
    trackSignUp: (method) => trackEvent('sign_up', { method }),
    trackSearch: (searchTerm) => trackEvent('search', { search_term: searchTerm }),
    trackShare: (content, method) => trackEvent('share', { content_type: content, method }),
    trackVideo: (action, label) => trackEvent('video', { action, label })
  };
}

// Usage in component
function ProductCard({ product }) {
  const { trackEvent } = useTrackEvent();
  
  const handleAddToCart = () => {
    trackEvent('add_to_cart', {
      currency: 'IDR',
      value: product.price,
      items: [{
        item_id: product.id,
        item_name: product.name,
        price: product.price
      }]
    });
  };
  
  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}
```

## Google Tag Manager

### 1. GTM Setup

```html
<!-- GTM Container -->
<!-- Place this as high as possible in <head> -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXX');</script>

<!-- GTM noscript in <body> -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
```

### 2. Custom HTML Tags in GTM

```javascript
// Facebook Pixel
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');

fbq('init', 'XXXXXXXXXX');
fbq('track', 'PageView');

// Trigger on specific events
fbq('track', 'ViewContent', {
  content_ids: ['product_123'],
  content_type: 'product',
  value: 29.99,
  currency: 'USD'
});
```

## User Analysis

### 1. Funnel Analysis

```javascript
// Define your conversion funnel
const funnel = {
  name: 'Checkout Funnel',
  steps: [
    { name: 'Product View', event: 'view_item' },
    { name: 'Add to Cart', event: 'add_to_cart' },
    { name: 'Begin Checkout', event: 'begin_checkout' },
    { name: 'Add Payment', event: 'add_payment_info' },
    { name: 'Purchase', event: 'purchase' }
  ]
};

// Calculate funnel metrics
function analyzeFunnel(userEvents) {
  const results = [];
  let previousCount = userEvents.length;
  
  for (const step of funnel.steps) {
    const stepUsers = userEvents.filter(e => e.event === step.event).length;
    const dropoff = ((previousCount - stepUsers) / previousCount * 100).toFixed(2);
    const conversionRate = (stepUsers / userEvents.length * 100).toFixed(2);
    
    results.push({
      step: step.name,
      users: stepUsers,
      dropoff: `${dropoff}%`,
      conversionRate: `${conversionRate}%`
    });
    
    previousCount = stepUsers;
  }
  
  return results;
}
```

### 2. Cohort Analysis

```javascript
// Cohort analysis for retention
function cohortAnalysis(userData) {
  // Group users by signup week
  const cohorts = {};
  
  userData.forEach(user => {
    const signupWeek = getWeek(user.signupDate);
    const weekNumber = getWeek(new Date()) - signupWeek;
    
    if (!cohorts[signupWeek]) {
      cohorts[signupWeek] = { total: 0, retained: {} };
    }
    
    cohorts[signupWeek].total++;
    
    // Check retention per week
    user.activityWeeks.forEach(activityWeek => {
      const weekDiff = activityWeek - signupWeek;
      cohorts[signupWeek].retained[weekDiff] = 
        (cohorts[signupWeek].retained[weekDiff] || 0) + 1;
    });
  });
  
  // Calculate retention rates
  const retentionMatrix = [];
  
  Object.entries(cohorts).forEach(([week, data]) => {
    const row = { cohort: `Week ${week}` };
    
    for (let i = 0; i <= 4; i++) {
      const retained = data.retained[i] || 0;
      row[`Week ${i}`] = data.total > 0 
        ? `${((retained / data.total) * 100).toFixed(1)}%` 
        : '0%';
    }
    
    retentionMatrix.push(row);
  });
  
  return retentionMatrix;
}
```

## Key Metrics

### KPIs for E-commerce

```javascript
const ecommerceMetrics = {
  // Acquisition
  sessions: 'Total visits',
  users: 'Unique visitors',
  newUsers: 'First-time visitors',
  trafficSources: 'Where visitors come from',
  
  // Behavior
  bounceRate: 'Single page sessions percentage',
  avgSessionDuration: 'Average time on site',
  pagesPerSession: 'Pages viewed per visit',
  pageViews: 'Total page views',
  
  // Conversion
  conversionRate: 'Visitors who complete goal / Total visitors',
  addToCartRate: 'Add to cart / Product views',
  cartAbandonmentRate: '1 - Checkout started / Add to cart',
  purchaseConversionRate: 'Purchase / Sessions',
  
  // Revenue
  revenue: 'Total sales',
  averageOrderValue: 'Revenue / Orders',
  revenuePerUser: 'Revenue / Unique users',
  
  // Retention
  returningUsers: 'Users who visited before',
  customerLifetimeValue: 'Total revenue per customer',
  churnRate: 'Users who stopped visiting'
};

// Calculate metrics
function calculateMetrics(data) {
  return {
    conversionRate: (data.purchases / data.sessions * 100).toFixed(2) + '%',
    avgOrderValue: formatCurrency(data.revenue / data.orders),
    cartAbandonment: ((data.addedToCart - data.startedCheckout) / data.addedToCart * 100).toFixed(2) + '%',
    revenuePerUser: formatCurrency(data.revenue / data.users)
  };
}
```

## Dashboard Setup

### 1. GA4 Dashboard JSON

```javascript
// GA4 Dashboard Configuration
const dashboardConfig = {
  reportTitle: 'E-commerce Dashboard',
  metrics: [
    { name: 'sessions', label: 'Sessions' },
    { name: 'totalRevenue', label: 'Revenue' },
    { name: 'ecommercePurchases', label: 'Purchases' },
    { name: 'addToCart', label: 'Add to Cart' },
    { name: 'beginCheckout', label: 'Checkout Started' }
  ],
  dimensions: [
    { name: 'date', label: 'Date' },
    { name: 'deviceCategory', label: 'Device' },
    { name: 'country', label: 'Country' },
    { name: 'source', label: 'Source' },
    { name: 'medium', label: 'Medium' }
  ],
  comparisons: [
    { name: 'deviceCategory', values: ['desktop', 'mobile', 'tablet'] },
    { name: 'userType', values: ['new', 'returning'] }
  ]
};
```

### 2. Custom Report

```javascript
// Create custom GA4 report
async function getCustomReport(analytics, dateRange) {
  return await analytics.runReport({
    dateRanges: [{
      startDate: dateRange.startDate,
      endDate: dateRange.endDate
    }],
    dimensions: [
      { name: 'pagePath' },
      { name: 'deviceCategory' },
      { name: 'country' }
    ],
    metrics: [
      { name: 'screenPageViews' },
      { name: 'totalUsers' },
      { name: 'averageSessionDuration' },
      { name: 'eventCount' }
    ],
    orderBys: [
      { metric: { metricName: 'screenPageViews' }, desc: true }
    ],
    limit: 100
  });
}
```
