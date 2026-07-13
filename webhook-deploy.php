<?php
/**
 * MAHA LAKSHMI - Webhook Deploy Script
 * 
 * Paste this file to your hosting: payanganhospital.gianyarkab.go.id/webhook-deploy.php
 * Then add webhook URL in GitHub: Settings > Webhooks > Add webhook
 * URL: https://payanganhospital.gianyarkab.go.id/webhook-deploy.php?secret=YOUR_SECRET
 */

// Configuration
$secret = 'gauranga-deploy-2026'; // Change this to your secret
$repo_path = __DIR__; // Deploy to current directory
$branch = 'main';

// Get GitHub webhook payload
$payload = file_get_contents('php://input');
$headers = getallheaders();

// Verify signature if secret is set
if (isset($_GET['secret']) && $_GET['secret'] !== $secret) {
    http_response_code(403);
    die('Invalid secret');
}

// Log the deployment
$log_file = __DIR__ . '/deploy.log';
$timestamp = date('Y-m-d H:i:s');
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

// Parse payload if JSON
$event = $headers['X-GitHub-Event'] ?? 'unknown';
$data = json_decode($payload, true);
$commit = $data['after'] ?? $data['head_commit']['id'] ?? 'unknown';
$message = $data['head_commit']['message'] ?? 'No message';

// Log
$log = "[$timestamp] $event - $commit - $message - IP: $ip\n";
file_put_contents($log_file, $log, FILE_APPEND);

// Only deploy on push
if ($event !== 'push') {
    die('Event ignored: ' . $event);
}

// Execute git pull
chdir($repo_path);

// Set timezone
putenv('TZ=Asia/Makassar');

// Git pull command
$output = [];
$return_var = 0;
exec('git pull origin ' . $branch . ' 2>&1', $output, $return_var);

$output_text = implode("\n", $output);

// Log result
$result = $return_var === 0 ? 'SUCCESS' : 'FAILED';
$log_result = "[$timestamp] DEPLOY $result\n";
$log_result .= "Output: $output_text\n";
file_put_contents($log_file, $log_result, FILE_APPEND);

// Response
header('Content-Type: application/json');
echo json_encode([
    'success' => $return_var === 0,
    'message' => $return_var === 0 ? 'Deployed successfully!' : 'Deployment failed',
    'output' => $output,
    'commit' => $commit
]);
