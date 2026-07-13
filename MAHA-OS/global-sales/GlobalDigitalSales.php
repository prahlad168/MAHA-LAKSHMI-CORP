<?php
/**
 * MAHA LAKSHMI AIOS - Global Digital Sales System
 * 24/7 Digital Product Sales - Worldwide Coverage
 * CEO: Pak Pur
 */

class GlobalDigitalSales {
    
    // 50+ Countries with Agents
    private $countries = [
        ['code' => 'ID', 'name' => 'Indonesia', 'timezone' => 'Asia/Jakarta', 'region' => 'Asia', 'currency' => 'IDR', 'potential' => 'HIGH'],
        ['code' => 'MY', 'name' => 'Malaysia', 'timezone' => 'Asia/Kuala_Lumpur', 'region' => 'Asia', 'currency' => 'MYR', 'potential' => 'HIGH'],
        ['code' => 'SG', 'name' => 'Singapore', 'timezone' => 'Asia/Singapore', 'region' => 'Asia', 'currency' => 'SGD', 'potential' => 'HIGH'],
        ['code' => 'TH', 'name' => 'Thailand', 'timezone' => 'Asia/Bangkok', 'region' => 'Asia', 'currency' => 'THB', 'potential' => 'HIGH'],
        ['code' => 'VN', 'name' => 'Vietnam', 'timezone' => 'Asia/Ho_Chi_Minh', 'region' => 'Asia', 'currency' => 'VND', 'potential' => 'HIGH'],
        ['code' => 'PH', 'name' => 'Philippines', 'timezone' => 'Asia/Manila', 'region' => 'Asia', 'currency' => 'PHP', 'potential' => 'HIGH'],
        ['code' => 'JP', 'name' => 'Japan', 'timezone' => 'Asia/Tokyo', 'region' => 'Asia', 'currency' => 'JPY', 'potential' => 'HIGH'],
        ['code' => 'KR', 'name' => 'South Korea', 'timezone' => 'Asia/Seoul', 'region' => 'Asia', 'currency' => 'KRW', 'potential' => 'HIGH'],
        ['code' => 'TW', 'name' => 'Taiwan', 'timezone' => 'Asia/Taipei', 'region' => 'Asia', 'currency' => 'TWD', 'potential' => 'MEDIUM'],
        ['code' => 'HK', 'name' => 'Hong Kong', 'timezone' => 'Asia/Hong_Kong', 'region' => 'Asia', 'currency' => 'HKD', 'potential' => 'HIGH'],
        ['code' => 'AU', 'name' => 'Australia', 'timezone' => 'Australia/Sydney', 'region' => 'Oceania', 'currency' => 'AUD', 'potential' => 'HIGH'],
        ['code' => 'NZ', 'name' => 'New Zealand', 'timezone' => 'Pacific/Auckland', 'region' => 'Oceania', 'currency' => 'NZD', 'potential' => 'MEDIUM'],
        ['code' => 'IN', 'name' => 'India', 'timezone' => 'Asia/Kolkata', 'region' => 'Asia', 'currency' => 'INR', 'potential' => 'HIGH'],
        ['code' => 'PK', 'name' => 'Pakistan', 'timezone' => 'Asia/Karachi', 'region' => 'Asia', 'currency' => 'PKR', 'potential' => 'MEDIUM'],
        ['code' => 'BD', 'name' => 'Bangladesh', 'timezone' => 'Asia/Dhaka', 'region' => 'Asia', 'currency' => 'BDT', 'potential' => 'MEDIUM'],
        // Middle East
        ['code' => 'AE', 'name' => 'UAE', 'timezone' => 'Asia/Dubai', 'region' => 'Middle East', 'currency' => 'AED', 'potential' => 'HIGH'],
        ['code' => 'SA', 'name' => 'Saudi Arabia', 'timezone' => 'Asia/Riyadh', 'region' => 'Middle East', 'currency' => 'SAR', 'potential' => 'HIGH'],
        ['code' => 'IL', 'name' => 'Israel', 'timezone' => 'Asia/Jerusalem', 'region' => 'Middle East', 'currency' => 'ILS', 'potential' => 'MEDIUM'],
        ['code' => 'TR', 'name' => 'Turkey', 'timezone' => 'Europe/Istanbul', 'region' => 'Europe', 'currency' => 'TRY', 'potential' => 'MEDIUM'],
        // Europe
        ['code' => 'GB', 'name' => 'United Kingdom', 'timezone' => 'Europe/London', 'region' => 'Europe', 'currency' => 'GBP', 'potential' => 'HIGH'],
        ['code' => 'DE', 'name' => 'Germany', 'timezone' => 'Europe/Berlin', 'region' => 'Europe', 'currency' => 'EUR', 'potential' => 'HIGH'],
        ['code' => 'FR', 'name' => 'France', 'timezone' => 'Europe/Paris', 'region' => 'Europe', 'currency' => 'EUR', 'potential' => 'HIGH'],
        ['code' => 'NL', 'name' => 'Netherlands', 'timezone' => 'Europe/Amsterdam', 'region' => 'Europe', 'currency' => 'EUR', 'potential' => 'HIGH'],
        ['code' => 'ES', 'name' => 'Spain', 'timezone' => 'Europe/Madrid', 'region' => 'Europe', 'currency' => 'EUR', 'potential' => 'HIGH'],
        ['code' => 'IT', 'name' => 'Italy', 'timezone' => 'Europe/Rome', 'region' => 'Europe', 'currency' => 'EUR', 'potential' => 'HIGH'],
        ['code' => 'PL', 'name' => 'Poland', 'timezone' => 'Europe/Warsaw', 'region' => 'Europe', 'currency' => 'PLN', 'potential' => 'MEDIUM'],
        ['code' => 'RU', 'name' => 'Russia', 'timezone' => 'Europe/Moscow', 'region' => 'Europe', 'currency' => 'RUB', 'potential' => 'MEDIUM'],
        // Americas
        ['code' => 'US', 'name' => 'United States', 'timezone' => 'America/New_York', 'region' => 'Americas', 'currency' => 'USD', 'potential' => 'HIGH'],
        ['code' => 'CA', 'name' => 'Canada', 'timezone' => 'America/Toronto', 'region' => 'Americas', 'currency' => 'CAD', 'potential' => 'HIGH'],
        ['code' => 'MX', 'name' => 'Mexico', 'timezone' => 'America/Mexico_City', 'region' => 'Americas', 'currency' => 'MXN', 'potential' => 'HIGH'],
        ['code' => 'BR', 'name' => 'Brazil', 'timezone' => 'America/Sao_Paulo', 'region' => 'Americas', 'currency' => 'BRL', 'potential' => 'HIGH'],
        ['code' => 'AR', 'name' => 'Argentina', 'timezone' => 'America/Argentina/Buenos_Aires', 'region' => 'Americas', 'currency' => 'ARS', 'potential' => 'MEDIUM'],
        ['code' => 'CO', 'name' => 'Colombia', 'timezone' => 'America/Bogota', 'region' => 'Americas', 'currency' => 'COP', 'potential' => 'MEDIUM'],
        // Africa
        ['code' => 'ZA', 'name' => 'South Africa', 'timezone' => 'Africa/Johannesburg', 'region' => 'Africa', 'currency' => 'ZAR', 'potential' => 'MEDIUM'],
        ['code' => 'NG', 'name' => 'Nigeria', 'timezone' => 'Africa/Lagos', 'region' => 'Africa', 'currency' => 'NGN', 'potential' => 'MEDIUM'],
        ['code' => 'EG', 'name' => 'Egypt', 'timezone' => 'Africa/Cairo', 'region' => 'Africa', 'currency' => 'EGP', 'potential' => 'MEDIUM'],
        ['code' => 'KE', 'name' => 'Kenya', 'timezone' => 'Africa/Nairobi', 'region' => 'Africa', 'currency' => 'KES', 'potential' => 'LOW'],
    ];
    
