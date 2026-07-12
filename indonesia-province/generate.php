<?php
/**
 * Province Landing Page Generator
 * Generates 190 landing pages (38 provinces × 5 units)
 * 
 * Usage: php generate.php
 */

// 38 Provinces of Indonesia
$provinces = [
    ['name' => 'Aceh', 'code' => 'aceh', 'region' => 'Sumatera'],
    ['name' => 'Sumatera Utara', 'code' => 'sumut', 'region' => 'Sumatera'],
    ['name' => 'Sumatera Barat', 'code' => 'sumbar', 'region' => 'Sumatera'],
    ['name' => 'Riau', 'code' => 'riau', 'region' => 'Sumatera'],
    ['name' => 'Jambi', 'code' => 'jambi', 'region' => 'Sumatera'],
    ['name' => 'Sumatera Selatan', 'code' => 'sumsel', 'region' => 'Sumatera'],
    ['name' => 'Bengkulu', 'code' => 'bengkulu', 'region' => 'Sumatera'],
    ['name' => 'Lampung', 'code' => 'lampung', 'region' => 'Sumatera'],
    ['name' => 'DKI Jakarta', 'code' => 'jakarta', 'region' => 'Jawa'],
    ['name' => 'Jawa Barat', 'code' => 'jabar', 'region' => 'Jawa'],
    ['name' => 'Jawa Tengah', 'code' => 'jateng', 'region' => 'Jawa'],
    ['name' => 'DI Yogyakarta', 'code' => 'yogyakarta', 'region' => 'Jawa'],
    ['name' => 'Jawa Timur', 'code' => 'jatim', 'region' => 'Jawa'],
    ['name' => 'Banten', 'code' => 'banten', 'region' => 'Jawa'],
    ['name' => 'Bali', 'code' => 'bali', 'region' => 'Bali-Nusra'],
    ['name' => 'Nusa Tenggara Barat', 'code' => 'ntb', 'region' => 'Bali-Nusra'],
    ['name' => 'Nusa Tenggara Timur', 'code' => 'ntt', 'region' => 'Bali-Nusra'],
    ['name' => 'Kalimantan Barat', 'code' => 'kalbar', 'region' => 'Kalimantan'],
    ['name' => 'Kalimantan Tengah', 'code' => 'kalteng', 'region' => 'Kalimantan'],
    ['name' => 'Kalimantan Selatan', 'code' => 'kalsel', 'region' => 'Kalimantan'],
    ['name' => 'Kalimantan Timur', 'code' => 'kaltim', 'region' => 'Kalimantan'],
    ['name' => 'Kalimantan Utara', 'code' => 'kalut', 'region' => 'Kalimantan'],
    ['name' => 'Sulawesi Utara', 'code' => 'sulut', 'region' => 'Sulawesi'],
    ['name' => 'Sulawesi Tengah', 'code' => 'sulteng', 'region' => 'Sulawesi'],
    ['name' => 'Sulawesi Selatan', 'code' => 'sulsel', 'region' => 'Sulawesi'],
    ['name' => 'Sulawesi Tenggara', 'code' => 'sultra', 'region' => 'Sulawesi'],
    ['name' => 'Gorontalo', 'code' => 'gorontalo', 'region' => 'Sulawesi'],
    ['name' => 'Sulawesi Barat', 'code' => 'sulbar', 'region' => 'Sulawesi'],
    ['name' => 'Maluku', 'code' => 'maluku', 'region' => 'Maluku-Papua'],
    ['name' => 'Maluku Utara', 'code' => 'malut', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua', 'code' => 'papua', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Barat', 'code' => 'papbar', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Tengah', 'code' => 'papteng', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Pegunungan', 'code' => 'pappg', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Barat Daya', 'code' => 'papbar-daya', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Selatan', 'code' => 'papsel', 'region' => 'Maluku-Papua'],
    ['name' => 'Papua Jaya Wijaya', 'code' => 'papjwi', 'region' => 'Maluku-Papua'],
];

