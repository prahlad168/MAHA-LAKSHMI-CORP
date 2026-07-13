<?php
/**
 * MAHA TUKANG - WhatsApp Auto Reply API
 * Agent: whatsapp-agent-v1
 */

// WhatsApp Number
define('WA_NUMBER', '6281337558787');
define('COMPANY_NAME', 'MAHA TUKANG');

// Response Templates
$responses = [
    'sapa' => "Halo! 👋 Selamat datang di MAHA TUKANG!\n\nPlatform marketplace jasa tukang berbasis AI Indonesia.\n\nSilakan ketik kebutuhan Anda, kami bantu carikan tukang terbaik! 😊",
    
    'renovasi' => "🔧 LAYANAN RENOVASI RUMAH\n\nKami sediakan:\n• Renovasi Total\n• Renovasi Partial\n• Upgrade Rumah\n\nEstimasi:\n• Kecil: Rp 5-20jt\n• Sedang: Rp 20-50jt\n• Besar: Rp 50-100jt+\n\nMau kami carikan tukang untuk renovasi? 😊",
    
    'listrik' => "⚡ LAYANAN LISTRIK\n\n• Instalasi Baru\n• Perbaikan Listrik\n• Upgrade Panel\n• Pasang Lampu\n\nEstimasi:\n• Minor: Rp 500rb-2jt\n• Sedang: Rp 2-5jt\n• Besar: Rp 5-10jt+\n\nHubungi kami untuk info lebih lanjut!",
    
    'cat' => "🎨 LAYANAN CAT RUMAH\n\n• Cat Interior\n• Cat Eksterior\n• Cat Dulux/Nippon\n• Repaint Total\n\nEstimasi:\n• Per meter: Rp 30-80rb/m²\n• Rumah kecil: Rp 3-10jt\n• Rumah besar: Rp 10-30jt+\n\nMau dapat estimasi lebih akurat?",
    
    'plumbing' => "🚿 LAYANAN PLUMBING\n\n• Pasang Pipa Baru\n• Perbaikan Pipa Bocor\n• Pasang WC/Wastafel\n• Saluran Air\n\nEstimasi:\n• Minor: Rp 500rb-1jt\n• Sedang: Rp 1-3jt\n• Besar: Rp 3-10jt+\n\nSiap membantu! 😊",
    
    'default' => "Terima kasih sudah menghubungi MAHA TUKANG! 🙏\n\nKami bantu untuk:\n🔧 Renovasi Rumah\n⚡ Listrik\n🎨 Cat\n🚿 Plumbing\n🧱 Keramik\n🏠 Dan layanan pertukangan lainnya\n\nSilakan ketik:\n1. Jenis layanan\n2. Lokasi\n3. Estimasi budget\n\nKami carikan tukang terbaik untuk Anda! 😊"
];

// Handle incoming message
$input = json_decode(file_get_contents('php://input'), true);
$message = strtolower(trim($input['message'] ?? ''));
$from = $input['from'] ?? '';

// Generate response
$response = '';

if (empty($message)) {
    $response = $responses['sapa'];
} elseif (strpos($message, 'halo') !== false || strpos($message, 'hi') !== false || strpos($message, 'hai') !== false) {
    $response = $responses['sapa'];
} elseif (strpos($message, 'renovasi') !== false) {
    $response = $responses['renovasi'];
} elseif (strpos($message, 'listrik') !== false) {
    $response = $responses['listrik'];
} elseif (strpos($message, 'cat') !== false) {
    $response = $responses['cat'];
} elseif (strpos($message, 'pipa') !== false || strpos($message, 'plumbing') !== false || strpos($message, 'wc') !== false) {
    $response = $responses['plumbing'];
} else {
    $response = $responses['default'];
}

// Add CTA
$response .= "\n\n━━━━━━━━━━━━━━━━\n📞 Butuh bantuan lanjut?\nHubungi: 081337558787\n🌐 MAHA TUKANG - #1 Platform Tukang AI";

// Log for analytics
$log = [
    'timestamp' => date('Y-m-d H:i:s'),
    'from' => $from,
    'message' => $message,
    'response' => $response
];
file_put_contents(__DIR__ . '/whatsapp_log.json', json_encode($log, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);

// Return response
header('Content-Type: application/json');
echo json_encode([
    'status' => 'success',
    'response' => $response,
    'agent' => 'whatsapp-agent-v1',
    'company' => COMPANY_NAME
]);
