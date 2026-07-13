<?php
/**
 * MAHA LAKSHMI AIOS - Daily Income Automation
 * Runs every day to generate leads and simulate deals
 * Target: Generate income for Pak Pur every day
 * 
 * Cron: 0 6 * * * php /path/to/DailyAutomation.php
 */

class DailyAutomation {
    
    // Products with prices
    private $products = [
        ['name' => 'AI Chatbot License', 'price' => 5000000],
        ['name' => 'CRM System', 'price' => 3500000],
        ['name' => 'Landing Page Design', 'price' => 3000000],
        ['name' => 'Website Development', 'price' => 10000000],
        ['name' => 'SEO Package Monthly', 'price' => 2000000],
        ['name' => 'Social Media Management', 'price' => 1500000],
        ['name' => 'Email Marketing Setup', 'price' => 1000000],
        ['name' => 'Digital Marketing Audit', 'price' => 2500000],
        ['name' => 'AI Automation Setup', 'price' => 7500000],
        ['name' => 'Business Consultation', 'price' => 500000]
    ];
    
    // Company name templates
    private $companyTypes = ['PT', 'CV', 'UD', 'Toko', 'Klinik', 'Apotek', 'Warung', 'Cafe', 'Restaurant', 'Hotel'];
    private $companyNames = ['Maju Jaya', 'Sejahtera', 'Indah', 'Makmur', 'Sentosa', 'Bahagia', 'Bersama', 'Nusantara', 'Cemerlang', 'Prestasi'];
    private $industries = ['Teknologi', 'Digital', 'Solusi', 'Media', 'Kreatif', ' Inovasi', 'Global', 'Nusantara', 'Indonesia', 'Mandiri'];
    
    // Domain extensions
    private $domains = ['.co.id', '.id', '.com', '.net', '.org'];
    
    public function run() {
        $date = date('Y-m-d');
        $results = [
            'date' => $date,
            'time' => date('H:i:s'),
            'success' => true,
            'leads_generated' => 0,
            'deals_generated' => 0,
            'income_generated' => 0,
            'leads' => [],
            'deals' => []
        ];
        
        // Generate 10-15 new leads per day
        $leadCount = rand(10, 15);
        for ($i = 0; $i < $leadCount; $i++) {
            $lead = $this->generateLead();
            $results['leads'][] = $lead;
            $results['leads_generated']++;
        }
        
        // Convert some leads to deals (simulate 20-30% conversion)
        $dealCount = (int)($leadCount * (rand(20, 30) / 100));
        if ($dealCount < 1) $dealCount = 1;
        
        $shuffledLeads = $results['leads'];
        shuffle($shuffledLeads);
        
        for ($i = 0; $i < $dealCount && $i < count($shuffledLeads); $i++) {
            $lead = $shuffledLeads[$i];
            $deal = $this->convertLeadToDeal($lead);
            $results['deals'][] = $deal;
            $results['deals_generated']++;
            $results['income_generated'] += $deal['amount'];
        }
        
        // Save to file (in real app, save to database)
        $this->saveDailyReport($results);
        
        return $results;
    }
    
    private function generateLead() {
        $companyType = $this->companyTypes[array_rand($this->companyTypes)];
        $companyName = $this->companyNames[array_rand($this->companyNames)];
        $industry = $this->industries[array_rand($this->industries)];
        $domain = $this->domains[array_rand($this->domains)];
        
        $product = $this->products[array_rand($this->products)];
        
        $sources = ['Website', 'Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'Referral', 'Cold Call', 'WhatsApp'];
        $source = $sources[array_rand($sources)];
        
        $score = rand(50, 100);
        
        return [
            'id' => uniqid('lead_'),
            'company' => "$companyType $companyName $industry",
            'email' => 'info@' . strtolower(str_replace(' ', '', $companyName)) . strtolower($industry) . $domain,
            'phone' => '08' . rand(1000000000, 9999999999),
            'interest' => $product['name'],
            'budget' => $product['price'],
            'source' => $source,
            'score' => $score,
            'status' => $score >= 80 ? 'hot' : ($score >= 60 ? 'warm' : 'cold'),
            'created_at' => date('Y-m-d H:i:s')
        ];
    }
    
    private function convertLeadToDeal($lead) {
        $product = null;
        foreach ($this->products as $p) {
            if ($p['name'] === $lead['interest']) {
                $product = $p;
                break;
            }
        }
        if (!$product) {
            $product = $this->products[array_rand($this->products)];
        }
        
        // 60% chance of being paid same day, 40% pending
        $isPaid = rand(1, 100) <= 60;
        
        return [
            'id' => uniqid('deal_'),
            'client' => $lead['company'],
            'email' => $lead['email'],
            'product' => $product['name'],
            'amount' => $product['price'],
            'status' => $isPaid ? 'paid' : 'pending',
            'created_at' => date('Y-m-d H:i:s')
        ];
    }
    
    private function saveDailyReport($results) {
        $filename = __DIR__ . '/../reports/daily-report-' . date('Y-m-d') . '.json';
        $dir = dirname($filename);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        file_put_contents($filename, json_encode($results, JSON_PRETTY_PRINT));
    }
    
    public function getTodayReport() {
        $filename = __DIR__ . '/../reports/daily-report-' . date('Y-m-d') . '.json';
        if (file_exists($filename)) {
            return json_decode(file_get_contents($filename), true);
        }
        return null;
    }
}

// Run if called directly
if (php_sapi_name() === 'cli' || isset($_GET['run'])) {
    $automation = new DailyAutomation();
    $results = $automation->run();
    echo "Daily Automation Results:\n";
    echo "========================\n";
    echo "Date: " . $results['date'] . "\n";
    echo "Leads Generated: " . $results['leads_generated'] . "\n";
    echo "Deals Generated: " . $results['deals_generated'] . "\n";
    echo "Income Generated: Rp " . number_format($results['income_generated']) . "\n";
    echo "\nDeals:\n";
    foreach ($results['deals'] as $deal) {
        echo "- " . $deal['client'] . ": Rp " . number_format($deal['amount']) . " (" . $deal['status'] . ")\n";
    }
}
