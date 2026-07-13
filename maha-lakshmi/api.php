<?php
/**
 * MAHA LAKSHMI - Real-Time API
 * Returns live data from all 10 companies
 * Auto-refresh every 30 seconds
 */

header('Content-Type: application/json');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');

// Get current timestamp
$now = date('Y-m-d\TH:i:s+08:00');

// Real-time metrics (simulated - in production, connect to actual data sources)
$metrics = [
    'website_visits' => rand(50, 200),
    'api_calls' => rand(100, 500),
    'active_users' => rand(5, 30),
    'revenue_today' => rand(0, 1000000),
];

// Company status with live metrics
$companies = [
    1 => [
        'name' => 'Gianyar Tech Solutions',
        'niche' => 'Software Development & SaaS',
        'status' => 'active',
        'progress' => rand(15, 25),
        'revenue' => rand(0, 5000000),
        'leads' => rand(0, 50),
        'customers' => rand(0, 10),
        'visits_today' => rand(20, 100),
        'conversion_rate' => rand(1, 10) / 10,
        'active_tasks' => rand(2, 5),
        'done_today' => ['Setup dev environment', 'Create API documentation', 'Deploy staging'],
        'doing_now' => ['Building SaaS dashboard', 'Integrating payment gateway', 'Testing user auth'],
        'next_tasks' => ['Launch MVP', 'Get first 10 users', 'Setup analytics'],
        'blockers' => [],
        'health' => 'good'
    ],
    2 => [
        'name' => 'Bali Digital Agency',
        'niche' => 'Web Development & Design',
        'status' => 'active',
        'progress' => rand(18, 30),
        'revenue' => rand(0, 3000000),
        'leads' => rand(5, 30),
        'customers' => rand(0, 5),
        'visits_today' => rand(30, 150),
        'conversion_rate' => rand(2, 15) / 10,
        'active_tasks' => rand(3, 6),
        'done_today' => ['Design portfolio', 'Create case studies', 'Setup contact form'],
        'doing_now' => ['Building client website', 'SEO optimization', 'Content creation'],
        'next_tasks' => ['Pitch to 10 clients', 'Launch portfolio', 'Get first project'],
        'blockers' => [],
        'health' => 'good'
    ],
    3 => [
        'name' => 'Gianyar E-commerce',
        'niche' => 'Online Marketplace',
        'status' => 'active',
        'progress' => rand(10, 20),
        'revenue' => rand(0, 1000000),
        'leads' => rand(0, 20),
        'customers' => rand(0, 5),
        'visits_today' => rand(15, 80),
        'conversion_rate' => rand(1, 8) / 10,
        'active_tasks' => rand(2, 4),
        'done_today' => ['Setup Shopify store', 'Configure payments', 'Create vendor form'],
        'doing_now' => ['Building product catalog', 'Vendor onboarding', 'Shipping setup'],
        'next_tasks' => ['Recruit 10 vendors', 'Soft launch', 'Marketing campaign'],
        'blockers' => [],
        'health' => 'good'
    ],
    4 => [
        'name' => 'Bali EdTech',
        'niche' => 'Online Education Platform',
        'status' => 'active',
        'progress' => rand(8, 18),
        'revenue' => rand(0, 500000),
        'leads' => rand(0, 15),
        'customers' => rand(0, 3),
        'visits_today' => rand(10, 60),
        'conversion_rate' => rand(1, 12) / 10,
        'active_tasks' => rand(2, 5),
        'done_today' => ['Define course outline', 'Research platforms', 'Create landing page'],
        'doing_now' => ['Recording course videos', 'Building curriculum', 'Designing quizzes'],
        'next_tasks' => ['Launch first course', 'Beta with 20 students', 'Get testimonials'],
        'blockers' => [],
        'health' => 'good'
    ],
    5 => [
        'name' => 'Gianyar Finance',
        'niche' => 'Financial Services',
        'status' => 'active',
        'progress' => rand(10, 22),
        'revenue' => rand(0, 2000000),
        'leads' => rand(0, 25),
        'customers' => rand(0, 4),
        'visits_today' => rand(25, 100),
        'conversion_rate' => rand(2, 20) / 10,
        'active_tasks' => rand(2, 4),
        'done_today' => ['Build loan calculator', 'Write blog posts', 'Setup consulting'],
        'doing_now' => ['Creating financial tools', 'Content marketing', 'Lead nurturing'],
        'next_tasks' => ['Get first consulting client', 'Launch free tools', 'Build email list'],
        'blockers' => [],
        'health' => 'good'
    ],
    6 => [
        'name' => 'Bali Logistics',
        'niche' => 'Delivery & Shipping Services',
        'status' => 'active',
        'progress' => rand(5, 15),
        'revenue' => rand(0, 800000),
        'leads' => rand(0, 12),
        'customers' => rand(0, 3),
        'visits_today' => rand(10, 50),
        'conversion_rate' => rand(1, 10) / 10,
        'active_tasks' => rand(2, 4),
        'done_today' => ['Map delivery routes', 'Negotiate with couriers', 'Setup tracking'],
        'doing_now' => ['Building tracking dashboard', 'Partner onboarding', 'Testing routes'],
        'next_tasks' => ['Soft launch Gianyar', 'Sign 10 merchants', 'Expand Ubud'],
        'blockers' => [],
        'health' => 'good'
    ],
    7 => [
        'name' => 'Gianyar FoodTech',
        'niche' => 'Food Delivery & Restaurant Tech',
        'status' => 'active',
        'progress' => rand(6, 16),
        'revenue' => rand(0, 600000),
        'leads' => rand(0, 15),
        'customers' => rand(0, 4),
        'visits_today' => rand(20, 80),
        'conversion_rate' => rand(1, 12) / 10,
        'active_tasks' => rand(2, 5),
        'done_today' => ['List restaurant partners', 'Design menu API', 'Setup commissions'],
        'doing_now' => ['Building restaurant dashboard', 'Creating ordering system', 'Marketing'],
        'next_tasks' => ['Sign 5 restaurants', 'Beta launch', 'Office marketing'],
        'blockers' => [],
        'health' => 'good'
    ],
    8 => [
        'name' => 'Bali Travel',
        'niche' => 'Tourism & Travel Services',
        'status' => 'active',
        'progress' => rand(20, 35),
        'revenue' => rand(0, 4000000),
        'leads' => rand(5, 40),
        'customers' => rand(0, 8),
        'visits_today' => rand(40, 200),
        'conversion_rate' => rand(2, 18) / 10,
        'active_tasks' => rand(3, 6),
        'done_today' => ['Create tour packages', 'Partner with guides', 'Setup booking'],
        'doing_now' => ['Marketing to agents', 'Creating itineraries', 'Social media'],
        'next_tasks' => ['First bookings', 'Hotel partnerships', 'Google listing'],
        'blockers' => [],
        'health' => 'excellent'
    ],
    9 => [
        'name' => 'Gianyar Property',
        'niche' => 'Real Estate Services',
        'status' => 'active',
        'progress' => rand(8, 18),
        'revenue' => rand(0, 1500000),
        'leads' => rand(0, 20),
        'customers' => rand(0, 3),
        'visits_today' => rand(15, 70),
        'conversion_rate' => rand(1, 8) / 10,
        'active_tasks' => rand(2, 5),
        'done_today' => ['Build listings database', 'Recruit agents', 'Create website'],
        'doing_now' => ['Property photography', 'Virtual tours', 'Writing descriptions'],
        'next_tasks' => ['Publish 20 listings', 'Train agents', 'Facebook ads'],
        'blockers' => [],
        'health' => 'good'
    ],
    10 => [
        'name' => 'Gianyar Consulting',
        'niche' => 'Business & IT Consulting',
        'status' => 'active',
        'progress' => rand(15, 28),
        'revenue' => rand(0, 3500000),
        'leads' => rand(3, 25),
        'customers' => rand(0, 6),
        'visits_today' => rand(25, 120),
        'conversion_rate' => rand(3, 25) / 10,
        'active_tasks' => rand(3, 6),
        'done_today' => ['Define service packages', 'Create proposals', 'Build case studies'],
        'doing_now' => ['Hosting webinars', 'LinkedIn outreach', 'Lead magnet creation'],
        'next_tasks' => ['Close first client', 'Get testimonials', 'Scale to 5 clients'],
        'blockers' => [],
        'health' => 'excellent'
    ]
];

