<?php
/**
 * MAHA AI Command Center - Data API
 * 
 * This API provides data for the MACC dashboard
 * 
 * @version 1.0.0
 * @created 2026-07-03
 */

// Enable CORS
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

// Config
$config = [
    'ceo' => [
        'name' => 'Prahlad',
        'title' => 'CEO',
        'bank' => 'BCA 6485086645'
    ],
    'holding' => [
        'name' => 'MAHA LAKSHMI HOLDINGS',
        'target_revenue' => 1000000000
    ]
];

// Companies data
$companies = [
    [
        'id' => 1,
        'name' => 'Payangan Hospital AI',
        'short' => 'Payangan AI',
        'icon' => '🏥',
        'niche' => 'Healthcare SaaS',
        'progress' => 25,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 6
    ],
    [
        'id' => 2,
        'name' => 'Gianyar Tech Solutions',
        'short' => 'Gianyar Tech',
        'icon' => '💻',
        'niche' => 'Software Development',
        'progress' => 15,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 3,
        'name' => 'Bali Digital Agency',
        'short' => 'Bali Digital',
        'icon' => '🎨',
        'niche' => 'Digital Marketing',
        'progress' => 20,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 4,
        'name' => 'Gianyar E-Commerce Hub',
        'short' => 'Gianyar E-Com',
        'icon' => '🛒',
        'niche' => 'Online Marketplace',
        'progress' => 12,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 5,
        'name' => 'Bali EdTech Center',
        'short' => 'Bali EdTech',
        'icon' => '📚',
        'niche' => 'Education Tech',
        'progress' => 10,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 6,
        'name' => 'Gianyar Finance Tech',
        'short' => 'Gianyar Finance',
        'icon' => '💰',
        'niche' => 'Financial Services',
        'progress' => 12,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 7,
        'name' => 'Bali Logistics Network',
        'short' => 'Bali Logistics',
        'icon' => '🚚',
        'niche' => 'Delivery & Logistics',
        'progress' => 8,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 8,
        'name' => 'Gianyar Food Tech',
        'short' => 'Gianyar Food',
        'icon' => '🍔',
        'niche' => 'Food Technology',
        'progress' => 8,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 9,
        'name' => 'Bali Travel Platform',
        'short' => 'Bali Travel',
        'icon' => '✈️',
        'niche' => 'Tourism & Travel',
        'progress' => 25,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ],
    [
        'id' => 10,
        'name' => 'Gianyar Property Tech',
        'short' => 'Gianyar Property',
        'icon' => '🏠',
        'niche' => 'Real Estate',
        'progress' => 10,
        'status' => 'active',
        'revenue' => 0,
        'leads' => 0,
        'customers' => 0,
        'agents' => 0
    ]
];

// Active agents
$agents = [
    ['name' => 'GAURANGA CEO', 'icon' => '👑', 'status' => 'active', 'task' => 'Strategic decisions'],
    ['name' => 'SaaS Sales Agent', 'icon' => '💰', 'status' => 'active', 'task' => 'Lead gen'],
    ['name' => 'Content Marketing', 'icon' => '📝', 'status' => 'active', 'task' => 'Creating content'],
    ['name' => 'SEO & Ads Agent', 'icon' => '🔍', 'status' => 'active', 'task' => 'Optimizing SEO'],
    ['name' => 'Customer Service', 'icon' => '🎧', 'status' => 'active', 'task' => 'Handling tickets'],
    ['name' => 'Finance Agent', 'icon' => '💵', 'status' => 'active', 'task' => 'Financial reporting']
];

// Financial data
$financial = [
    'total_revenue' => 0,
    'total_expense' => 0,
    'net_profit' => 0,
    'cash_position' => 2500000,
    'wallet' => 2500000,
    'bank' => 0,
    'distribution' => [
        'ceo_share' => 0,
        'reinvest' => 0,
        'agent' => 0,
        'reserve' => 0
    ]
];

// Alerts
$alerts = [
    ['type' => 'critical', 'icon' => 'exclamation-triangle', 'title' => 'No Revenue Generated', 'time' => '2 hours ago'],
    ['type' => 'warning', 'icon' => 'users', 'title' => 'Low Lead Generation', 'time' => '5 hours ago'],
    ['type' => 'warning', 'icon' => 'globe', 'title' => '9/10 Websites Not Deployed', 'time' => '1 day ago']
];

