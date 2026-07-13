# SEO Deep Knowledge - For seo-agent

## On-Page SEO

### 1. Meta Tags

```html
<head>
  <!-- Primary Meta Tags -->
  <title>Judul Halaman Optimal | Nama Website</title>
  <meta name="title" content="Judul Halaman Optimal untuk SEO">
  <meta name="description" content="Deskripsi halaman 150-160 karakter yang mengandung kata kunci utama dan CTA yang jelas untuk meningkatkan CTR di hasil pencarian.">
  <meta name="keywords" content="kata kunci 1, kata kunci 2, kata kunci utama">
  <meta name="author" content="Nama Author">
  <meta name="robots" content="index, follow">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="https://example.com/halaman">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://example.com/halaman">
  <meta property="og:title" content="Judul untuk Social Media Share">
  <meta property="og:description" content="Deskripsi 150-200 karakter untuk social media">
  <meta property="og:image" content="https://example.com/images/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="id_ID">
  <meta property="og:site_name" content="Nama Website">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="https://example.com/halaman">
  <meta name="twitter:title" content="Judul untuk Twitter">
  <meta name="twitter:description" content="Deskripsi untuk Twitter">
  <meta name="twitter:image" content="https://example.com/images/twitter-image.jpg">
  
  <!-- Favicon -->
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
</head>
```

### 2. Structured Data (Schema.org)

```html
<!-- Organization -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Nama Perusahaan",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://facebook.com/company",
    "https://twitter.com/company",
    "https://instagram.com/company"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+62-21-1234567",
    "contactType": "customer service"
  }
}
</script>

<!-- Article/Blog Post -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Judul Artikel yang Menarik",
  "description": "Deskripsi artikel 150-160 karakter",
  "image": "https://example.com/images/article.jpg",
  "author": {
    "@type": "Person",
    "name": "Nama Penulis"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Nama Website",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-15",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/artikel"
  }
}
</script>

<!-- Product (for E-commerce) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Nama Produk",
  "image": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
  "description": "Deskripsi produk lengkap",
  "sku": "SKU-12345",
  "brand": {
    "@type": "Brand",
    "name": "Nama Merek"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "IDR",
    "price": "299000",
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "Nama Toko"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "128"
  }
}
</script>

<!-- FAQ -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Apa itu SEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO adalah singkatan dari Search Engine Optimization, yaitu proses mengoptimalkan website agar dapat ditemukan di mesin pencari."
      }
    },
    {
      "@type": "Question", 
      "name": "Bagaimana cara belajar SEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Anda dapat belajar SEO melalui kursus online, blog SEO, dan praktik langsung pada website Anda."
      }
    }
  ]
}
</script>

<!-- Local Business -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Nama Bisnis",
  "image": "https://example.com/store.jpg",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Jl. Jalan No. 123",
    "addressLocality": "Jakarta",
    "addressRegion": "DKI Jakarta",
    "postalCode": "12345",
    "addressCountry": "ID"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "-6.200000",
    "longitude": "106.816666"
  },
  "telephone": "+62-21-1234567",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ]
}
</script>
```

### 3. Technical SEO

```html
<!-- Sitemap Reference -->
<!-- In robots.txt -->
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: https://example.com/sitemap.xml

<!-- robots.txt for specific pages -->
User-agent: *
Allow: /
Disallow: /checkout/
Disallow: /cart/

<!-- Sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/halaman</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>

<!-- hreflang for multi-language -->
<link rel="alternate" hreflang="id" href="https://example.com/id/halaman">
<link rel="alternate" hreflang="en" href="https://example.com/en/page">
<link rel="alternate" hreflang="x-default" href="https://example.com/">
```

## Performance SEO

### Core Web Vitals Optimization

```html
<!-- Preload critical resources -->
<link rel="preload" href="/fonts/main-font.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/css/critical.css" as="style">

<!-- Preconnect to external domains -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://www.google-analytics.com">

<!-- Lazy load images -->
<img src="image.jpg" loading="lazy" alt="Description" width="800" height="600">

<!-- Async CSS -->
<link rel="preload" href="/css/non-critical.css" as="style" 
      onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="/css/non-critical.css"></noscript>
```

## Indonesian SEO Keywords

### Common Search Patterns

```javascript
// Indonesian keyword research
const indonesianKeywords = {
  // Products
  "jual": "jual [produk]",
  "harga": "harga [produk] 2024",
  "promo": "promo [produk] [bulan]",
  
  // Local
  "dekat": "[produk] dekat saya",
  " Jakarta": "[produk] Jakarta",
  " Surabaya": "[produk] Surabaya",
  " Bandung": "[produk] Bandung",
  
  // Transactional
  " order": "order [produk]",
  " pesan": "pesan [produk] online",
  " beli": "beli [produk] murah",
  
  // Informational
  " apa itu": "apa itu [topik]",
  " cara": "cara [aktivitas]",
  " manfaat": "manfaat [produk/topik]",
  " review": "review [produk]",
  " tutorial": "tutorial [topik]"
};

// Indonesian long-tail keywords
const longTailKeywords = [
  "jual laptop gaming murah jakarta 2024",
  "harga iphone 15 pro max terbaru desember",
  "cara daftar google bisnis untuk pemula",
  "tokopedia vs shopee mana lebih murah",
  "jasa pembuatan website perusahaan jakarta"
];
```

### SEO Checklist

- [ ] Title tag optimal (50-60 karakter)
- [ ] Meta description (150-160 karakter)
- [ ] Heading hierarchy (H1, H2, H3)
- [ ] Image alt text
- [ ] Internal linking
- [ ] External linking
- [ ] Schema markup
- [ ] Mobile responsive
- [ ] Page speed < 3 detik
- [ ] HTTPS enabled
- [ ] XML sitemap
- [ ] Robots.txt
- [ ] Canonical tags
- [ ] hreflang (if multi-language)
