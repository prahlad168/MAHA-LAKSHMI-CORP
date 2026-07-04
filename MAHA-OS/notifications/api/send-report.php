<?php
/**
 * MAHA LAKSHMI AIOS - Daily Report API
 * Sends report to CEO
 * CEO: ceo@mahalakshmi.id | WhatsApp: 081337558787
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET');

require_once __DIR__ . '/../DailyReportSender.php';

$result = sendDailyReport();
echo json_encode($result, JSON_PRETTY_PRINT);