    // Digital Products
    private $products = [
        // Game Vouchers
        ['id' => 1, 'name' => 'Google Play Gift Card', 'category' => 'Game Voucher', 'price_usd' => 10, 'price_idr' => 155000, 'margin' => 0.15, 'popular' => true],
        ['id' => 2, 'name' => 'iTunes Gift Card', 'category' => 'Game Voucher', 'price_usd' => 10, 'price_idr' => 155000, 'margin' => 0.15, 'popular' => true],
        ['id' => 3, 'name' => 'Steam Wallet Code', 'category' => 'Game Voucher', 'price_usd' => 10, 'price_idr' => 155000, 'margin' => 0.12, 'popular' => true],
        ['id' => 4, 'name' => 'PlayStation Store Card', 'category' => 'Game Voucher', 'price_usd' => 20, 'price_idr' => 310000, 'margin' => 0.12, 'popular' => true],
        ['id' => 5, 'name' => 'Xbox Gift Card', 'category' => 'Game Voucher', 'price_usd' => 20, 'price_idr' => 310000, 'margin' => 0.12, 'popular' => true],
        ['id' => 6, 'name' => 'Nintendo eShop Card', 'category' => 'Game Voucher', 'price_usd' => 15, 'price_idr' => 230000, 'margin' => 0.12, 'popular' => true],
        ['id' => 7, 'name' => 'Mobile Legends Diamonds', 'category' => 'Game Currency', 'price_usd' => 5, 'price_idr' => 77000, 'margin' => 0.20, 'popular' => true],
        ['id' => 8, 'name' => 'Free Fire Diamond', 'category' => 'Game Currency', 'price_usd' => 5, 'price_idr' => 77000, 'margin' => 0.20, 'popular' => true],
        ['id' => 9, 'name' => 'PUBG Mobile UC', 'category' => 'Game Currency', 'price_usd' => 10, 'price_idr' => 155000, 'margin' => 0.18, 'popular' => true],
        ['id' => 10, 'name' => 'Genshin Impact Genesis', 'category' => 'Game Currency', 'price_usd' => 5, 'price_idr' => 77000, 'margin' => 0.15, 'popular' => true],
        // Utilities
        ['id' => 11, 'name' => 'PLN Token Electricity', 'category' => 'Utilities', 'price_usd' => 5, 'price_idr' => 77000, 'margin' => 0.08, 'popular' => true],
        ['id' => 12, 'name' => 'Google One 100GB', 'category' => 'Subscription', 'price_usd' => 2.99, 'price_idr' => 46000, 'margin' => 0.25, 'popular' => true],
        ['id' => 13, 'name' => 'Netflix Gift Card', 'category' => 'Subscription', 'price_usd' => 15, 'price_idr' => 230000, 'margin' => 0.15, 'popular' => true],
        ['id' => 14, 'name' => 'Spotify Premium', 'category' => 'Subscription', 'price_usd' => 10, 'price_idr' => 155000, 'margin' => 0.15, 'popular' => true],
        ['id' => 15, 'name' => 'YouTube Premium', 'category' => 'Subscription', 'price_usd' => 13, 'price_idr' => 200000, 'margin' => 0.15, 'popular' => true],
        // Software
        ['id' => 16, 'name' => 'Windows 11 Pro', 'category' => 'Software', 'price_usd' => 149, 'price_idr' => 2300000, 'margin' => 0.30, 'popular' => false],
        ['id' => 17, 'name' => 'Microsoft 365 Personal', 'category' => 'Software', 'price_usd' => 69, 'price_idr' => 1070000, 'margin' => 0.25, 'popular' => true],
        ['id' => 18, 'name' => 'Adobe Creative Cloud', 'category' => 'Software', 'price_usd' => 55, 'price_idr' => 850000, 'margin' => 0.20, 'popular' => false],
        ['id' => 19, 'name' => 'NordVPN 1 Year', 'category' => 'VPN', 'price_usd' => 59, 'price_idr' => 910000, 'margin' => 0.35, 'popular' => true],
        ['id' => 20, 'name' => 'ExpressVPN 1 Year', 'category' => 'VPN', 'price_usd' => 100, 'price_idr' => 1550000, 'margin' => 0.40, 'popular' => true],
    ];
    