// Unit businesses configuration
$units = [
    'digimart' => [
        'title' => 'DigiMart',
        'subtitle' => 'Toko Produk Digital',
        'products' => ['Voucher Game', 'Token Listrik', 'Pulsa', 'Paket Data', 'Software'],
        'colors' => ['#6366f1', '#10b981'],
        'emoji' => '🎮'
    ],
    'linkshort' => [
        'title' => 'LinkShort Pro',
        'subtitle' => 'Shorten Links & Earn',
        'products' => ['URL Shortener', 'Monetisasi Link', 'CPM Tinggi'],
        'colors' => ['#8b5cf6', '#10b981'],
        'emoji' => '🔗'
    ],
    'airdrop' => [
        'title' => 'AirdropHunter',
        'subtitle' => 'Crypto Airdrop Hunter',
        'products' => ['Auto Track', 'Auto Claim', 'Portfolio Tracker'],
        'colors' => ['#f59e0b', '#10b981'],
        'emoji' => '🪂'
    ],
    'microtask' => [
        'title' => 'MicroTask Pro',
        'subtitle' => 'Earn from Micro Tasks',
        'products' => ['Survei', 'Review', 'Data Entry', 'App Testing'],
        'colors' => ['#22c55e', '#3b82f6'],
        'emoji' => '💰'
    ],
    'survey' => [
        'title' => 'SurveyPro',
        'subtitle' => 'Survei Berbayar',
        'products' => ['Buat Survei', 'Ikuti Survei', 'Dapat Bayaran'],
        'colors' => ['#ec4899', '#8b5cf6'],
        'emoji' => '📊'
    ]
];

