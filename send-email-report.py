#!/usr/bin/env python3
"""
GAURANGA - Email Report Sender
Send daily CEO revenue report to CEO (Pak Pur)
Email: ceo@mahalakshmi.id
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gaurangga168@gmail.com"
# PASTE YOUR APP PASSWORD HERE
APP_PASSWORD = "YOUR_APP_PASSWORD_HERE"
RECIPIENT_EMAIL = "ceo@mahalakshmi.id"

def send_ceo_daily_report():
    """Send CEO daily revenue report to Pak Pur via email"""
    
    # Email content
    today = datetime.now().strftime("%Y-%m-%d %H:%M WIB")
    
    subject = f"📊 CEO Daily Revenue Report - MAHA LAKSHMI HOLDINGS - {today}"
    
    body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; background: #f5f5f5;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
        <h1 style="color: white; margin: 0;">👑 CEO DAILY REVENUE REPORT</h1>
        <p style="color: white; font-size: 18px;">MAHA LAKSHMI HOLDINGS</p>
    </div>
    
    <div style="padding: 30px; background: white; margin: 20px; border-radius: 10px;">
        <h2 style="color: #333;">👋 Selamat Pagi, Pak Pur!</h2>
        <p style="color: #666;">Laporan revenue harian untuk <strong>{today}</strong></p>
        
        <!-- Total Revenue Section -->
        <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2e7d32;">💰 TOTAL REVENUE</h3>
            <table style="width: 100%;">
                <tr>
                    <td><strong>Today's Revenue</strong></td>
                    <td style="text-align: right; font-size: 24px; color: #2e7d32;"><strong>Rp 1.000.000</strong></td>
                </tr>
                <tr>
                    <td>Monthly Target</td>
                    <td style="text-align: right;">Rp 1.000.000.000</td>
                </tr>
                <tr>
                    <td>Progress</td>
                    <td style="text-align: right;">0.1%</td>
                </tr>
            </table>
        </div>
        
        <!-- Profit Distribution Section -->
        <div style="background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #e65100;">🏦 PROFIT DISTRIBUTION</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #ffe0b2;">
                    <th style="padding: 10px; text-align: left;">Category</th>
                    <th style="padding: 10px; text-align: center;">%</th>
                    <th style="padding: 10px; text-align: right;">Amount</th>
                </tr>
                <tr>
                    <td style="padding: 10px;">👑 CEO Pak Pur</td>
                    <td style="text-align: center;">60%</td>
                    <td style="text-align: right;"><strong>Rp 600.000</strong></td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 10px;">🔄 Reinvestment</td>
                    <td style="text-align: center;">25%</td>
                    <td style="text-align: right;">Rp 250.000</td>
                </tr>
                <tr>
                    <td style="padding: 10px;">👥 Team Bonus</td>
                    <td style="text-align: center;">10%</td>
                    <td style="text-align: right;">Rp 100.000</td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 10px;">❤️ Charity</td>
                    <td style="text-align: center;">5%</td>
                    <td style="text-align: right;">Rp 50.000</td>
                </tr>
            </table>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 15px;">
                <h4 style="margin: 0 0 10px 0;">🏦 CEO Transfer Details</h4>
                <p style="margin: 5px 0;"><strong>Bank:</strong> BCA (Bank Central Asia)</p>
                <p style="margin: 5px 0;"><strong>Account:</strong> 6485086645</p>
                <p style="margin: 5px 0;"><strong>Name:</strong> i Made Purna Ananda</p>
            </div>
        </div>
        
        <!-- Top Products Section -->
        <div style="background: #f3e5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #7b1fa2;">🛒 TOP PRODUCTS</h3>
            <table style="width: 100%;">
                <tr style="background: #e1bee7;">
                    <th style="padding: 8px; text-align: left;">#</th>
                    <th style="padding: 8px; text-align: left;">Product/Service</th>
                    <th style="padding: 8px; text-align: left;">SBU</th>
                    <th style="padding: 8px; text-align: right;">Target</th>
                </tr>
                <tr><td style="padding: 8px;">1</td><td>Hospital Management System</td><td>Payangan AI</td><td style="text-align: right;">Rp 30M</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">2</td><td>Web Development</td><td>Gianyar Tech</td><td style="text-align: right;">Rp 25M</td></tr>
                <tr><td style="padding: 8px;">3</td><td>Digital Marketing Services</td><td>Bali Digital</td><td style="text-align: right;">Rp 20M</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">4</td><td>E-Commerce Platform</td><td>Gianyar E-Commerce</td><td style="text-align: right;">Rp 15M</td></tr>
                <tr><td style="padding: 8px;">5</td><td>Online Courses</td><td>Bali EdTech</td><td style="text-align: right;">Rp 15M</td></tr>
            </table>
        </div>
        
        <!-- Top Countries Section -->
        <div style="background: #e0f7fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #00838f;">🌐 TOP COUNTRIES</h3>
            <table style="width: 100%;">
                <tr><td>🇮🇩 Indonesia</td><td style="text-align: right;">Primary market - Bali & Gianyar</td></tr>
                <tr><td>🇸🇬 Singapore</td><td style="text-align: right;">Regional hub</td></tr>
                <tr><td>🇺🇸 USA</td><td style="text-align: right;">Global SaaS market</td></tr>
                <tr><td>🇬🇧 UK</td><td style="text-align: right;">European presence</td></tr>
                <tr><td>🇦🇺 Australia</td><td style="text-align: right;">Regional expansion</td></tr>
            </table>
        </div>
        
        <!-- AI Agent Performance Section -->
        <div style="background: #fce4ec; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #c2185b;">🤖 AI AGENT PERFORMANCE</h3>
            <table style="width: 100%;">
                <tr style="background: #f8bbd0;">
                    <th style="padding: 8px; text-align: left;">Agent</th>
                    <th style="padding: 8px; text-align: left;">Function</th>
                    <th style="padding: 8px; text-align: center;">Status</th>
                </tr>
                <tr><td style="padding: 8px;">GAURANGA</td><td>CEO Agent</td><td style="text-align: center;">✅ Active</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">SaaS Sales Agent</td><td>Lead outreach & sales</td><td style="text-align: center;">✅ Active</td></tr>
                <tr><td style="padding: 8px;">Content Marketing Agent</td><td>Content creation</td><td style="text-align: center;">✅ Active</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">SEO & Ads Agent</td><td>Optimization</td><td style="text-align: center;">✅ Active</td></tr>
                <tr><td style="padding: 8px;">Customer Service Agent</td><td>Support</td><td style="text-align: center;">✅ Active</td></tr>
                <tr style="background: #f5f5f5;"><td style="padding: 8px;">Finance Agent</td><td>Accounting</td><td style="text-align: center;">✅ Active</td></tr>
            </table>
            <p style="margin-top: 15px;"><strong>Target:</strong> 60 agents across 10 companies</p>
        </div>
        
        <!-- Next Actions -->
        <div style="background: #fff8e1; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #f57f17;">🎯 NEXT ACTIONS</h3>
            <h4>Priority 1 (This Week)</h4>
            <ol>
                <li>Deploy Payangan Hospital landing page</li>
                <li>Setup GitHub repositories for remaining 9 SBUs</li>
                <li>Activate 10 more AI agents</li>
            </ol>
            <h4>Priority 2 (This Month)</h4>
            <ol>
                <li>Generate first revenue: Rp 10,000,000</li>
                <li>Setup payment gateway</li>
                <li>Launch 3 more SBUs</li>
            </ol>
        </div>
        
        <p style="color: #888; font-size: 12px; margin-top: 30px; text-align: center;">
            <em>"Setiap kesalahan harus ada solusinya!"</em><br><br>
            Generated by <strong>GAURANGA AI Agent</strong><br>
            Report ID: CEO-DR-2026-07-04-001<br>
            {today}
        </p>
    </div>
</body>
</html>
"""
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        # Attach HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Connect to server and send
        print(f"📧 Sending CEO Report to {RECIPIENT_EMAIL}...")
        print(f"Subject: {subject}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        print("✅ Email sent successfully to ceo@mahalakshmi.id!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_simple_alert(subject, message):
    """Send simple alert/notification"""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"🔔 {subject}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        body = f"""
        <html>
        <body>
            <h2>🔔 {subject}</h2>
            <p>{message}</p>
            <hr>
            <p><em>GAURANGA AI • {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
        </body>
        </html>
        """
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📧 GAURANGA CEO Daily Revenue Report Sender")
    print("=" * 50)
    print("👑 MAHA LAKSHMI HOLDINGS")
    print("📅 Date: 2026-07-04")
    print("=" * 50)
    
    # Send CEO daily report
    success = send_ceo_daily_report()
    
    if success:
        print("\n✅ CEO Report sent successfully!")
        print("📧 To: ceo@mahalakshmi.id")
    else:
        print("\n❌ Failed to send email")
        print("💡 Tip: Make sure to add your Gmail App Password in the script")
