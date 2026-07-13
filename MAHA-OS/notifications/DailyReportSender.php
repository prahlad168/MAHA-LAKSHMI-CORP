<?php
/**
 * MAHA LAKSHMI AIOS - Daily Report Sender
 * Sends daily report to CEO
 * CEO: ceo@mahalakshmi.id | WhatsApp: 081337558787
 * Created: 2026-07-03
 */

// CEO Contact Info
define('CEO_EMAIL', 'ceo@mahalakshmi.id');
define('CEO_PHONE', '081337558787');
define('CEO_WHATSAPP', '6281337558787');

/**
 * Generate daily report data
 */
function generateDailyReport(): array {
    $totalTasks = 64;
    $completedTasks = 4; // Current count
    
    return [
        'date' => date('Y-m-d'),
        'time' => date('H:i') . ' WIB',
        'revenue' => 'Rp 0',
        'revenue_raw' => 0,
        'leads' => 0,
        'tasks_completed' => $completedTasks,
        'total_tasks' => $totalTasks,
        'progress_percent' => round(($completedTasks / $totalTasks) * 100, 1),
        'achievements' => [
            'Task #0001 Database Foundation selesai',
            'Task #0002 Authentication System selesai',
            'Task #0007 AI Agent Template selesai',
            'Task #0008 CRM Database Schema selesai'
        ],
        'tomorrow_plan' => [
            'Start Task #0003 - Company Module',
            'Setup GitHub automation',
            'Deploy notification system'
        ],
        'blockers' => [],
        'active_companies' => 10,
        'ai_agents' => 6,
        'automations' => 6
    ];
}

/**
 * Send email report
 */
function sendEmailReport(string $to, array $report): array {
    $subject = "📊 Laporan Harian MAHA - " . date('d M Y');
    
    $achievementsList = '';
    foreach ($report['achievements'] as $a) {
        $achievementsList .= "<li>✅ $a</li>";
    }
    
    $planList = '';
    foreach ($report['tomorrow_plan'] as $p) {
        $planList .= "<li>📌 $p</li>";
    }
    
    $html = <<<HTML
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #1a5f5a, #0d3d3a); color: white; padding: 25px; text-align: center; }
        .header h1 { margin: 0 0 5px; font-size: 1.5rem; }
        .content { padding: 25px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
        .kpi-card { background: #f8fafc; border-radius: 10px; padding: 15px; text-align: center; }
        .kpi-value { font-size: 1.5rem; font-weight: bold; color: #1a5f5a; }
        .kpi-label { font-size: 0.8rem; color: #64748b; margin-top: 5px; }
        .section { margin-bottom: 20px; }
        .section h3 { color: #1e293b; font-size: 1rem; margin-bottom: 10px; border-bottom: 2px solid #1a5f5a; padding-bottom: 5px; }
        ul { list-style: none; padding: 0; margin: 0; }
        li { padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
        .progress-bar { background: #e2e8f0; height: 12px; border-radius: 6px; overflow: hidden; }
        .progress-fill { background: linear-gradient(90deg, #1a5f5a, #22c55e); height: 100%; }
        .footer { background: #f8fafc; padding: 15px; text-align: center; font-size: 0.8rem; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Laporan Harian MAHA AIOS</h1>
            <p>{$report['date']} • {$report['time']}</p>
        </div>
        <div class="content">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{$report['revenue']}</div>
                    <div class="kpi-label">💰 Revenue Hari Ini</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{$report['leads']}</div>
                    <div class="kpi-label">🎯 Leads Baru</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{$report['tasks_completed']}</div>
                    <div class="kpi-label">✅ Tasks Selesai</div>
                </div>
            </div>
            <div class="section">
                <h3>📋 Progress AIOS (64 Tasks)</h3>
                <p><strong>{$report['progress_percent']}% Complete</strong></p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {$report['progress_percent']}%"></div>
                </div>
            </div>
            <div class="section">
                <h3>🎉 Achievements</h3>
                <ul>{$achievementsList}</ul>
            </div>
            <div class="section">
                <h3>📅 Rencana Besok</h3>
                <ul>{$planList}</ul>
            </div>
        </div>
        <div class="footer">
            <p>🏛️ MAHA LAKSHMI HOLDINGS</p>
            <p>CEO: Prahlad | BCA: 6485086645</p>
        </div>
    </div>
</body>
</html>
HTML;
    
    // Simple mail function
    $headers = [
        'From: MAHA AIOS <noreply@mahalakshmi.id>',
        'Content-Type: text/html; charset=UTF-8',
        'MIME-Version: 1.0'
    ];
    
    $sent = mail($to, $subject, $html, implode("\r\n", $headers));
    
    return [
        'success' => $sent,
        'message' => $sent ? 'Email sent' : 'Failed to send email'
    ];
}

/**
 * Generate WhatsApp message
 */
function generateWhatsAppMessage(array $report): string {
    $msg = "📊 *LAPORAN HARIAN MAHA*\n";
    $msg .= "─────────────────\n\n";
    $msg .= "💰 Revenue: {$report['revenue']}\n";
    $msg .= "🎯 Leads: {$report['leads']}\n";
    $msg .= "✅ Tasks: {$report['tasks_completed']}/{$report['total_tasks']}\n";
    $msg .= "📈 Progress: {$report['progress_percent']}%\n\n";
    $msg .= "*🎉 Achievements:*\n";
    $msg .= $report['achievements'][0] . "\n\n";
    $msg .= "*📅 Besok:*\n";
    $msg .= $report['tomorrow_plan'][0] . "\n\n";
    $msg .= "─────────────────\n";
    $msg .= "🏛️ MAHA LAKSHMI HOLDINGS\n";
    $msg .= "CEO: Prahlad | BCA: 6485086645";
    return $msg;
}

/**
 * Main function to send daily report
 */
function sendDailyReport(): array {
    $report = generateDailyReport();
    
    $result = [
        'success' => true,
        'timestamp' => date('Y-m-d H:i:s'),
        'report' => $report,
        'channels' => []
    ];
    
    // 1. Send Email
    $emailResult = sendEmailReport(CEO_EMAIL, $report);
    $result['channels']['email'] = $emailResult;
    
    // 2. WhatsApp Link (opens WhatsApp with pre-filled message)
    $waMessage = generateWhatsAppMessage($report);
    $result['channels']['whatsapp'] = [
        'success' => true,
        'link' => 'https://wa.me/' . CEO_WHATSAPP . '?text=' . urlencode($waMessage),
        'message' => $waMessage
    ];
    
    return $result;
}

// Run if called directly
if (php_sapi_name() === 'cli' || isset($_GET['run'])) {
    echo "Sending daily report...\n";
    $result = sendDailyReport();
    echo json_encode($result, JSON_PRETTY_PRINT);
}
