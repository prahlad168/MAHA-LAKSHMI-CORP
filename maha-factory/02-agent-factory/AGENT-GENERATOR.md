# 🤖 AGENT GENERATOR FACTORY
## "Generate Any Agent in Minutes"

**Version:** 1.0.0
**Created:** 2026-07-03
**Module:** 02 - Agent Generator

---

## 🎯 PURPOSE

Agent Generator menerima input sederhana dan menghasilkan Agent lengkap dengan semua komponen yang dibutuhkan.

**Input:** Nama + Departemen + Tugas + Target + KPI + Security
**Output:** Agent Profile + DNA + Prompts + SOPs + Workflows + Dashboard + Reports

---

## 📥 INPUT SPECIFICATION

### Minimal Input
```yaml
minimal_input:
  name: "SEO Agent"                    # Required
  department: "marketing"               # Required
  tasks:                               # Required (min 1)
    - "keyword_research"
  targets:                             # Required (min 1)
    - "monthly_leads: 100"
  kpis:                               # Required (min 1)
    - "keyword_rankings"
  security_level: "internal"          # Required
```

### Full Input
```yaml
full_input:
  name: "SEO Agent"
  department: "marketing"
  industry: "saas"
  tasks:
    - "keyword_research"
    - "content_optimization"
    - "link_building"
    - "technical_audit"
    - "competitor_analysis"
  targets:
    monthly_leads: 100
    organic_traffic_growth: "50%"
    keyword_rankings_top10: 50
  kpis:
    - "keyword_rankings"
    - "organic_traffic"
    - "domain_authority"
    - "backlinks_count"
    - "page_speed_score"
  security_level: "internal"
  tools:
    - "semrush"
    - "ahrefs"
    - "google_analytics"
    - "google_search_console"
  integrations:
    - "google_analytics"
    - "search_console"
  communication_style: "professional"
  language: "id"
  escalation_rules:
    - "unresolved_seo_issues > 5"
    - "ranking_drop > 20%"
```

---

## 🔧 GENERATION PROCESS

### Step 1: Input Validation
```python
def validate_input(input_data):
    """
    Validates all required fields are present and valid.
    
    Checks:
    - Name is not empty
    - Department exists in list
    - At least 1 task defined
    - At least 1 KPI defined
    - Security level is valid
    """
    errors = []
    if not input_data.get('name'):
        errors.append("Agent name is required")
    if not input_data.get('department'):
        errors.append("Department is required")
    if not input_data.get('tasks'):
        errors.append("At least 1 task is required")
    if not input_data.get('kpis'):
        errors.append("At least 1 KPI is required")
    
    return {"valid": len(errors) == 0, "errors": errors}
```

### Step 2: Agent Profile Generation
```python
def generate_agent_profile(input_data):
    """
    Generates comprehensive agent profile.
    
    Output: Markdown document with full agent specification
    """
    profile = {
        "agent_id": generate_agent_id(input_data['name']),
        "name": input_data['name'],
        "department": input_data['department'],
        "role": determine_role(input_data),
        "mission": generate_mission(input_data),
        "responsibilities": generate_responsibilities(input_data['tasks']),
        "authority": generate_authority(input_data['security_level']),
        "reporting": generate_reporting_structure(input_data)
    }
    return markdown_format(profile)
```

### Step 3: Agent DNA Generation
```python
def generate_agent_dna(input_data):
    """
    Generates agent DNA - configuration file for agent behavior.
    
    Output: JSON configuration
    """
    dna = {
        "agent_id": generate_agent_id(input_data['name']),
        "version": "1.0.0",
        "classification": {
            "type": classify_agent_type(input_data),
            "level": determine_autonomy_level(input_data),
            "security": input_data['security_level']
        },
        "capabilities": {
            "skills": match_skills(input_data['tasks']),
            "tools": input_data.get('tools', []),
            "apis": map_required_apis(input_data)
        },
        "configuration": {
            "autonomy_level": determine_autonomy_level(input_data),
            "escalation_threshold": input_data.get('escalation', 'medium'),
            "communication_style": input_data.get('communication_style', 'professional'),
            "language": input_data.get('language', 'id')
        },
        "targets": input_data.get('targets', {}),
        "kpis": input_data.get('kpis', []),
        "lifecycle": {
            "created": get_current_date(),
            "status": "generated"
        }
    }
    return json_format(dna)
```

---

## 📋 OUTPUT TEMPLATES

