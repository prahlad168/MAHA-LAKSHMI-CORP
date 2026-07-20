<?php
/**
 * 🤖 WhatsApp Auto-Send Script
 * Send messages to leads automatically
 * 
 * Usage:
 * php whatsapp-send.php --lead=LEAD_ID
 * php whatsapp-send.php --all
 * php whatsapp-send.php --type=outreach
 */

// Configuration
$CONFIG = [
    'phone_number_id' => 'YOUR_PHONE_NUMBER_ID',
    'access_token' => 'YOUR_ACCESS_TOKEN',
    'leads_file' => 'archives/LEADS-DATABASE.json',
    'log_file' => 'whatsapp-send-log.txt'
];

// =======================
// MESSAGE TEMPLATES
// =======================
$MESSAGES = [
    'outreach' => [
        'bali_travel' => "🏝️ HALO [NAME]! 👋

Dari **Bali Travel Platform** 🇮🇩

Partner dengan kami untuk tour eksklusif!

✅ Commission 15% per booking
✅ No minimum order
✅ Professional guides ready
✅ Real-time booking system

Contoh:
Tamuku pesan Ubud Tour Rp 750.000
→ Anda dapat Rp 112.500 (15%)

Mau diskusi partnership?
📱 wa.me/6281337558787

--
Bali Travel
Your Partner in Bali",

        'tech' => "💻 HALO [NAME]! 👋

Dari **Gianyar Tech Solutions** 🇮🇩

Kami bantu bisnis Anda go-digital!

✅ Website Company Profile - Rp 2.000.000
✅ Online Shop - Rp 5.000.000
✅ Custom App - Rp 15.000.000

✅ Free konsultasi 30 menit
✅ Free maintenance 3 bulan

Mau diskusi?
📱 wa.me/6281337558787

--
Gianyar Tech Solutions",

        'digital' => "📢 HALO [NAME]! 👋

Dari **Bali Digital Agency** 🇮🇩

Kami bantu bisnis Anda lebih dikenal!

SERVICES:
✅ Social Media Management - Rp 3.000.000/bulan
✅ SEO Optimization - Rp 5.000.000
✅ Google Ads - Rp 2.000.000/bulan

✅ Monthly report
✅ Dedicated manager
✅ ROI guaranteed

Mau diskusi?
📱 wa.me/6281337558787

--
Bali Digital Agency",

        'ai' => "🤖 HALO [NAME]! 👋

Dari **Payangan AI Solutions** 🇮🇩

Automasi bisnis dengan AI!

SOLUTIONS:
✅ Chatbot - Rp 5.000.000
✅ AI Automation - Rp 15.000.000
✅ AI Agent System - Rp 25.000.000

✅ Increase efficiency 70%
✅ 24/7 operation
✅ Cost reduction

Mau diskusi?
📱 wa.me/6281337558787

--
Payangan AI Solutions"
    ],
    
    'followup_day3' => "👋 Hi [NAME]!

Following up dari pesan kami sebelumnya.

Apakah Anda sudah mempertimbangkan partnership dengan kami?

15% commission, zero risk!

Mau diskusi lebih lanjut?
📱 wa.me/6281337558787

--
MAHA LAKSHMI",

    'followup_day7' => "👋 Hi [NAME]!

Just checking in again!

Partnership offer masih tersedia:
✅ 15% commission
✅ No minimum order
✅ We handle everything

Apakah ada pertanyaan yang bisa kami bantu?

📱 wa.me/6281337558787

--
MAHA LAKSHMI",

    'followup_day14' => "⚠️ Hi [NAME]!

Ini adalah pesan follow-up terakhir kami.

🌟 SPECIAL OFFER (This week only!):
✅ 15% commission
✅ Waived setup fee
✅ Priority support

Setelah ini, list akan kami tutup.

Apakah Anda tertarik?
📱 wa.me/6281337558787

--
MAHA LAKSHMI"
];

// =======================
// CLI PARSING
// =======================
$options = getopt('', ['lead::', 'all', 'type::', 'dry-run']);
$type = $options['type'] ?? 'outreach';
$dry_run = isset($options['dry-run']);

// =======================
// MAIN EXECUTION
// =======================
echo "🤖 WhatsApp Auto-Send Script\n";
echo "========================================\n\n";

// Load leads
$leads_file = $CONFIG['leads_file'];
if (!file_exists($leads_file)) {
    echo "❌ Leads file not found: $leads_file\n";
    exit(1);
}

