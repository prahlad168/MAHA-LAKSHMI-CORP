<?php
/**
 * 🤖 WhatsApp Webhook Handler
 * Auto-reply dan handle incoming messages
 * 
 * Setup:
 * 1. Upload ke hosting
 * 2. Set webhook URL di Meta Developer Console
 * 3. Verify token
 */

// Configuration
$VERIFY_TOKEN = "maha_lakshmi_verify_token_2026";
$ACCESS_TOKEN = "YOUR_WHATSAPP_ACCESS_TOKEN";
$PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID";

// =======================
// WEBHOOK VERIFICATION
// =======================
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Facebook webhook verification
    $mode = $_GET['hub_mode'];
    $token = $_GET['hub_verify_token'];
    $challenge = $_GET['hub_challenge'];
    
    if ($mode === 'subscribe' && $token === $VERIFY_TOKEN) {
        echo $challenge;
        http_response_code(200);
    } else {
        http_response_code(403);
    }
    exit;
}

// =======================
// INCOMING MESSAGES
// =======================
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Extract message data
    $entry = $input['entry'][0] ?? [];
    $changes = $entry['changes'][0] ?? [];
    $value = $changes['value'] ?? [];
    $messages = $value['messages'] ?? [];
    
    if (empty($messages)) {
        exit;
    }
    
    foreach ($messages as $message) {
        $from = $message['from'] ?? '';
        $msg_id = $message['id'] ?? '';
        $type = $message['type'] ?? '';
        $timestamp = $message['timestamp'] ?? '';
        
        // Handle different message types
        if ($type === 'text') {
            $body = $message['text']['body'] ?? '';
            handleTextMessage($from, $body, $msg_id);
        }
        elseif ($type === 'interactive') {
            $body = $message['interactive']['button_reply']['title'] ?? '';
            handleTextMessage($from, $body, $msg_id);
        }
        
        // Log incoming message
        logMessage($from, $body, 'INCOMING');
    }
    
    http_response_code(200);
    exit;
}

// =======================
// HANDLE TEXT MESSAGES
// =======================
function handleTextMessage($from, $body, $msg_id) {
    global $PHONE_NUMBER_ID, $ACCESS_TOKEN;
    
    $body = strtolower(trim($body));
    
    // Auto-response logic
    $response = "";
    
    if (strpos($body, 'halo') !== false || strpos($body, 'hi') !== false || strpos($body, 'hai') !== false) {
        $response = "Halo! 👋

Terima kasih sudah menghubungi MAHA LAKSHMI Digital!

Kami menyediakan:
✅ Software Development
✅ Digital Marketing
✅ AI Solutions
✅ E-Commerce Setup

Harga mulai dari Rp 1.000.000

Mau konsultasi gratis? Silakan reply dengan:
1. Jika tertarik SOFTWARE
2. Jika tertarik MARKETING
3. Jika tertarik AI
4. Jika tertarik E-COMMERCE

Terima kasih! 🙏";
    }
    elseif (strpos($body, '1') !== false || strpos($body, 'software') !== false) {
        $response = "Excellent! 🎯

MAHA LAKSHMI Software Services:

✅ Website Company Profile - Rp 2.000.000
✅ Web App Custom - Rp 10.000.000
✅ Mobile App - Rp 15.000.000
✅ SaaS Product - Rp 25.000.000+

Benefits:
- Free maintenance 3 bulan
- Full documentation
- 24/7 support

Mau diskusi lebih lanjut?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    elseif (strpos($body, '2') !== false || strpos($body, 'marketing') !== false) {
        $response = "Great choice! 📢

MAHA LAKSHMI Digital Marketing:

✅ Social Media Management - Rp 3.000.000/bulan
✅ SEO Optimization - Rp 5.000.000
✅ Google Ads Management - Rp 2.000.000/bulan
✅ Content Marketing - Rp 2.500.000/bulan

Benefits:
- Monthly report
- Dedicated account manager
- ROI tracking

Mau diskusi lebih lanjut?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    elseif (strpos($body, '3') !== false || strpos($body, 'ai') !== false) {
        $response = "Future is AI! 🤖

MAHA LAKSHMI AI Solutions:

✅ Chatbot Development - Rp 5.000.000
✅ AI Automation - Rp 15.000.000
✅ AI Agent System - Rp 25.000.000
✅ Custom AI Model - Rp 50.000.000+

Benefits:
- Increase efficiency 70%
- 24/7 operation
- Cost reduction

Mau diskusi lebih lanjut?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    elseif (strpos($body, '4') !== false || strpos($body, 'ecommerce') !== false) {
        $response = "E-Commerce is the future! 🛒

MAHA LAKSHMI E-Commerce Solutions:

✅ Online Shop Setup - Rp 5.000.000
✅ Marketplace Integration - Rp 3.000.000
✅ Payment Gateway - Rp 2.000.000
✅ Full E-Commerce Platform - Rp 15.000.000

Benefits:
- Ready in 7 days
- Free training
- Inventory management

Mau diskusi lebih lanjut?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    elseif (strpos($body, 'harga') !== false || strpos($body, 'price') !== false || strpos($body, 'berapa') !== false) {
        $response = "Berikut harga paket kami: 💰

SOFTWARE:
• Basic Website: Rp 2.000.000
• Professional Website: Rp 5.000.000
• Custom App: Rp 15.000.000

MARKETING:
• Starter Package: Rp 1.500.000/bulan
• Pro Package: Rp 5.000.000/bulan

AI:
• Chatbot: Rp 5.000.000
• Automation: Rp 15.000.000

Mau详细信息?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    elseif (strpos($body, 'partnership') !== false || strpos($body, 'partner') !== false) {
        $response = "Great to hear about partnership! 🤝

MAHA LAKSHMI Partnership Program:

BENEFITS:
✅ 15% commission per transaction
✅ Zero upfront cost
✅ Marketing materials provided
✅ Priority support

HOW IT WORKS:
1. Anda refer client ke kami
2. Client purchase services
3. Anda dapat 15% commission

Contoh:
Client purchase Rp 10.000.000
→ Anda dapat Rp 1.500.000

Mau ikut program partnership?
📱 wa.me/6281337558787

Terima kasih! 🙏";
    }
    else {
        $response = "Terima kasih pesan Anda! 🙏

Kami dari MAHA LAKSHMI Digital Holdings.

Untuk informasi lebih lanjut, silakan reply dengan:
1. SOFTWARE
2. MARKETING
3. AI SOLUTIONS
4. E-COMMERCE
5. PARTNERSHIP

Atau hubungi langsung:
📱 wa.me/6281337558787

Tim kami siap membantu! 💪";
    }
    
    // Send auto-reply
    sendMessage($from, $response);
    
    // Log
    logMessage($from, $response, 'AUTO-REPLY');
}

// =======================
// SEND MESSAGE FUNCTION
// =======================
function sendMessage($to, $message) {
    global $PHONE_NUMBER_ID, $ACCESS_TOKEN;
    
    $url = "https://graph.facebook.com/v18.0/$PHONE_NUMBER_ID/messages";
    
    $data = [
        'messaging_product' => 'whatsapp',
        'to' => $to,
        'type' => 'text',
        'text' => [
            'body' => $message
        ]
    ];
    
    $headers = [
        'Authorization: Bearer ' . $ACCESS_TOKEN,
        'Content-Type: application/json'
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// =======================
// LOG FUNCTION
// =======================
function logMessage($from, $message, $type) {
    $log = date('Y-m-d H:i:s') . " | $type | $from | " . substr($message, 0, 100) . "\n";
    file_put_contents('whatsapp-log.txt', $log, FILE_APPEND);
}
