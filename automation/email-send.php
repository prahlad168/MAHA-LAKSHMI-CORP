<?php
/**
 * 🤖 Email Auto-Send Script
 * Send emails to leads automatically
 * 
 * Usage:
 * php email-send.php --lead=LEAD_ID
 * php email-send.php --all
 * php email-send.php --type=outreach
 */

// =======================
// SMTP CONFIGURATION
// =======================
$SMTP = [
    'host' => 'smtp.mahalaksmi.web.id',    // Custom domain SMTP
    'port' => 587,
    'encryption' => 'tls',
    'username' => 'admin@mahalaksmi.web.id',   // ✅ Email admin
    'password' => 'Gaurangga168$',               // ✅ Password
    'from_name' => 'MAHA LAKSHMI Holdings',
    'from_email' => 'admin@mahalaksmi.web.id'
];

// =======================
// EMAIL TEMPLATES
// =======================
$TEMPLATES = [
    'outreach' => [
        'subject' => 'Partnership Opportunity - MAHA LAKSHMI Digital',
        'body' => "
Hi [NAME],

I'm reaching out from MAHA LAKSHMI Digital Holdings, an Indonesian tech company specializing in:

• Software Development
• Digital Marketing  
• AI Automation
• E-Commerce Solutions

We're expanding our reach and would love to discuss how we can help [COMPANY] with digital transformation.

Would you be open to a 15-minute call this week?

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital Holdings
WhatsApp: +62 813 3755 8787
WhatsApp: wa.me/6281337558787
"
    ],
    
    'followup' => [
        'subject' => 'Re: Partnership Opportunity - Following Up',
        'body' => "
Hi [NAME],

Just following up on my previous email.

Have you had a chance to consider our proposal?

We're currently offering special rates for early partners.

Let me know if you'd like to schedule a call.

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital Holdings
WhatsApp: wa.me/6281337558787
"
    ],
    
    'final' => [
        'subject' => 'Final Follow-Up - Special Offer This Week',
        'body' => "
Hi [NAME],

This is our final follow-up.

SPECIAL OFFER (This week only!):
• 20% discount on all services
• Free consultation
• Priority support

After this, we'll close our outreach list.

Is there anything I can help you with?

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital
WhatsApp: wa.me/6281337558787
"
    ],
    
    'bali_travel' => [
        'subject' => 'Partnership Opportunity - Bali Travel Platform',
        'body' => "
Hi [NAME],

I'm from Bali Travel Platform, a leading travel technology company in Indonesia.

We're looking for hotel and villa partners to collaborate on exclusive tour packages.

BENEFITS:
✓ 15% commission per booking
✓ No upfront costs
✓ Professional licensed guides
✓ Real-time booking system
✓ Marketing support included

REVENUE EXAMPLE:
If 10 guests book tours monthly:
• Average booking: Rp 1.000.000
• Your commission: 15% = Rp 150.000/booking
• Monthly potential: Rp 1.500.000

Would you be interested in learning more?

Best regards,
Bali Travel Platform
WhatsApp: wa.me/6281337558787
"
    ],
    
    'tech' => [
        'subject' => 'Digital Solutions for [COMPANY]',
        'body' => "
Hi [NAME],

I came across [COMPANY] and was impressed by your work.

MAHA LAKSHMI Digital offers:

SOFTWARE DEVELOPMENT:
• Website Development - from Rp 2.000.000
• Mobile Apps - from Rp 15.000.000
• Custom Software - Custom pricing

DIGITAL MARKETING:
• SEO & Content - from Rp 2.500.000/month
• Social Media - from Rp 3.000.000/month
• Google Ads Management - from Rp 2.000.000/month

AI SOLUTIONS:
• Chatbots - from Rp 5.000.000
• Business Automation - from Rp 15.000.000

Would you be open to a free consultation?

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital
WhatsApp: wa.me/6281337558787
"
    ],
    
    'proposal' => [
        'subject' => 'Partnership Proposal - MAHA LAKSHMI Digital',
        'body' => "
Hi [NAME],

Thank you for your interest in MAHA LAKSHMI Digital!

Please find our partnership proposal attached.

SUMMARY:
• Services: Software, Marketing, AI, E-Commerce
• Commission: 15% for referrals
• Payment: Invoice-based
• Support: Dedicated account manager

NEXT STEPS:
1. Review proposal
2. Schedule call (30 minutes)
3. Sign agreement
4. Start collaboration

Are you available for a call this week?

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital
WhatsApp: wa.me/6281337558787
"
    ]
];

