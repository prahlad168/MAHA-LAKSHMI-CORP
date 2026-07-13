<?php
/** MAHA LAKSHMI - Finance API */
header('Content-Type: application/json');

$data = [
    'date' => date('d F Y'),
    'time' => date('H:i:s') . ' WIB',
    'wallet_balance' => 0,
    'bank_balance' => 0,
    'bank_account' => 'BCA 6485086645',
    'today_income' => 0,
    'today_expense' => 0,
    'monthly_target' => 1000000000,
    'monthly_revenue' => 0,
    'progress_percent' => 0,
    'profit_distribution' => [
        ['name' => 'Owner (Pak Pur)', 'percent' => 60, 'account' => 'BCA 6485086645'],
        ['name' => 'Reinvestasi', 'percent' => 25, 'account' => 'Company Reserve'],
        ['name' => 'Team Bonus', 'percent' => 10, 'account' => 'Team Account'],
        ['name' => 'Charity/CSR', 'percent' => 5, 'account' => 'CSR Account']
    ]
];

echo json_encode(['success' => true, 'data' => $data], JSON_PRETTY_PRINT);
