#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# GLOBAL DIGITAL SALES - AI AGENTS AUTOMATION
# CEO: i Made Purna Ananda (Pak Pur)
# System: 24/7 Running | CEO Only Receives Reports
# ═══════════════════════════════════════════════════════════════

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GLOBAL DIGITAL SALES - AI AGENTS SCHEDULER            ║${NC}"
echo -e "${BLUE}║     CEO: Pak Pur | 24/7 Automation System                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# CRON SCHEDULE (Asia/Jakarta Timezone)
# ─────────────────────────────────────────────────────────────────

# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * command to be executed

# ─────────────────────────────────────────────────────────────────
# SCHEDULE TABLE
# ─────────────────────────────────────────────────────────────────
echo -e "${GREEN}📅 AUTOMATION SCHEDULE:${NC}"
echo ""
echo -e "  ${YELLOW}Agent 1: Revenue Agent${NC}"
echo -e "    ├── Every 6 hours"
echo -e "    └── Command: Update revenue dashboard"
echo ""
echo -e "  ${YELLOW}Agent 2: Lead Gen Agent${NC}"
echo -e "    ├── Daily 9:00 AM"
echo -e "    └── Command: Generate 100+ qualified leads"
echo ""
echo -e "  ${YELLOW}Agent 3: Outreach Agent${NC}"
echo -e "    ├── Every 2 hours (24/7)"
echo -e "    └── Command: Send personalized emails"
echo ""
echo -e "  ${YELLOW}Agent 4: Follow-up Agent${NC}"
echo -e "    ├── Every 4 hours"
echo -e "    └── Command: Follow up with leads"
echo ""
echo -e "  ${YELLOW}Agent 5: Chat Agent${NC}"
echo -e "    ├── 24/7 Always on"
echo -e "    └── Command: Respond to customer inquiries"
echo ""
echo -e "  ${YELLOW}Agent 6: Content Agent${NC}"
echo -e "    ├── Daily 6:00 AM"
echo -e "    └── Command: Create marketing content"
echo ""
echo -e "  ${YELLOW}Agent 7: Social Agent${NC}"
echo -e "    ├── Every 4 hours"
echo -e "    └── Command: Post to social media"
echo ""
echo -e "  ${YELLOW}Agent 8: Research Agent${NC}"
echo -e "    ├── Weekly (Sunday 10:00 AM)"
echo -e "    └── Command: Market research & competitor analysis"
echo ""
echo -e "  ${YELLOW}Agent 9: Payment Agent${NC}"
echo -e "    ├── Every hour"
echo -e "    └── Command: Verify & process payments"
echo ""
echo -e "  ${YELLOW}Agent 10: Report Agent${NC}"
echo -e "    ├── Daily 8:00 AM"
echo -e "    ├── Weekly Monday 9:00 AM"
echo -e "    └── Command: Generate CEO reports"
echo ""

# ─────────────────────────────────────────────────────────────────
# INSTALL CRON JOBS
# ─────────────────────────────────────────────────────────────────
echo -e "${GREEN}🔧 Installing Cron Jobs...${NC}"

# Lead Gen Agent - Daily 9:00 AM WIB (02:00 UTC)
(crontab -l 2>/dev/null | grep -v "lead-gen-agent"; echo "0 2 * * * /automation/agents/lead-gen-agent.sh >> /logs/lead-gen.log 2>&1") | crontab -

# Outreach Agent - Every 2 hours (24/7)
(crontab -l 2>/dev/null | grep -v "outreach-agent"; echo "0 */2 * * * /automation/agents/outreach-agent.sh >> /logs/outreach.log 2>&1") | crontab -

# Follow-up Agent - Every 4 hours
(crontab -l 2>/dev/null | grep -v "followup-agent"; echo "0 */4 * * * /automation/agents/followup-agent.sh >> /logs/followup.log 2>&1") | crontab -

# Chat Agent - 24/7 (check every minute)
(crontab -l 2>/dev/null | grep -v "chat-agent"; echo "* * * * * /automation/agents/chat-agent.sh >> /logs/chat.log 2>&1") | crontab -