### Agent Profile Template
```markdown
# 🤖 {AGENT_NAME}

**Agent ID:** `{agent_id}`
**Department:** `{department}`
**Version:** `{version}`
**Created:** `{date}`
**Status:** 🟡 Generated

---

## 🎯 MISSION

{Mission statement based on tasks and targets}

---

## 📋 RESPONSIBILITIES

| No | Task | Priority | SLA |
|----|------|----------|-----|
| 1 | {task_1} | High | Daily |
| 2 | {task_2} | Medium | Weekly |
| ... | ... | ... | ... |

---

## 🎯 TARGETS & KPIs

### Targets
| Metric | Target | Current |
|--------|--------|---------|
| {target_1} | {value} | - |
| {target_2} | {value} | - |

### KPIs
| KPI | Weight | Measurement |
|-----|--------|-------------|
| {kpi_1} | 30% | Weekly |
| {kpi_2} | 25% | Monthly |

---

## 🛠️ TOOLS & INTEGRATIONS

### Tools
- {tool_1}
- {tool_2}

### Integrations
- {integration_1}
- {integration_2}

---

## 🔒 SECURITY & ACCESS

- **Security Level:** {security_level}
- **Data Access:** {access_level}
- **Escalation:** {escalation_rules}

---

## 📊 REPORTING

- **Reports To:** {manager}
- **Report Frequency:** {frequency}
- **Dashboard:** {dashboard_url}
```

### Agent DNA Template
```json
{
  "agent_id": "{agent_id}",
  "name": "{agent_name}",
  "version": "1.0.0",
  "department": "{department}",
  "classification": {
    "type": "{agent_type}",
    "level": "{autonomy_level}",
    "security": "{security_level}"
  },
  "capabilities": {
    "skills": ["{skill_1}", "{skill_2}"],
    "tools": ["{tool_1}", "{tool_2}"],
    "apis": ["{api_1}", "{api_2}"]
  },
  "tasks": [
    {
      "id": "task_001",
      "name": "{task_name}",
      "priority": "high|medium|low",
      "frequency": "daily|weekly|monthly",
      "sla": "{sla_duration}"
    }
  ],
  "targets": {
    "{metric}": "{value}"
  },
  "kpis": [
    {
      "name": "{kpi_name}",
      "weight": 0.30,
      "measurement": "weekly|monthly",
      "target": "{target_value}"
    }
  ],
  "configuration": {
    "autonomy_level": "high|medium|low",
    "escalation_threshold": "{threshold}",
    "communication_style": "{style}",
    "language": "{language}"
  },
  "lifecycle": {
    "created": "{date}",
    "tested": null,
    "deployed": null,
    "last_improved": null
  },
  "metrics": {
    "accuracy": 0,
    "quality": 0,
    "speed": 0,
    "revenue_generated": 0
  }
}
```

---

## 🔄 GENERATION FLOW

```
INPUT RECEIVED
    │
    ▼
┌───────────────────────┐
│ 1. VALIDATE INPUT     │
│    Check all fields  │
└───────────────────────┘
    │ Valid
    ▼
┌───────────────────────┐
│ 2. GENERATE ID        │
│    agent-id-v1        │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 3. MATCH SKILLS       │
│    From Skill Library │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 4. GENERATE PROFILE   │
│    Markdown format     │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 5. GENERATE DNA       │
│    JSON config        │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 6. GENERATE PROMPTS   │
│    Role + Task + QA   │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 7. GENERATE SOPS      │
│    Standard Procedures │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 8. GENERATE WORKFLOW  │
│    Task workflows     │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 9. GENERATE DASHBOARD │
│    HTML dashboard     │
└───────────────────────┘
    │
    ▼
┌───────────────────────┐
│ 10. GENERATE REPORTS  │
│     Report templates  │
└───────────────────────┘
    │
    ▼
GENERATED AGENT ✅
```

---

## 📁 OUTPUT FILE STRUCTURE

```
agents/{agent-name}/
├── 01-agent-profile.md          # Full agent specification
├── 02-agent-dna.json            # Agent configuration
├── 03-prompts/
│   ├── 01-role-prompt.md       # Main role prompt
│   ├── 02-task-prompts.md     # Task-specific prompts
│   ├── 03-review-prompt.md     # Self-review prompt
│   ├── 04-qa-prompt.md         # Quality assurance prompt
│   └── 05-report-prompt.md     # Report generation prompt
├── 04-sops/
│   ├── 01-main-sop.md          # Main SOP
│   └── 02-task-sops/
│       ├── task-001.md
│       └── task-002.md
├── 05-workflows/
│   └── workflows.json          # All workflows
├── 06-dashboard/
│   └── dashboard.html          # Agent dashboard
├── 07-reports/
│   └── templates/
│       ├── daily-report.md
│       ├── weekly-report.md
│       └── monthly-report.md
└── 08-knowledge/
    └── knowledge-base.md       # Agent knowledge
```