// =======================
// CLI PARSING
// =======================
$options = getopt('', ['lead::', 'all', 'type::', 'dry-run', 'help']);

if (isset($options['help'])) {
    showHelp();
    exit;
}

$type = $options['type'] ?? 'outreach';
$dry_run = isset($options['dry-run']);

// =======================
// MAIN EXECUTION
// =======================
echo "🤖 Email Auto-Send Script\n";
echo "========================================\n\n";

// Load leads
$leads_file = 'archives/LEADS-DATABASE.json';
if (!file_exists($leads_file)) {
    echo "❌ Leads file not found: $leads_file\n";
    exit(1);
}

$leads_data = json_decode(file_get_contents($leads_file), true);
$leads = $leads_data['leads'] ?? [];

echo "📊 Total Leads: " . count($leads) . "\n";
echo "📧 Email Type: $type\n";
echo "🔍 Mode: " . ($dry_run ? "DRY RUN (No emails sent)" : "LIVE") . "\n\n";

// Process leads
if (isset($options['lead'])) {
    $lead_id = $options['lead'];
    $lead = findLead($leads, $lead_id);
    if ($lead) {
        sendEmail($lead, $type, $dry_run);
    } else {
        echo "❌ Lead not found: $lead_id\n";
    }
}
elseif (isset($options['all'])) {
    echo "📤 Sending to ALL leads...\n";
    echo "------------------------------------------\n";
    $count = 0;
    foreach ($leads as $lead) {
        $email = $lead['email'] ?? '';
        if (!empty($email) && filter_var($email, FILTER_VALIDATE_EMAIL)) {
            sendEmail($lead, $type, $dry_run);
            $count++;
            sleep(3); // Delay to avoid rate limit
        }
    }
    echo "\n📊 Total emails prepared: $count\n";
}
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

function sendEmail($lead, $type, $dry_run) {
    global $TEMPLATES, $SMTP;
    
    $name = $lead['name'] ?? 'there';
    $email = $lead['email'] ?? '';
    $company = $lead['company'] ?? 'your company';
    
    // Get template
    $template = $TEMPLATES[$type] ?? $TEMPLATES['outreach'];
    
    // Replace placeholders
    $subject = str_replace('[NAME]', explode(' ', $name)[0], $template['subject']);
    $subject = str_replace('[COMPANY]', $company, $subject);
    
    $body = str_replace('[NAME]', explode(' ', $name)[0], $template['body']);
    $body = str_replace('[COMPANY]', $company, $body);
    
    echo "📧 To: $name <$email>\n";
    echo "   📋 Subject: $subject\n";
    
    if ($dry_run) {
        echo "   [DRY RUN] Email preview:\n";
        echo "   " . substr($body, 0, 100) . "...\n";
    } else {
        // Send email
        $result = smtpMail($email, $subject, $body);
        
        if ($result) {
            echo "   ✅ Sent successfully!\n";
            logEmail($lead, $type, 'SENT');
        } else {
            echo "   ❌ Failed to send\n";
            logEmail($lead, $type, 'FAILED');
        }
    }
    
    echo "\n";
}

function smtpMail($to, $subject, $body) {
    global $SMTP;
    
    // For simple implementation, use PHP mail()
    // For production, use PHPMailer or SwiftMailer
    
    $headers = [
        'From: ' . $SMTP['from_name'] . ' <' . $SMTP['from_email'] . '>',
        'Reply-To: ' . $SMTP['from_email'],
        'X-Mailer: PHP/' . phpversion(),
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8'
    ];
    
    $header_string = implode("\r\n", $headers);
    
    // Try mail() first (works if server configured)
    $result = mail($to, $subject, $body, $header_string);
    
    if ($result) {
        return true;
    }
    
    // Alternative: Use SMTP directly (requires socket)
    return smtpSend($to, $subject, $body);
}

