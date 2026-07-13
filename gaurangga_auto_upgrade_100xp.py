#!/usr/bin/env python3
"""
GAURANGA - Auto Upgrade Skills to 100 XP
All agents work until ALL skills reach 100 XP

CEO: i Made Purna Ananda
Bank: BCA 6485086645
"""

import json
import random
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
CONFIG = {
    'owner': 'i Made Purna Ananda',
    'bank': 'BCA 6485086645',
    'target_xp': 100,
    'min_improvement': 5,
    'max_improvement': 20
}

# ==================== AGENT DEFINITIONS ====================
AGENTS = {
    'gauranga_ceo': {
        'name': 'GAURANGA CEO',
        'role': 'Chief Executive Officer',
        'skills': ['strategy', 'leadership', 'decision_making', 'resource_allocation', 'risk_management']
    },
    'saas_sales': {
        'name': 'SaaS Sales Agent',
        'role': 'Software Sales',
        'skills': ['cold_outreach', 'demo_scheduling', 'negotiation', 'closing', 'crm_management']
    },
    'content_marketing': {
        'name': 'Content Marketing Agent',
        'role': 'Content Creator',
        'skills': ['seo_writing', 'video_scripting', 'social_content', 'email_copywriting', 'copywriting']
    },
    'seo_ads': {
        'name': 'SEO & Ads Agent',
        'role': 'Marketing Optimization',
        'skills': ['google_ads', 'facebook_ads', 'seo_optimization', 'keyword_research', 'conversion_optimization']
    },
    'customer_service': {
        'name': 'Customer Service Agent',
        'role': 'Customer Support',
        'skills': ['ticket_management', 'response_templates', 'escalation', 'satisfaction_survey', 'faq_management']
    },
    'finance': {
        'name': 'Finance Agent',
        'role': 'Financial Management',
        'skills': ['invoicing', 'expense_tracking', 'financial_reporting', 'tax_compliance', 'profit_calculation']
    },
    'hr_recruitment': {
        'name': 'HR & Recruitment Agent',
        'role': 'Human Resources',
        'skills': ['recruitment', 'interviewing', 'onboarding', 'performance_review', 'training']
    },
    'project_manager': {
        'name': 'Project Manager Agent',
        'role': 'Project Management',
        'skills': ['task_management', 'timeline_tracking', 'resource_allocation', 'risk_management', 'quality_control']
    },
    'social_media': {
        'name': 'Social Media Agent',
        'role': 'Social Media Management',
        'skills': ['instagram', 'tiktok', 'linkedin', 'engagement', 'community_management']
    },
    'email_marketing': {
        'name': 'Email Marketing Agent',
        'role': 'Email Campaigns',
        'skills': ['list_management', 'sequence_automation', 'ab_testing', 'segmentation', 'deliverability']
    }
}

# ==================== SKILL DATABASE ====================
class SkillDatabase:
    def __init__(self):
        self.skills_db = {}
        self.upgrade_count = 0
        self.load_skills()
    
    def load_skills(self):
        try:
            with open('gauranga-skills-db.json', 'r') as f:
                data = json.load(f)
                self.skills_db = data.get('skills', {})
        except FileNotFoundError:
            pass
    
    def save_skills(self):
        data = {
            'skills': self.skills_db,
            'total_upgrades': self.upgrade_count,
            'last_updated': datetime.now().isoformat()
        }
        with open('gauranga-skills-db.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def upgrade_skill(self, agent_id: str, skill_name: str) -> dict:
        key = f"{agent_id}_{skill_name}"
        agent = AGENTS[agent_id]
        
        # Initialize if not exists
        if key not in self.skills_db:
            self.skills_db[key] = {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'skill_name': skill_name,
                'level': 1,
                'experience': 0,
                'total_xp': 0
            }
        
        # Add XP
        xp_gain = random.randint(CONFIG['min_improvement'], CONFIG['max_improvement'])
        old_xp = self.skills_db[key]['experience']
        self.skills_db[key]['experience'] += xp_gain
        self.skills_db[key]['total_xp'] += xp_gain
        self.upgrade_count += 1
        
        # Level up if XP >= 100
        leveled_up = False
        if self.skills_db[key]['experience'] >= CONFIG['target_xp']:
            self.skills_db[key]['level'] += 1
            self.skills_db[key]['experience'] = 0
            leveled_up = True
        
        return {
            'key': key,
            'agent': agent['name'],
            'skill': skill_name,
            'xp_gain': xp_gain,
            'current_xp': self.skills_db[key]['experience'],
            'level': self.skills_db[key]['level'],
            'leveled_up': leveled_up
        }
    
    def get_all_skills(self) -> list:
        return list(self.skills_db.values())
    
    def is_all_max_level(self) -> bool:
        for skill in self.skills_db.values():
            if skill['level'] < 5:  # Max level is 5
                return False
        return len(self.skills_db) > 0


def print_header():
    print("\n" + "=" * 70)
    print("🎮 GAURANGA AUTO UPGRADE SKILLS TO 100 XP")
    print("=" * 70)
    print(f"👑 Owner: {CONFIG['owner']}")
    print(f"🏦 Bank: {CONFIG['bank']}")
    print(f"🎯 Target XP: {CONFIG['target_xp']} XP per skill")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


def print_progress_bar(current: int, total: int, width: int = 40) -> str:
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent * 100:.1f}%"