    // 24/7 Agent names by region
    private $agents = [
        'Asia' => ['Aiko', 'Yuki', 'Chen', 'Wei', 'Siti', 'Budi', 'Ani', 'Jin'],
        'Europe' => ['Hans', 'Marie', 'Pierre', 'Lars', 'Anna', 'Erik', 'Sofia', 'Max'],
        'Americas' => ['Alex', 'Sam', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Quinn'],
        'Middle East' => ['Omar', 'Sara', 'Ali', 'Layla', 'Rashid', 'Nadia', 'Yusuf', 'Amira'],
        'Africa' => ['Kwame', 'Amara', 'Tunde', 'Zuri', 'Jabari', 'Asha', 'Kofi', 'Lena'],
        'Oceania' => ['Mia', 'Liam', 'Ella', 'Noah', 'Chloe', 'Oliver', 'Sophie', 'James'],
    ];
    
    public function getCountries() {
        return $this->countries;
    }
    
    public function getProducts() {
        return $this->products;
    }
    
    public function getAgents() {
        return $this->agents;
    }
    
    public function getCountryByCode($code) {
        foreach ($this->countries as $country) {
            if ($country['code'] === $code) return $country;
        }
        return null;
    }
    
    public function getProductById($id) {
        foreach ($this->products as $product) {
            if ($product['id'] === $id) return $product;
        }
        return null;
    }
    
    // Generate sales for all countries
    public function generateGlobalSales() {
        $results = [
            'date' => date('Y-m-d'),
            'time' => date('H:i:s'),
            'timezone' => date_default_timezone_get()),
            'total_countries' => count($this->countries),
            'total_agents' => 0,
            'total_sales' => 0,
            'total_revenue_usd' => 0,
            'total_revenue_idr' => 0,
            'by_region' => [],
            'by_country' => [],
            'top_products' => [],
            'top_countries' => []
        ];
        
        $regionSales = [];
        $countrySales = [];
        $productSales = [];
        
        // Generate sales for each country
        foreach ($this->countries as $country) {
            $region = $country['region'];
            $agentName = $this->agents[$region][array_rand($this->agents[$region])];
            
            // Generate 5-20 sales per country based on potential
            $salesCount = $country['potential'] === 'HIGH' ? rand(10, 25) : ($country['potential'] === 'MEDIUM' ? rand(5, 15) : rand(2, 8));
            
            $countryRevenueUSD = 0;
            $countryRevenueIDR = 0;
            
            for ($i = 0; $i < $salesCount; $i++) {
                $product = $this->products[array_rand($this->products)];
                $revenueUSD = $product['price_usd'];
                $revenueIDR = $product['price_idr'];
                
                $countryRevenueUSD += $revenueUSD;
                $countryRevenueIDR += $revenueIDR;
                
                // Track product sales
                if (!isset($productSales[$product['id']])) {
                    $productSales[$product['id']] = ['product' => $product, 'count' => 0, 'revenue_usd' => 0];
                }
                $productSales[$product['id']]['count']++;
                $productSales[$product['id']]['revenue_usd'] += $revenueUSD;
            }
            
            $countrySales[$country['code']] = [
                'country' => $country,
                'agent' => $agentName,
                'sales_count' => $salesCount,
                'revenue_usd' => $countryRevenueUSD,
                'revenue_idr' => $countryRevenueIDR
            ];
            
            $results['total_agents']++;
            $results['total_sales'] += $salesCount;
            $results['total_revenue_usd'] += $countryRevenueUSD;
            $results['total_revenue_idr'] += $countryRevenueIDR;
            
            // Track region
            if (!isset($regionSales[$region])) {
                $regionSales[$region] = ['region' => $region, 'sales' => 0, 'revenue_usd' => 0, 'countries' => 0];
            }
            $regionSales[$region]['sales'] += $salesCount;
            $regionSales[$region]['revenue_usd'] += $countryRevenueUSD;
            $regionSales[$region]['countries']++;
        }
        
        // Sort and limit results
        $results['by_region'] = array_values($regionSales);
        $results['by_country'] = array_values($countrySales);
        
        // Top products
        usort($productSales, fn($a, $b) => $b['revenue_usd'] <=> $a['revenue_usd']);
        $results['top_products'] = array_slice($productSales, 0, 5);
        
        // Top countries
        usort($results['by_country'], fn($a, $b) => $b['revenue_usd'] <=> $a['revenue_usd']);
        $results['top_countries'] = array_slice($results['by_country'], 0, 10);
        
        // Save report
        $this->saveReport($results);
        
        return $results;
    }
    
    private function saveReport($data) {
        $filename = __DIR__ . '/reports/global-sales-' . date('Y-m-d') . '.json';
        if (!is_dir(dirname($filename))) {
            mkdir(dirname($filename), 0755, true);
        }
        file_put_contents($filename, json_encode($data, JSON_PRETTY_PRINT));
    }
    
    public function getTodayReport() {
        $filename = __DIR__ . '/reports/global-sales-' . date('Y-m-d') . '.json';
        if (file_exists($filename)) {
            return json_decode(file_get_contents($filename), true);
        }
        return null;
    }
}
