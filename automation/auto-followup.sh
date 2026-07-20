#!/bin/bash
# 🤖 AI FOLLOW-UP AGENT
# Automatically follows up with leads that haven't responded

echo "🤖 AI FOLLOW-UP AGENT STARTING..."
echo "=========================================="

# Check for leads that need follow-up
echo "📋 Checking leads for follow-up..."

# Follow-up schedule
# Day 3: First follow-up
# Day 7: Second follow-up  
# Day 14: Final follow-up

FOLLOWUP_TYPE=${1:-"check"}

case $FOLLOWUP_TYPE in
    "check")
        echo "🔍 Checking leads that need follow-up..."
        ;;
    "day3")
        echo "📅 DAY 3 FOLLOW-UP"
        ;;
    "day7")
        echo "📅 DAY 7 FOLLOW-UP"
        ;;
    "day14")
        echo "📅 DAY 14 FINAL FOLLOW-UP"
        ;;
esac

echo ""
echo "🎯 FOLLOW-UP SEQUENCE"
echo "------------------------------------------"

# Sample leads that need follow-up
SAMPLE_FOLLOWUPS=(
    "Four Seasons Resort Sayan|3|Contacted"
    "Viceroy Bali|3|Contacted"
    "AYANA Resort|7|No Response"
)

for entry in "${SAMPLE_FOLLOWUPS[@]}"; do
    IFS='|' read -r name day status <<< "$entry"
    echo "📱 Lead: $name"
    echo "   📅 Day: $day"
    echo "   📊 Status: $status"
    
    # Generate follow-up message based on day
    if [ "$day" = "3" ]; then
        MESSAGE="🏝️ Hi $name! 👋

Just following up on our partnership message!

Have you had a chance to consider the 15% commission offer?

✅ Passive income opportunity
✅ No risk, no minimum order
✅ We handle everything

Let's chat more? 
📱 wa.me/6281337558787

--
Bali Travel"
    elif [ "$day" = "7" ]; then
        MESSAGE="👋 Hi $name!

Following up again! 

15% commission partnership still available!

Quick question: Is this something your team would be interested in?

📱 wa.me/6281337558787

--
Bali Travel"
    else
        MESSAGE="⚠️ Hi $name!

This is our FINAL follow-up.

🌟 SPECIAL OFFER (This week only!):
✅ 15% commission
✅ Waived setup fee
✅ Priority booking slots

After this, we'll close the list.

📱 wa.me/6281337558787

--
Bali Travel"
    fi
    
    echo "   ✅ Follow-up #${day} message prepared"
    echo ""
done

echo "------------------------------------------"
echo "📊 FOLLOW-UP SUMMARY"
echo "=========================================="
echo "✅ Follow-ups Prepared: 3"
echo "📧 Messages Ready: 3"
echo ""
echo "⏰ Next Step: Send via WhatsApp API"
echo ""

# Log to file
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] FOLLOW-UP AGENT RAN" >> automation/followup-log.txt

echo "🤖 AI FOLLOW-UP AGENT COMPLETE!"