---

## 🧬 AGENT ID GENERATION

```python
def generate_agent_id(agent_name):
    """
    Generates unique agent ID from name.
    
    Rules:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters
    - Add version suffix
    """
    import re
    import uuid
    
    # Clean name
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', agent_name)
    slug = clean_name.lower().replace(' ', '-')
    
    # Generate short UUID
    short_uuid = uuid.uuid4().hex[:6]
    
    return f"{slug}-{short_uuid}"
    
# Examples:
# "SEO Agent" → "seo-agent-a1b2c3"
# "HR Manager" → "hr-manager-x1y2z3"
# "Hospital Patient Agent" → "hospital-patient-agent-m5n6o7"
```

---

## 🎯 ROLE DETERMINATION

```python
def determine_role(input_data):
    """
    Determines agent role based on tasks and department.
    """
    department = input_data.get('department', '')
    tasks = input_data.get('tasks', [])
    
    role_mapping = {
        'sales': {
            'lead_generation': 'Sales Development Rep',
            'closing': 'Account Executive',
            'account_management': 'Account Manager'
        },
        'marketing': {
            'content': 'Content Marketer',
            'seo': 'SEO Specialist',
            'social_media': 'Social Media Manager',
            'ads': 'Paid Media Specialist'
        },
        'hr': {
            'recruitment': 'Recruiter',
            'onboarding': 'Onboarding Specialist',
            'training': 'Training Coordinator'
        },
        'finance': {
            'invoicing': 'Accounts Receivable',
            'bookkeeping': 'Bookkeeper',
            'reporting': 'Financial Analyst'
        },
        'operations': {
            'project_management': 'Project Manager',
            'quality': 'QA Specialist',
            'support': 'Operations Manager'
        }
    }
    
    # Determine primary role
    primary_task = tasks[0] if tasks else 'general'
    
    return role_mapping.get(department, {}).get(primary_task, 'General Agent')
```

---

## 🔧 SKILL MATCHING

```python
def match_skills(tasks):
    """
    Matches required skills from skill library based on tasks.
    """
    skill_map = {
        'keyword_research': ['seo', 'analytics', 'research'],
        'content_optimization': ['content_writing', 'seo', 'copywriting'],
        'link_building': ['outreach', 'seo', 'networking'],
        'technical_audit': ['technical_seo', 'web_development', 'analytics'],
        'competitor_analysis': ['market_research', 'analytics', 'reporting'],
        'recruitment': ['hr', 'interviewing', 'communication'],
        'onboarding': ['hr', 'training', 'documentation'],
        'invoicing': ['finance', 'accounting', 'documentation'],
        'bookkeeping': ['finance', 'accounting', 'data_entry'],
        'project_management': ['project_management', 'coordination', 'reporting']
    }
    
    skills = set()
    for task in tasks:
        if task in skill_map:
            skills.update(skill_map[task])
    
    return list(skills)
```

---

## 📊 METRICS & TRACKING

| Metric | Description | Target |
|--------|-------------|--------|
| generation_time | Time to generate complete agent | < 5 min |
| completeness | % of required fields generated | 100% |
| test_pass_rate | Validation test pass rate | > 95% |
| deployment_success | Successful deployment rate | 100% |

---

## 🚀 USAGE EXAMPLES

### Example 1: Generate SEO Agent
```markdown
# Input
name: "SEO Agent"
department: "marketing"
tasks:
  - keyword_research
  - content_optimization
  - link_building
targets:
  monthly_leads: 100
  organic_traffic: "+50%"
kpis:
  - keyword_rankings
  - organic_traffic
  - domain_authority
security_level: "internal"
```

### Example 2: Generate HR Agent
```markdown
# Input
name: "HR Agent"
department: "hr"
tasks:
  - recruitment
  - onboarding
  - performance_review
targets:
  hire_time: "< 30 days"
  retention_rate: "> 90%"
kpis:
  - time_to_hire
  - retention
  - satisfaction_score
security_level: "confidential"
```

### Example 3: Generate Hospital Agent
```markdown
# Input
name: "Hospital Registration Agent"
department: "healthcare"
tasks:
  - patient_registration
  - appointment_scheduling
  - medical_records
targets:
  wait_time: "< 15 minutes"
  accuracy: "> 99%"
kpis:
  - patient_satisfaction
  - registration_time
  - error_rate
security_level: "restricted"
```

---

**Document Version:** 1.0.0
**Created:** 2026-07-03
**Status:** 🚀 ACTIVE
**Module:** 02 - Agent Generator Factory
