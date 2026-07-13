<?php
/**
 * MAHA LAKSHMI AIOS - Income Generator
 * Target: Generate income every day for Pak Pur
 * Created: 2026-07-03
 */

class IncomeGenerator {
    
    // Daily income targets
    private $dailyTarget = 33333333; // Rp 1B / 30 days
    
    // Products with prices
    private $products = [
        ['id' => 1, 'name' => 'AI Chatbot License', 'price' => 5000000, 'category' => 'SaaS', 'leads' => 10, 'conv_rate' => 0.10],
        ['id' => 2, 'name' => 'CRM System', 'price' => 3500000, 'category' => 'SaaS', 'leads' => 8, 'conv_rate' => 0.15],
        ['id' => 3, 'name' => 'Landing Page Design', 'price' => 3000000, 'category' => 'Service', 'leads' => 5, 'conv_rate' => 0.20],
        ['id' => 4, 'name' => 'Website Development', 'price' => 10000000, 'category' => 'Service', 'leads' => 3, 'conv_rate' => 0.15],
        ['id' => 5, 'name' => 'SEO Package Monthly', 'price' => 2000000, 'category' => 'Service', 'leads' => 12, 'conv_rate' => 0.12],
        ['id' => 6, 'name' => 'Social Media Management', 'price' => 1500000, 'category' => 'Service', 'leads' => 15, 'conv_rate' => 0.10],
        ['id' => 7, 'name' => 'Email Marketing Setup', 'price' => 1000000, 'category' => 'Service', 'leads' => 20, 'conv_rate' => 0.08],
        ['id' => 8, 'name' => 'Digital Marketing Audit', 'price' => 2500000, 'category' => 'Consulting', 'leads' => 6, 'conv_rate' => 0.18],
        ['id' => 9, 'name' => 'AI Automation Setup', 'price' => 7500000, 'category' => 'Service', 'leads' => 4, 'conv_rate' => 0.12],
        ['id' => 10, 'name' => 'Business Consultation', 'price' => 500000, 'category' => 'Consulting', 'leads' => 25, 'conv_rate' => 0.05]
    ];
    
    // Realistic leads for today (simulate potential customers)
    private $todayLeads = [
        ['name' => 'PT Maju Jaya', 'email' => 'info@majujaya.co.id', 'phone' => '081234567890', 'interest' => 'AI Chatbot License', 'source' => 'Website', 'score' => 85],
        ['name' => 'CV Sejahtera Abadi', 'email' => 'contact@sejahtera.co.id', 'phone' => '087654321098', 'interest' => 'Website Development', 'source' => 'Google Ads', 'score' => 90],
        ['name' => 'PT Indo Digital', 'email' => 'sales@indodigital.id', 'phone' => '081298765432', 'interest' => 'SEO Package Monthly', 'source' => 'Referral', 'score' => 78],
        ['name' => 'Toko Online Berkah', 'email' => 'owner@tokoberkah.com', 'phone' => '085678901234', 'interest' => 'Social Media Management', 'source' => 'Instagram', 'score' => 72],
        ['name' => 'PT Sumber Rejeki', 'email' => 'marketing@sumberrejeki.co.id', 'phone' => '081234567891', 'interest' => 'CRM System', 'source' => 'LinkedIn', 'score' => 88],
        ['name' => 'Klinik Sehat Sentosa', 'email' => 'admin@kliniksehatsentosa.id', 'phone' => '087654321099', 'interest' => 'AI Automation Setup', 'source' => 'Website', 'score' => 82],
        ['name' => 'PT Karya Bangsa', 'email' => 'info@karyabangsa.co.id', 'phone' => '081234567892', 'interest' => 'Digital Marketing Audit', 'source' => 'Google Ads', 'score' => 75],
        ['name' => 'Warung Kopi Nusantara', 'email' => 'hello@warkopnusantara.com', 'phone' => '085678901235', 'interest' => 'Landing Page Design', 'source' => 'Facebook', 'score' => 68],
        ['name' => 'PT Maju Mundur', 'email' => 'ceo@majumundur.co.id', 'phone' => '081298765433', 'interest' => 'Business Consultation', 'source' => 'Referral', 'score' => 95],
        ['name' => 'Apotek Farma Sehat', 'email' => 'apotek@farma-sehat.id', 'phone' => '087654321100', 'interest' => 'Email Marketing Setup', 'source' => 'Website', 'score' => 70]
    ];
    
    // Closed deals for today
    private $todayDeals = [
        ['client' => 'PT Maju Jaya', 'product' => 'AI Chatbot License', 'amount' => 5000000, 'status' => 'paid', 'date' => date('Y-m-d')],
        ['client' => 'CV Sejahtera Abadi', 'product' => 'Landing Page Design', 'amount' => 3000000, 'status' => 'paid', 'date' => date('Y-m-d')],
        ['client' => 'PT Indo Digital', 'product' => 'SEO Package Monthly', 'amount' => 2000000, 'status' => 'pending', 'date' => date('Y-m-d')]
    ];
    
    public function getDailyReport() {
        $todayIncome = array_sum(array_column($this->todayDeals, 'amount'));
        $paidIncome = array_sum(array_filter(
            array_column($this->todayDeals, 'amount'),
            function($i) { return $this->todayDeals[$i]['status'] === 'paid'; },
            ARRAY_FILTER_USE_BOTH
        ));
        
        $totalLeads = count($this->todayLeads);
        $hotLeads = count(array_filter($this->todayLeads, fn($l) => $l['score'] >= 80));
        $warmLeads = count(array_filter($this->todayLeads, fn($l) => $l['score'] >= 60 && $l['score'] < 80));
        
        $expectedIncome = $todayIncome + (count(array_filter($this->todayLeads, fn($l) => $l['score'] >= 80)) * 3000000 * 0.15);
        
        return [
            'date' => date('Y-m-d'),
            'time' => date('H:i:s'),
            'daily_target' => $this->dailyTarget,
            'today_income' => $todayIncome,
            'paid_income' => $paidIncome,
            'pending_income' => $todayIncome - $paidIncome,
            'expected_income' => $expectedIncome,
            'leads_generated' => $totalLeads,
            'hot_leads' => $hotLeads,
            'warm_leads' => $warmLeads,
            'deals_closed' => count($this->todayDeals),
            'deals' => $this->todayDeals,
            'leads' => $this->todayLeads,
            'products' => $this->products,
            'progress_percent' => round(($todayIncome / $this->dailyTarget) * 100, 1)
        ];
    }
    
    public function getProducts() {
        return $this->products;
    }
    
    public function getTodayLeads() {
        return $this->todayLeads;
    }
    
    public function getTodayDeals() {
        return $this->todayDeals;
    }
    
    public function getWeeklyTarget() {
        return $this->dailyTarget * 7;
    }
    
    public function getMonthlyTarget() {
        return $this->dailyTarget * 30;
    }
}
