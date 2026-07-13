<?php
/** MAHA LAKSHMI - Income Generator API */
header('Content-Type: application/json');
require_once __DIR__ . '/../IncomeGenerator.php';

$generator = new IncomeGenerator();
echo json_encode(['success' => true, 'data' => $generator->getDailyReport()], JSON_PRETTY_PRINT);