function smtpSend($to, $subject, $body) {
    global $SMTP;
    
    $host = $SMTP['host'];
    $port = $SMTP['port'];
    $username = $SMTP['username'];
    $password = $SMTP['password'];
    
    // Connect to SMTP
    $socket = fsockopen($host, $port, $errno, $errstr, 30);
    
    if (!$socket) {
        echo "   ⚠️ SMTP connection failed: $errstr ($errno)\n";
        echo "   💡 Tip: Install PHPMailer for better SMTP support\n";
        return false;
    }
    
    // Read greeting
    $response = fgets($socket, 515);
    
    // Send EHLO
    fputs($socket, "EHLO " . gethostname() . "\r\n");
    $response = fgets($socket, 515);
    
    // Start TLS
    fputs($socket, "STARTTLS\r\n");
    $response = fgets($socket, 515);
    
    stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT);
    
    // EHLO again
    fputs($socket, "EHLO " . gethostname() . "\r\n");
    $response = fgets($socket, 515);
    
    // Auth
    fputs($socket, "AUTH LOGIN\r\n");
    fgets($socket, 515);
    
    fputs($socket, base64_encode($username) . "\r\n");
    fgets($socket, 515);
    
    fputs($socket, base64_encode($password) . "\r\n");
    $response = fgets($socket, 515);
    
    if (strpos($response, '235') === false) {
        echo "   ⚠️ SMTP auth failed\n";
        fclose($socket);
        return false;
    }
    
    // MAIL FROM
    fputs($socket, "MAIL FROM: <" . $SMTP['from_email'] . ">\r\n");
    fgets($socket, 515);
    
    // RCPT TO
    fputs($socket, "RCPT TO: <$to>\r\n");
    fgets($socket, 515);
    
    // DATA
    fputs($socket, "DATA\r\n");
    fgets($socket, 515);
    
    // Send email content
    $message = "From: " . $SMTP['from_name'] . " <" . $SMTP['from_email'] . ">\r\n";
    $message .= "To: $to\r\n";
    $message .= "Subject: $subject\r\n";
    $message .= "MIME-Version: 1.0\r\n";
    $message .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $message .= "\r\n";
    $message .= $body . "\r\n";
    $message .= ".\r\n";
    
    fputs($socket, $message);
    $response = fgets($socket, 515);
    
    // QUIT
    fputs($socket, "QUIT\r\n");
    fclose($socket);
    
    return (strpos($response, '250') !== false);
}

function logEmail($lead, $type, $status) {
    $log = date('Y-m-d H:i:s') . " | $status | $type | " . ($lead['name'] ?? 'Unknown') . " | " . ($lead['email'] ?? '') . "\n";
    file_put_contents('email-send-log.txt', $log, FILE_APPEND);
}

function showLeadStatus($leads) {
    echo "📊 LEADS WITH EMAIL\n";
    echo "========================================\n\n";
    
    $with_email = 0;
    $without_email = 0;
    
    foreach ($leads as $lead) {
        $email = $lead['email'] ?? '';
        if (!empty($email) && filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $with_email++;
            echo sprintf("%-3d. %-30s | %s\n", $lead['id'], $lead['name'], $email);
        } else {
            $without_email++;
        }
    }
    
    echo "\n📊 Summary:\n";
    echo "   ✅ With email: $with_email\n";
    echo "   ⚠️  Without email: $without_email\n\n";
    
    echo "📝 Usage:\n";
    echo "   php email-send.php --lead=1          Send to lead ID 1\n";
    echo "   php email-send.php --all             Send to all leads\n";
    echo "   php email-send.php --all --dry-run  Preview only\n";
    echo "   php email-send.php --type=followup  Send follow-up\n";
}

function showHelp() {
    echo "
🤖 Email Auto-Send Script
========================================

USAGE:
  php email-send.php [OPTIONS]

OPTIONS:
  --lead=ID      Send to specific lead ID
  --all           Send to all leads
  --type=TYPE     Email type (outreach, followup, final, bali_travel, tech)
  --dry-run       Preview without sending
  --help          Show this help

EXAMPLES:
  php email-send.php --help
  php email-send.php --lead=1 --dry-run
  php email-send.php --all --type=outreach
  php email-send.php --all --type=followup

EMAIL TYPES:
  outreach      - Initial outreach email
  followup      - Follow-up email (Day 3-7)
  final        - Final follow-up (Day 14)
  bali_travel  - Bali Travel partnership
  tech         - Tech solutions offer
  proposal     - Partnership proposal

";
}