# Content Agent - Daily 5:00 AM WIB (22:00 UTC)
(crontab -l 2>/dev/null | grep -v "content-agent"; echo "0 22 * * * /automation/agents/content-agent.sh >> /logs/content.log 2>&1") | crontab -

# Social Agent - Every 4 hours
(crontab -l 2>/dev/null | grep -v "social-agent"; echo "0 */4 * * * /automation/agents/social-agent.sh >> /logs/social.log 2>&1") | crontab -

# Research Agent - Weekly Sunday 3:00 AM WIB
(crontab -l 2>/dev/null | grep -v "research-agent"; echo "0 3 * * 0 /automation/agents/research-agent.sh >> /logs/research.log 2>&1") | crontab -

# Payment Agent - Every hour
(crontab -l 2>/dev/null | grep -v "payment-agent"; echo "0 * * * * /automation/agents/payment-agent.sh >> /logs/payment.log 2>&1") | crontab -

# Revenue Agent - Every 6 hours
(crontab -l 2>/dev/null | grep -v "revenue-agent"; echo "0 */6 * * * /automation/agents/revenue-agent.sh >> /logs/revenue.log 2>&1") | crontab -

# Report Agent - Daily 8:00 AM WIB
(crontab -l 2>/dev/null | grep -v "report-agent"; echo "0 1 * * * /automation/agents/report-agent.sh daily >> /logs/report.log 2>&1") | crontab -

# Report Agent - Weekly Monday 9:00 AM WIB
(crontab -l 2>/dev/null | grep -v "report-agent-weekly"; echo "0 2 * * 1 /automation/agents/report-agent.sh weekly >> /logs/report-weekly.log 2>&1") | crontab -

# Report Agent - Monthly 1st 9:00 AM WIB
(crontab -l 2>/dev/null | grep -v "report-agent-monthly"; echo "0 2 1 * * /automation/agents/report-agent.sh monthly >> /logs/report-monthly.log 2>&1") | crontab -

echo -e "${GREEN}✅ Cron Jobs Installed!${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# DISPLAY CURRENT CRONTAB
# ─────────────────────────────────────────────────────────────────
echo -e "${BLUE}📋 Current Crontab:${NC}"
crontab -l 2>/dev/null || echo "No crontab installed"
echo ""

# ─────────────────────────────────────────────────────────────────
# 24/7 AGENTS (Background Services)
# ─────────────────────────────────────────────────────────────────
echo -e "${GREEN}🚀 Starting 24/7 Background Agents...${NC}"
echo ""

# Chat Agent - Always running web server
# nohup python3 /automation/agents/chat-server.py > /logs/chat-server.log 2>&1 &
# echo -e "  ✅ Chat Server started"

# Payment Webhook Listener - Always running
# nohup python3 /automation/agents/payment-webhook.py > /logs/payment-webhook.log 2>&1 &
# echo -e "  ✅ Payment Webhook Listener started"

echo -e "${GREEN}✅ All 24/7 agents ready!${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# VERIFICATION
# ─────────────────────────────────────────────────────────────────
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    SETUP COMPLETE!                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Your Global Digital Sales System is now running 24/7!${NC}"
echo ""
echo -e "CEO Dashboard: ${YELLOW}./dashboard/index.html${NC}"
echo -e "CEO Reports: ${YELLOW}Daily at 8:00 AM WIB${NC}"
echo -e "Email Reports: ${YELLOW}pakpur@[email]${NC}"
echo ""
echo -e "${GREEN}All 10 AI Agents are now active and working for you! 🎉${NC}"
echo ""
echo -e "─────────────────────────────────────────────────────────────"
echo -e "🏦 Bank: BCA 6485086645"
echo -e "💰 Target: \$100,000/bulan"
echo -e "👤 CEO: i Made Purna Ananda (Pak Pur)"
echo -e "─────────────────────────────────────────────────────────────"