// Approvals
$approvals = [
    ['type' => 'budget', 'icon' => '💰', 'title' => 'Budget Request - Marketing', 'meta' => 'Rp 5.000.000 • HR Agent', 'priority' => 'medium'],
    ['type' => 'agent', 'icon' => '🤖', 'title' => 'New AI Agent Creation', 'meta' => 'Sales Agent v2 • AI Factory', 'priority' => 'medium'],
    ['type' => 'sop', 'icon' => '📄', 'title' => 'SOP Update Request', 'meta' => 'Sales SOP v2.1 • Finance Agent', 'priority' => 'low']
];

// Notifications
$notifications = [
    ['priority' => 'critical', 'icon' => 'exclamation-triangle', 'title' => 'Critical: No Revenue', 'text' => 'Semua perusahaan belum menghasilkan revenue', 'time' => '2 hours ago', 'unread' => true],
    ['priority' => 'high', 'icon' => 'users', 'title' => 'Low Lead Generation', 'text' => '3 hot leads butuh follow up', 'time' => '5 hours ago', 'unread' => true],
    ['priority' => 'medium', 'icon' => 'robot', 'title' => 'Agent Update', 'text' => 'GAURANGA CEO agent updated', 'time' => '1 day ago', 'unread' => false],
    ['priority' => 'low', 'icon' => 'check-circle', 'title' => 'Automation Complete', 'text' => 'Daily report generated successfully', 'time' => '1 day ago', 'unread' => false]
];

// Handle API requests
$action = $_GET['action'] ?? 'dashboard';

switch ($action) {
    case 'dashboard':
        echo json_encode([
            'success' => true,
            'timestamp' => date('c'),
            'data' => [
                'ceo' => $config['ceo'],
                'companies' => $companies,
                'agents' => $agents,
                'financial' => $financial,
                'alerts' => $alerts,
                'approvals' => $approvals,
                'notifications' => $notifications,
                'summary' => [
                    'total_companies' => count($companies),
                    'active_companies' => count(array_filter($companies, fn($c) => $c['status'] === 'active')),
                    'total_agents' => 60,
                    'active_agents' => count($agents),
                    'total_revenue' => array_sum(array_column($companies, 'revenue')),
                    'total_leads' => array_sum(array_column($companies, 'leads')),
                    'total_customers' => array_sum(array_column($companies, 'customers'))
                ]
            ]
        ]);
        break;
        
    case 'companies':
        echo json_encode([
            'success' => true,
            'data' => $companies
        ]);
        break;
        
    case 'agents':
        echo json_encode([
            'success' => true,
            'data' => $agents,
            'stats' => [
                'total' => 60,
                'active' => count($agents),
                'pending' => 60 - count($agents)
            ]
        ]);
        break;
        
    case 'financial':
        echo json_encode([
            'success' => true,
            'data' => $financial
        ]);
        break;
        
    case 'alerts':
        echo json_encode([
            'success' => true,
            'data' => $alerts,
            'stats' => [
                'critical' => count(array_filter($alerts, fn($a) => $a['type'] === 'critical')),
                'warning' => count(array_filter($alerts, fn($a) => $a['type'] === 'warning')),
                'info' => count(array_filter($alerts, fn($a) => $a['type'] === 'info'))
            ]
        ]);
        break;
        
    case 'approvals':
        echo json_encode([
            'success' => true,
            'data' => $approvals,
            'stats' => [
                'pending' => count($approvals),
                'approved' => 0,
                'rejected' => 0
            ]
        ]);
        break;
        
    case 'notifications':
        echo json_encode([
            'success' => true,
            'data' => $notifications,
            'stats' => [
                'unread' => count(array_filter($notifications, fn($n) => $n['unread']))
            ]
        ]);
        break;
        
    case 'health':
        echo json_encode([
            'success' => true,
            'status' => 'healthy',
            'services' => [
                'api' => 'up',
                'database' => 'up',
                'cache' => 'up'
            ],
            'uptime' => '99.9%',
            'timestamp' => date('c')
        ]);
        break;
        
    default:
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'Unknown action',
            'available_actions' => ['dashboard', 'companies', 'agents', 'financial', 'alerts', 'approvals', 'notifications', 'health']
        ]);
}