function generateLandingPage($province, $unit) {
    $provinceName = $province['name'];
    $provinceCode = $province['code'];
    $region = $province['region'];
    $unitKey = $unit['title'];
    $subtitle = $unit['subtitle'];
    $products = $unit['products'];
    $colors = $unit['colors'];
    $emoji = $unit['emoji'];
    $primary = $colors[0];
    $secondary = $colors[1];
    
    return <<<HTML
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$emoji} {$unitKey} {$provinceName} - {$subtitle}</title>
    <meta name="description" content="{$unitKey} {$provinceName}. {$subtitle}. Voucher game, token listrik, pulsa, dan produk digital lainnya. Pengiriman instan 24/7.">
    <meta name="keywords" content="{$provinceName}, {$unitKey}, voucher game {$provinceName}, token listrik {$provinceName}, pulsa {$provinceName}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: {$primary};
            --primary-dark: color-mix(in srgb, {$primary} 80%, black);
            --secondary: {$secondary};
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        header {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            padding: 15px 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 1.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, {$primary}, {$secondary});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .province-badge {
            background: rgba(255,255,255,0.1);
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 0.85rem;
        }
        .btn {
            background: {$primary};
            color: white;
            padding: 12px 25px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            transition: 0.3s;
            border: none;
            cursor: pointer;
            display: inline-block;
        }
        .btn:hover { background: var(--primary-dark); }
        
        .hero {
            padding: 120px 0 60px;
            text-align: center;
            background: radial-gradient(ellipse at top, rgba(99,102,241,0.15) 0%, transparent 60%);
        }
        .hero h1 {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 15px;
        }
        .hero h1 span {
            background: linear-gradient(135deg, {$primary}, {$secondary});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero .province-highlight {
            display: inline-block;
            background: var(--bg-card);
            padding: 10px 25px;
            border-radius: 50px;
            font-size: 1.1rem;
            margin-bottom: 20px;
            border: 2px solid {$primary};
        }
        .hero p {
            font-size: 1.1rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto 30px;
        }
        
        .region-bar {
            background: var(--bg-card);
            padding: 15px 0;
            text-align: center;
            margin-bottom: 30px;
        }
        .region-bar span {
            background: {$primary};
            padding: 5px 20px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .products {
            padding: 60px 0;
        }
        .section-title {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 40px;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }
        .product-card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
            transition: 0.3s;
        }
        .product-card:hover {
            transform: translateY(-5px);
            border-color: {$primary};
        }
        .product-icon { font-size: 2.5rem; margin-bottom: 15px; }
        .product-card h3 { margin-bottom: 8px; font-size: 1.1rem; }
        .product-card p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 10px; }
        .product-price { color: var(--secondary); font-weight: 700; font-size: 1.1rem; }
        
        .features {
            padding: 60px 0;
            background: rgba(30,41,59,0.3);
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .feature-card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .feature-icon { font-size: 2rem; margin-bottom: 15px; }
        .feature-card h3 { margin-bottom: 8px; }
        .feature-card p { color: var(--text-muted); font-size: 0.9rem; }
        
        .stats {
            padding: 40px 0;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            text-align: center;
        }
        .stat-item { padding: 20px; }
        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            color: {$primary};
        }
        .stat-label { color: var(--text-muted); font-size: 0.9rem; }
        
        .contact {
            padding: 60px 0;
        }
        .contact-box {
            background: var(--bg-card);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            max-width: 600px;
            margin: 0 auto;
        }
        .contact-box h2 { margin-bottom: 20px; }
        .contact-box p { color: var(--text-muted); margin-bottom: 25px; }
        .contact-icons {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .contact-icon {
            background: rgba(255,255,255,0.1);
            padding: 15px 25px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: 0.3s;
        }
        .contact-icon:hover { background: {$primary}; }
        .contact-icon span { font-size: 0.9rem; }
        
        footer {
            background: var(--bg-card);
            padding: 30px 0;
            text-align: center;
            margin-top: 60px;
        }
        footer p { color: var(--text-muted); font-size: 0.9rem; }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .header-inner { flex-direction: column; gap: 10px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-inner">
            <div class="logo">{$emoji} {$unitKey}</div>
            <div class="province-badge">📍 {$provinceName}</div>
        </div>
    </header>
    
    <section class="hero">
        <div class="container">
            <div class="province-highlight">📍 Melayani Seluruh {$provinceName}</div>
            <h1>{$emoji} {$unitKey} <span>{$provinceName}</span></h1>
            <p>{$subtitle}. Tersedia 24/7 dengan pengiriman instan untuk seluruh {$provinceName}.</p>
            <a href="#products" class="btn">Lihat Produk →</a>
        </div>
    </section>
    
    <div class="region-bar">
        <div class="container">
            <span>🏠 Region: {$region}</span>
        </div>
    </div>
    
    <section class="products" id="products">
        <div class="container">
            <h2 class="section-title">Produk & Layanan di {$provinceName}</h2>
            <div class="product-grid">
HTML;

    // Add products
    $productIcons = ['🎮', '⚡', '📱', '💻', '🎁', '🔗', '🪂', '💰', '📊'];
    foreach($products as $i => $product) {
        $price = rand(5, 50);
        $html .= <<<HTML
                <div class="product-card">
                    <div class="product-icon">{$productIcons[$i % count($productIcons)]}</div>
                    <h3>{$product}</h3>
                    <p>Untuk {$provinceName}</p>
                    <div class="product-price">Mulai Rp {$price}.000</div>
                </div>
HTML;
    }

    $html .= <<<HTML
            </div>
        </div>
    </section>
    
    <section class="features">
        <div class="container">
            <h2 class="section-title">Kenapa Pilih Kami di {$provinceName}?</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3>Pengiriman Instan</h3>
                    <p>Kode langsung dikirim dalam 5-30 menit setelah pembayaran</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>100% Aman</h3>
                    <p>Transaksi aman dengan enkripsi 256-bit</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3>Support 24/7</h3>
                    <p>Tim kami siap membantu kapan saja di {$provinceName}</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">✅</div>
                    <h3>Garansi</h3>
                    <p>Garansi 100% atau refund jika ada masalah</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="stats">
        <div class="container">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">100K+</div>
                    <div class="stat-label">Transaksi di Indonesia</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">38</div>
                    <div class="stat-label">Provinsi Coverage</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">99.9%</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">4.9/5</div>
                    <div class="stat-label">Rating Customer</div>
                </div>
            </div>
        </div>
    </section>
    
    <section class="contact">
        <div class="container">
            <div class="contact-box">
                <h2>Hubungi Kami di {$provinceName}</h2>
                <p>Tersedia untuk seluruh wilayah {$provinceName}. Hubungi kami sekarang!</p>
                <div class="contact-icons">
                    <a href="#" class="contact-icon">
                        <span>💬</span>
                        <span>WhatsApp</span>
                    </a>
                    <a href="#" class="contact-icon">
                        <span>📱</span>
                        <span>Telegram</span>
                    </a>
                    <a href="#" class="contact-icon">
                        <span>📧</span>
                        <span>Email</span>
                    </a>
                </div>
            </div>
        </div>
    </section>
    
    <footer>
        <div class="container">
            <p>&copy; 2024 {$unitKey} Indonesia. All rights reserved.</p>
            <p style="margin-top: 10px;">🏦 BCA 6485086645 | An: i Made Purna Ananda</p>
        </div>
    </footer>
</body>
</html>
HTML;
    
    return $html;
}

// Generate all pages
$totalGenerated = 0;
$baseDir = __DIR__;

foreach($units as $unitKey => $unit) {
    $unitDir = $baseDir . '/' . $unitKey;
    if (!is_dir($unitDir)) {
        mkdir($unitDir, 0755, true);
    }
    
    foreach($provinces as $province) {
        $filename = $unitDir . '/' . $province['code'] . '.html';
        $content = generateLandingPage($province, $unit);
        file_put_contents($filename, $content);
        $totalGenerated++;
        
        echo "[$totalGenerated] {$unit['title']} - {$province['name']}\n";
    }
}

echo "\n";
echo "═══════════════════════════════════════════\n";
echo "✅ GENERATION COMPLETE!\n";
echo "═══════════════════════════════════════════\n";
echo "Total files generated: $totalGenerated\n";
echo "Provinces: " . count($provinces) . "\n";
echo "Units: " . count($units) . "\n";
echo "\nBreakdown:\n";
foreach($units as $key => $unit) {
    echo "- {$unit['title']}: " . count($provinces) . " files\n";
}
echo "\nLocation: $baseDir/\n";
echo "═══════════════════════════════════════════\n";