def print_skill_status(skills: list):
    """Print all skills status in a nice table"""
    print("\n📊 ALL SKILLS STATUS:")
    print("-" * 70)
    print(f"{'Agent':<25} {'Skill':<20} {'Lv':<3} {'XP':<8} {'Status'}")
    print("-" * 70)
    
    for skill in sorted(skills, key=lambda x: x['agent_name']):
        level = skill['level']
        xp = skill['experience']
        max_xp = CONFIG['target_xp']
        
        # Status based on XP
        if level >= 5:
            status = "⭐ MAX!"
        elif xp >= 80:
            status = "🔥🔥🔥 CLOSE!"
        elif xp >= 50:
            status = "🔥🔥 GOOD"
        elif xp >= 25:
            status = "🔥 OK"
        else:
            status = "○ START"
        
        print(f"{skill['agent_name']:<25} {skill['skill_name']:<20} {level:<3} {xp}/{max_xp:<6} {status}")
    
    print("-" * 70)


def main():
    print_header()
    
    # Initialize skill database
    db = SkillDatabase()
    
    # Initialize all skills if not exists
    print("\n🔧 Initializing skills...")
    for agent_id, agent in AGENTS.items():
        for skill_name in agent['skills']:
            key = f"{agent_id}_{skill_name}"
            if key not in db.skills_db:
                db.skills_db[key] = {
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'skill_name': skill_name,
                    'level': 1,
                    'experience': 0,
                    'total_xp': 0
                }
    
    db.save_skills()
    print(f"✅ {len(db.skills_db)} skills initialized!")
    
    # Count total upgrades needed
    total_skills = len(db.skills_db)
    upgrades_done = 0
    
    # Print initial status
    print_skill_status(db.get_all_skills())
    
    # Auto upgrade loop
    print("\n🚀 STARTING AUTO UPGRADE TO 100 XP...")
    print("=" * 70)
    
    iteration = 0
    max_iterations = 5000  # Safety limit
    
    while iteration < max_iterations:
        iteration += 1
        
        # Check if all skills are at max level (5)
        all_max = all(skill['level'] >= 5 for skill in db.skills_db.values())
        
        if all_max:
            print(f"\n🎉🎉🎉 ALL SKILLS REACHED MAX LEVEL 5! 🎉🎉🎉")
            break
        
        # Pick a random skill that's not at max level
        available_skills = [
            (agent_id, skill) 
            for agent_id, agent in AGENTS.items() 
            for skill in agent['skills']
            if db.skills_db.get(f"{agent_id}_{skill}", {}).get('level', 0) < 5
        ]
        
        if not available_skills:
            break
        
        # Upgrade random skill
        agent_id, skill_name = random.choice(available_skills)
        result = db.upgrade_skill(agent_id, skill_name)
        upgrades_done += 1
        
        # Print progress every 10 upgrades
        if upgrades_done % 10 == 0:
            skills = db.get_all_skills()
            
            # Calculate progress
            total_levels = sum(s['level'] for s in skills)
            max_levels = len(skills) * 5
            progress = total_levels / max_levels * 100
            
            print(f"\n📈 Progress: {print_progress_bar(total_levels, max_levels)}")
            print(f"⚡ Upgrades: {upgrades_done} | Iterations: {iteration}")
            
            # Show skills that leveled up recently
            recent_levelups = [s for s in skills if s['level'] >= 5]
            if recent_levelups:
                print(f"⭐ Maxed Skills: {len(recent_levelups)}/{total_skills}")
            
            # Show skills close to level up
            close_skills = [s for s in skills if s['experience'] >= 80 and s['level'] < 5]
            if close_skills:
                print(f"🔥 Close to level up: {len(close_skills)}")
        
        # Save periodically
        if upgrades_done % 50 == 0:
            db.save_skills()
        
        # Small delay to simulate real work
        time.sleep(0.01)
    
    # Final save
    db.save_skills()
    
    # Print final status
    print("\n" + "=" * 70)
    print("🎊 AUTO UPGRADE COMPLETE!")
    print("=" * 70)
    
    print_skill_status(db.get_all_skills())
    
    # Summary
    skills = db.get_all_skills()
    maxed_count = sum(1 for s in skills if s['level'] >= 5)
    total_levels = sum(s['level'] for s in skills)
    total_xp = sum(s['total_xp'] for s in skills)
    
    print("\n📊 FINAL SUMMARY:")
    print("-" * 70)
    print(f"  🤖 Total Agents: {len(AGENTS)}")
    print(f"  📈 Total Skills: {len(skills)}")
    print(f"  ⭐ Maxed Skills (Lv 5): {maxed_count}/{len(skills)}")
    print(f"  📊 Total Levels Gained: {total_levels}")
    print(f"  💎 Total XP Earned: {total_xp}")
    print(f"  ⚡ Total Upgrades: {upgrades_done}")
    print(f"  ⏰ Iterations: {iteration}")
    print("-" * 70)
    
    # Show per-agent summary
    print("\n👥 PER-AGENT SUMMARY:")
    print("-" * 70)
    for agent_id, agent in AGENTS.items():
        agent_skills = [s for s in skills if s['agent_id'] == agent_id]
        maxed = sum(1 for s in agent_skills if s['level'] >= 5)
        total = len(agent_skills)
        avg_level = sum(s['level'] for s in agent_skills) / total if total > 0 else 0
        
        status = "⭐" * maxed + "○" * (total - maxed)
        print(f"  {agent['name']:<25} {status:<10} Avg Lv: {avg_level:.1f}")
    
    print("\n" + "=" * 70)
    print("💪 Motto: Setiap masalah pasti ada solusinya!")
    print("🎉 All agents skills upgraded to MAX!")
    print("=" * 70)
    
    # Save final execution log
    with open('agent-execution-log.json', 'w') as f:
        json.dump({
            'type': 'full_upgrade_to_max',
            'total_upgrades': upgrades_done,
            'total_skills': len(skills),
            'maxed_skills': maxed_count,
            'completed_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print("\n✅ gauranga-skills-db.json updated!")
    print("✅ agent-execution-log.json updated!")


if __name__ == '__main__':
    main()
