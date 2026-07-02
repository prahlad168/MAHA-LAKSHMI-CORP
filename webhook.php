<?php
/**
 * MAHA LAKSHMI - GitHub Webhook Receiver
 * 
 * Paste this code to: payanganhospital.gianyarkab.go.id/webhook.php
 * 
 * This script receives webhook from GitHub and executes git pull
 */

// Prevent direct access
if (php_sapi_name() === 'cli') {
    die('CLI access denied');
}

// CORS Headers (if needed)
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-GitHub-Event, X-Hub-Signature');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only allow POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    die(json_encode(['error' => 'Method not allowed']));
}

// Get payload
$payload = file_get_contents('php://input');
$headers = getallheaders();

// Get event type
$event = $headers['X-GitHub-Event'] ?? 'unknown';

// Log all requests
$log = "[" . date('Y-m-d H:i:s') . "] Event: $event\n";
$log .= "IP: " . ($_SERVER['REMOTE_ADDR'] ?? 'unknown') . "\n";
$log .= "Payload: " . substr($payload, 0, 200) . "...\n\n";
@file_put_contents(__DIR__ . '/webhook.log', $log, FILE_APPEND);

// Only process push events
if ($event !== 'push') {
    echo json_encode([
        'success' => true,
        'message' => 'Event ignored: ' . $event
    ]);
    exit;
}

// Parse payload
$data = json_decode($payload, true);
$branch = $data['ref'] ?? '';
$commit = $data['after'] ?? $data['head_commit']['id'] ?? 'unknown';
$message = $data['head_commit']['message'] ?? 'No message';
$author = $data['head_commit']['author']['name'] ?? 'Unknown';

// Check if it's main branch
if (strpos($branch, 'main') === false) {
    echo json_encode([
        'success' => true,
        'message' => 'Branch ignored: ' . $branch
    ]);
    exit;
}

// Execute deployment
$result = deploy();

// Response
echo json_encode([
    'success' => $result['success'],
    'message' => $result['success'] ? 'Deployed successfully!' : 'Deployment failed',
    'branch' => $branch,
    'commit' => $commit,
    'output' => $result['output'],
    'deployed_by' => $author
]);

function deploy() {
    $output = [];
    $return_var = 0;
    
    // Change to repository directory
    chdir(__DIR__);
    
    // Execute git pull
    exec('git pull origin main 2>&1', $output, $return_var);
    
    // Log result
    $log = "[" . date('Y-m-d H:i:s') . "] Deploy Result: " . ($return_var === 0 ? 'SUCCESS' : 'FAILED') . "\n";
    $log .= "Output: " . implode("\n", $output) . "\n\n";
    @file_put_contents(__DIR__ . '/webhook.log', $log, FILE_APPEND);
    
    return [
        'success' => $return_var === 0,
        'output' => implode("\n", $output)
    ];
}