$leads_data = json_decode(file_get_contents($leads_file), true);
$leads = $leads_data['leads'] ?? [];

echo "📊 Total Leads: " . count($leads) . "\n\n";

// Send to specific lead
if (isset($options['lead'])) {
    $lead_id = $options['lead'];
    $lead = findLead($leads, $lead_id);
    if ($lead) {
        sendToLead($lead, $type);
    } else {
        echo "❌ Lead not found: $lead_id\n";
    }
}
// Send to all
elseif (isset($options['all'])) {
    echo "📤 Sending to ALL leads...\n";
    echo "------------------------------------------\n";
    foreach ($leads as $lead) {
        sendToLead($lead, $type);
        sleep(2); // Delay to avoid rate limit
    }
}
// Show status
else {
    showLeadStatus($leads);
}

// =======================
// FUNCTIONS
// =======================

function findLead($leads, $id) {
    foreach ($leads as $lead) {
        if ($lead['id'] == $id) {
            return $lead;
        }
    }
    return null;
}

function sendToLead($lead, $type) {
    global $MESSAGES, $CONFIG, $dry_run;
    
    $name = $lead['name'] ?? 'there';
    $phone = $lead['whatsapp'] ?? '';
    $category = $lead['category'] ?? 'tech';
    
    // Get message template
    $template = $MESSAGES[$type][$category] ?? $MESSAGES[$type]['tech'] ?? '';
    
    if (empty($template)) {
        echo "⚠️ No template for type: $type, category: $category\n";
        return;
    }
    
    // Replace placeholder
    $message = str_replace('[NAME]', explode(' ', $name)[0], $template);
    
    echo "📱 Sending to: $name ($phone)\n";
    echo "   Category: $category\n";
    
    if ($dry_run) {
        echo "   [DRY RUN] Message preview:\n";
        echo "   " . substr($message, 0, 100) . "...\n";
    } else {
        // Send via API
        $result = sendWhatsApp($phone, $message);
        
        if ($result['success']) {
            echo "   ✅ Sent successfully!\n";
            logSend($lead, $type, 'SENT', $message);
        } else {
            echo "   ❌ Failed: " . ($result['error'] ?? 'Unknown error') . "\n";
            logSend($lead, $type, 'FAILED', $message);
        }
    }
    
    echo "\n";
}

function sendWhatsApp($phone, $message) {
    global $CONFIG;
    
    $phone = preg_replace('/[^0-9]/', '', $phone);
    
    // Add country code if not present
    if (substr($phone, 0, 1) !== '6') {
        $phone = '62' . ltrim($phone, '0');
    }
    
    $url = "https://graph.facebook.com/v18.0/" . $CONFIG['phone_number_id'] . "/messages";
    
    $data = [
        'messaging_product' => 'whatsapp',
        'to' => $phone,
        'type' => 'text',
        'text' => ['body' => $message]
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $CONFIG['access_token'],
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    $result = json_decode($response, true);
    
    if ($http_code === 200) {
        return ['success' => true, 'data' => $result];
    } else {
        return ['success' => false, 'error' => $result['error']['message'] ?? 'API Error'];
    }
}

function logSend($lead, $type, $status, $message) {
    global $CONFIG;
    
    $log = date('Y-m-d H:i:s') . " | $status | $type | " . ($lead['name'] ?? 'Unknown') . " | " . ($lead['whatsapp'] ?? '') . "\n";
    file_put_contents($CONFIG['log_file'], $log, FILE_APPEND);
}

function showLeadStatus($leads) {
    echo "📊 LEADS STATUS\n";
    echo "========================================\n\n";
    
    $statuses = [
        'new' => 0,
        'contacted' => 0,
        'responded' => 0,
        'interested' => 0,
        'proposal' => 0,
        'closed' => 0
    ];
    
    foreach ($leads as $lead) {
        $status = $lead['status'] ?? 'new';
        if (isset($statuses[$status])) {
            $statuses[$status]++;
        }
    }
    
    foreach ($statuses as $status => $count) {
        echo sprintf("%-12s: %3d leads\n", ucfirst($status), $count);
    }
    
    echo "\n";
    echo "📝 Usage:\n";
    echo "  php whatsapp-send.php --lead=1          Send to lead ID 1\n";
    echo "  php whatsapp-send.php --all             Send to all leads\n";
    echo "  php whatsapp-send.php --all --dry-run   Preview only\n";
    echo "  php whatsapp-send.php --type=followup_day3  Send follow-up\n";
}
