<?php
session_start();
if (!isset($_SESSION['maha_lakshmi_auth']) || $_SESSION['maha_lakshmi_auth'] !== true) {
    header('Location: login.php');
    exit;
}
// Refresh session on activity
$_SESSION['login_time'] = time();
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maha Lakshmi - Revenue Dashboard</title>
    <style>
        :root {
            --gold: #FFD700;
            --gold-dark: #B8860B;
            --purple: #6B21A8;
            --purple-light: #A855F7;
            --bg-dark: #0F0F23;
            --bg-card: #1A1A2E;
            --text: #E5E5E5;
            --success: #10B981;
            --warning: #F59E0B;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, var(--purple) 0%, #1A1A2E 100%);
            padding: 30px 40px;
            border-bottom: 3px solid var(--gold);
        }
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }
        .logo { display: flex; align-items: center; gap: 15px; }
        .logo-icon { font-size: 48px; }
        .logo-text h1 {
            font-size: 32px;
            background: linear-gradient(135deg, var(--gold) 0%, #FFF8DC 50%, var(--gold) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .logo-text p {
            color: var(--gold-dark);
            font-size: 14px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        .header-stats { display: flex; gap: 40px; }
        .header-stat { text-align: right; }
        .header-stat-label { font-size: 12px; color: #888; text-transform: uppercase; }
        .header-stat-value { font-size: 28px; font-weight: 700; color: var(--gold); }
        .main { max-width: 1400px; margin: 0 auto; padding: 30px 40px; }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255, 215, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(255, 215, 0, 0.1);
        }
        .summary-card.gold {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, var(--bg-card) 100%);
            border-color: var(--gold);
        }
        .summary-card-icon { font-size: 36px; margin-bottom: 15px; }
        .summary-card-label { font-size: 13px; color: #888; text-transform: uppercase; margin-bottom: 8px; }
        .summary-card-value { font-size: 32px; font-weight: 700; color: var(--gold); }
        .summary-card-change { font-size: 14px; margin-top: 10px; color: var(--success); }
        .section-title {
            font-size: 24px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .section-title::before {
            content: '';
            width: 5px;
            height: 30px;
            background: var(--gold);
            border-radius: 3px;
        }
        .companies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }
        .company-card {
            background: var(--bg-card);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s;
        }
        .company-card:hover {
            border-color: var(--gold);
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.1);
        }
        .company-header {
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .company-info { display: flex; align-items: center; gap: 15px; }
        .company-number {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 18px;
            color: var(--bg-dark);
        }
        .company-name { font-size: 18px; font-weight: 600; }
        .company-type { font-size: 13px; color: #888; }
        .company-status {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-active { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .status-ready { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .status-pending { background: rgba(107, 33, 168, 0.3); color: var(--purple-light); }
        .company-body { padding: 25px; }
        .revenue-bar { margin-bottom: 20px; }
        .revenue-bar-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .revenue-label { font-size: 13px; color: #888; }
        .revenue-amount { font-size: 13px; font-weight: 600; color: var(--gold); }
        .revenue-target { font-size: 13px; color: #666; margin-top: 4px; }
        .progress-bar { height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--gold-dark) 0%, var(--gold) 100%);
            border-radius: 4px;
            transition: width 1s ease;
        }
        .company-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; }
        .metric { text-align: center; padding: 15px; background: rgba(255, 255, 255, 0.02); border-radius: 10px; }
        .metric-value { font-size: 20px; font-weight: 700; color: var(--gold); }
        .metric-label { font-size: 11px; color: #666; text-transform: uppercase; margin-top: 5px; }
        .streams-section { margin-top: 40px; }
        .streams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }
        .stream-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .stream-icon { font-size: 32px; margin-bottom: 10px; }
        .stream-name { font-size: 13px; color: #888; margin-bottom: 8px; }
        .stream-value { font-size: 22px; font-weight: 700; color: var(--gold); }
        .footer { text-align: center; padding: 40px; color: #666; font-size: 13px; }
        .footer span { color: var(--gold); }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .live-indicator { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--success); }
        .live-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; animation: pulse 2s infinite; }
        @media (max-width: 768px) {
            .header-content { flex-direction: column; text-align: center; }
            .header-stats { justify-content: center; }
            .companies-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-icon">💰</span>
                <div class="logo-text">
                    <h1>Maha Lakshmi</h1>
                    <p>Revenue Intelligence Dashboard</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="header-stat">
                    <div class="header-stat-label">Total Target</div>
                    <div class="header-stat-value">Rp 1Milyar</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-label">Active</div>
                    <div class="header-stat-value">1/10</div>
                </div>
                <div class="header-stat">
                    <div class="live-indicator">
                        <span class="live-dot"></span>
                        LIVE
                    </div>
                </div>
                <button onclick="logout()" style="background: #333; color: #FFD700; border: 1px solid #FFD700; padding: 8px 16px; border-radius: 8px; cursor: pointer; margin-left: 20px;">🚪 Logout</button>
            </div>
        </div>
    </header>

    <main class="main">
        <div class="summary-grid">
            <div class="summary-card gold">
                <div class="summary-card-icon">🎯</div>
                <div class="summary-card-label">Monthly Target</div>
                <div class="summary-card-value">Rp 1.000.000.000</div>
                <div class="summary-card-change">↑ 10 Companies × Rp 100M</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-icon">📊</div>
                <div class="summary-card-label">Current Revenue</div>
                <div class="summary-card-value">Rp 100.000.000</div>
                <div class="summary-card-change">↑ 10% of target</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-icon">🏢</div>
                <div class="summary-card-label">Active Companies</div>
                <div class="summary-card-value">1</div>
                <div class="summary-card-change">10 Companies Ready</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-icon">🤖</div>
                <div class="summary-card-label">Total Agents</div>
                <div class="summary-card-value">60</div>
                <div class="summary-card-change">6 per company</div>
            </div>
        </div>

        <h2 class="section-title">Company Revenue Overview</h2>
        <div class="companies-grid">
            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">01</div>
                        <div>
                            <div class="company-name">Payangan Hospital Digital</div>
                            <div class="company-type">Healthcare SaaS</div>
                        </div>
                    </div>
                    <span class="company-status status-active">Active</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 100.000.000</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">100%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Rp 30M</div><div class="metric-label">SaaS</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">02</div>
                        <div><div class="company-name">Gianyar Tech Solutions</div><div class="company-type">IT Services & Software</div></div>
                    </div>
                    <span class="company-status status-ready">Ready</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Setup</div><div class="metric-label">Pending</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">03</div>
                        <div><div class="company-name">Bali Digital Agency</div><div class="company-type">Digital Marketing</div></div>
                    </div>
                    <span class="company-status status-ready">Ready</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Setup</div><div class="metric-label">Pending</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">04</div>
                        <div><div class="company-name">Gianyar E-Commerce Hub</div><div class="company-type">E-Commerce Platform</div></div>
                    </div>
                    <span class="company-status status-ready">Ready</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Setup</div><div class="metric-label">Pending</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">05</div>
                        <div><div class="company-name">Bali EdTech Center</div><div class="company-type">Education Technology</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q2</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">06</div>
                        <div><div class="company-name">Gianyar Finance Tech</div><div class="company-type">Fintech</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q2</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">07</div>
                        <div><div class="company-name">Bali Logistics Network</div><div class="company-type">Logistics & Delivery</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q3</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">08</div>
                        <div><div class="company-name">Gianyar Food Tech</div><div class="company-type">Food Technology</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q3</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">09</div>
                        <div><div class="company-name">Bali Travel Platform</div><div class="company-type">Travel & Tourism</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q3</div></div>
                    </div>
                </div>
            </div>

            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <div class="company-number">10</div>
                        <div><div class="company-name">Gianyar Property Tech</div><div class="company-type">Property Technology</div></div>
                    </div>
                    <span class="company-status status-pending">Pending</span>
                </div>
                <div class="company-body">
                    <div class="revenue-bar">
                        <div class="revenue-bar-header">
                            <span class="revenue-label">Monthly Progress</span>
                            <span class="revenue-amount">Rp 0</span>
                        </div>
                        <div class="progress-bar"><div class="progress-fill" style="width: 0%;"></div></div>
                        <div class="revenue-target">Target: Rp 100.000.000</div>
                    </div>
                    <div class="company-metrics">
                        <div class="metric"><div class="metric-value">6</div><div class="metric-label">Agents</div></div>
                        <div class="metric"><div class="metric-value">0%</div><div class="metric-label">Progress</div></div>
                        <div class="metric"><div class="metric-value">Queue</div><div class="metric-label">Q4</div></div>
                    </div>
                </div>
            </div>
        </div>

        <section class="streams-section">
            <h2 class="section-title">Revenue Streams Breakdown</h2>
            <div class="streams-grid">
                <div class="stream-card">
                    <div class="stream-icon">💻</div>
                    <div class="stream-name">SaaS Products</div>
                    <div class="stream-value">Rp 300M</div>
                </div>
                <div class="stream-card">
                    <div class="stream-icon">🛠️</div>
                    <div class="stream-name">Freelance Services</div>
                    <div class="stream-value">Rp 250M</div>
                </div>
                <div class="stream-card">
                    <div class="stream-icon">📚</div>
                    <div class="stream-name">Digital Products</div>
                    <div class="stream-value">Rp 200M</div>
                </div>
                <div class="stream-card">
                    <div class="stream-icon">💎</div>
                    <div class="stream-name">Consulting</div>
                    <div class="stream-value">Rp 150M</div>
                </div>
                <div class="stream-card">
                    <div class="stream-icon">🔗</div>
                    <div class="stream-name">Affiliate</div>
                    <div class="stream-value">Rp 100M</div>
                </div>
            </div>
        </section>
    </main>

    <footer class="footer">
        <p><span>Maha Lakshmi</span> - Revenue Intelligence Dashboard | Powered by <span>GAURANGA</span> AI</p>
        <p>Target: Rp 1.000.000.000/bulan dari 10 Perusahaan</p>
        <p>Last Updated: <span id="lastUpdate"></span></p>
    </footer>

    <script>
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString('id-ID', {
            day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        document.querySelectorAll('.progress-fill').forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => { bar.style.width = width; }, 500);
        });
        function logout() {
            if (confirm('Logout dari Maha Lakshmi?')) {
                window.location.href = 'login.php?logout=1';
            }
        }
    </script>
</body>
</html>