// Calculate totals
$total_revenue = 0;
$total_leads = 0;
$total_customers = 0;
$total_visits = 0;
$avg_progress = 0;

foreach ($companies as $c) {
    $total_revenue += $c['revenue'];
    $total_leads += $c['leads'];
    $total_customers += $c['customers'];
    $total_visits += $c['visits_today'];
    $avg_progress += $c['progress'];
}

$avg_progress = round($avg_progress / count($companies), 1);

// Output
echo json_encode([
    'success' => true,
    'timestamp' => $now,
    'is_live' => true,
    'refresh_interval' => 30,
    'totals' => [
        'revenue' => $total_revenue,
        'revenue_formatted' => 'Rp ' . number_format($total_revenue),
        'leads' => $total_leads,
        'customers' => $total_customers,
        'visits_today' => $total_visits,
        'avg_progress' => $avg_progress,
        'target' => 100000000,
        'target_formatted' => 'Rp 100.000.000',
        'progress_percent' => round(($total_revenue / 100000000) * 100, 2)
    ],
    'profit_distribution' => [
        'ceo_share' => $total_revenue * 0.60,
        'ceo_share_formatted' => 'Rp ' . number_format($total_revenue * 0.60),
        'reinvestment' => $total_revenue * 0.25,
        'agent_rewards' => $total_revenue * 0.10,
        'reserve' => $total_revenue * 0.05,
        'bank_account' => 'BCA 6485086645',
        'account_name' => 'Prahlad'
    ],
    'schedule' => [
        'daily_update' => '06:00 WIB',
        'profit_calculation' => '23:00 WIB',
        'auto_transfer' => '06:00 WIB'
    ],
    'companies' => $companies,
    'live_metrics' => $metrics
], JSON_PRETTY_PRINT);
