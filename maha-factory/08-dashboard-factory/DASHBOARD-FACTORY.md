# 📊 DASHBOARD FACTORY
## "Every Agent Gets a Dashboard"

**Version:** 1.0.0
**Created:** 2026-07-03
**Module:** 08 - Dashboard Factory

---

## 🎯 PHILOSOPHY

**Every agent needs visibility into their own performance.**

```
Agent Created
    ↓
Dashboard Factory
    ↓
Generate Agent Dashboard
    ↓
Real-time Performance Visibility
    ↓
Continuous Improvement
```

---

## 📋 DASHBOARD COMPONENTS

```html
Agent Dashboard Structure:

┌─────────────────────────────────────────────────────────────┐
│  🤖 AGENT DASHBOARD: {Agent Name}                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Today's Tasks   │  │ Completed       │                 │
│  │      12        │  │       8         │                 │
│  │  ↑ 20%        │  │   67% done     │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Pending        │  │ Success Rate   │                 │
│  │       4        │  │     92%        │                 │
│  │   Priority     │  │   ↑ 5%        │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              KPI PROGRESS                              ││
│  │  ━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░  80%                ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              RECENT ACTIVITY                           ││
│  │  • Task 1 completed - 5 min ago                       ││
│  │  • Task 2 completed - 15 min ago                      ││
│  │  • Task 3 started - 30 min ago                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              KNOWLEDGE UPDATES                         ││
│  │  📚 New: SEO Best Practices (Updated)                 ││
│  │  📚 New: Content Optimization Guide                    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              IMPROVEMENT ACTIONS                       ││
│  │  ⚠️ Speed optimization needed                          ││
│  │  💡 Suggested: Batch similar tasks                     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 DASHBOARD TEMPLATE

```html
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Agent Name} - Dashboard</title>
    <style>
        :root {
            --primary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-dark: #1e293b;
            --bg-card: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }
        
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--bg-card);
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .header .agent-id {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .last-update {
            color: var(--text-secondary);
            font-size: 12px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: 700;
        }
        
        .stat-change {
            font-size: 12px;
            margin-top: 8px;
        }
        
        .stat-change.positive { color: var(--success); }
        .stat-change.negative { color: var(--danger); }
        
        .sections {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .section {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 600;
        }
        
        .section-badge {
            background: var(--primary);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .task-list {
            list-style: none;
        }
        
        .task-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--bg-dark);
        }
        
        .task-item:last-child {
            border-bottom: none;
        }
        
        .task-name {
            font-size: 14px;
        }
        
        .task-status {
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .status-pending {
            background: var(--warning);
            color: #000;
        }
        
        .status-completed {
            background: var(--success);
            color: #000;
        }
        
        .status-in-progress {
            background: var(--primary);
            color: #fff;
        }
        
        .progress-bar {
            width: 100%;
            height: 24px;
            background: var(--bg-dark);
            border-radius: 12px;
            overflow: hidden;
            margin: 16px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--success));
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 12px;
            font-weight: 600;
            transition: width 0.3s ease;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .kpi-item {
            background: var(--bg-dark);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        
        .kpi-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--success);
        }
        
        .kpi-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        @media (max-width: 768px) {
            .sections {
                grid-template-columns: 1fr;
            }
            
            .kpi-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <div>
                <h1>🤖 {{ agent_name }}</h1>
                <div class="agent-id">ID: {{ agent_id }}</div>
            </div>
            <div class="last-update">
                Last updated: {{ timestamp }}
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Today's Tasks</div>
                <div class="stat-value">{{ today_tasks }}</div>
                <div class="stat-change positive">↑ {{ task_growth }}% from yesterday</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Completed</div>
                <div class="stat-value">{{ completed_tasks }}</div>
                <div class="stat-change positive">{{ completion_rate }}% done</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Pending</div>
                <div class="stat-value">{{ pending_tasks }}</div>
                <div class="stat-change warning">{{ priority_pending }} priority</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{{ success_rate }}%</div>
                <div class="stat-change positive">↑ {{ rate_improvement }}%</div>
            </div>
        </div>
        
        <div class="sections">
            <div class="section full-width">
                <div class="section-header">
                    <span class="section-title">📊 KPI Progress</span>
                    <span class="section-badge">{{ kpi_overall }}% Overall</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ kpi_overall }}%">
                        {{ kpi_overall }}%
                    </div>
                </div>
                <div class="kpi-grid">
                    {% for kpi in kpis %}
                    <div class="kpi-item">
                        <div class="kpi-value">{{ kpi.current }}</div>
                        <div class="kpi-label">{{ kpi.name }} ({{ kpi.target }})</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-title">📋 Current Tasks</span>
                    <span class="section-badge">Active</span>
                </div>
                <ul class="task-list">
                    {% for task in current_tasks %}
                    <li class="task-item">
                        <span class="task-name">{{ task.name }}</span>
                        <span class="task-status status-in-progress">{{ task.progress }}%</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-title">📚 Recent Activity</span>
                    <span class="section-badge">Today</span>
                </div>
                <ul class="task-list">
                    {% for activity in recent_activity %}
                    <li class="task-item">
                        <span class="task-name">{{ activity.description }}</span>
                        <span class="task-status status-{{ activity.status }}">{{ activity.time }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-title">💡 Learning & Improvement</span>
                </div>
                <ul class="task-list">
                    {% for item in improvements %}
                    <li class="task-item">
                        <span class="task-name">{{ item.suggestion }}</span>
                        <span class="task-status status-{{ item.type }}">{{ item.impact }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-header">
                    <span class="section-title">📈 Performance Trend</span>
                </div>
                <div class="chart-placeholder">
                    [Performance Chart - 7 Days]
                    <div style="display:flex; justify-content:space-around; padding:20px;">
                        {% for day in performance_trend %}
                        <div style="text-align:center;">
                            <div style="height:{{ day.value }}px; width:30px; background:var(--primary); border-radius:4px;"></div>
                            <div style="font-size:10px; margin-top:4px;">{{ day.day }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

---

## 🔧 DASHBOARD GENERATOR

```python
def generate_agent_dashboard(agent_config: dict) -> str:
    """
    Generates HTML dashboard for agent.
    """
    template = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>{agent_name} - Dashboard</title>
    <style>
        /* Agent-specific styles */
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🤖 {agent_name}</h1>
            <div class="agent-id">ID: {agent_id}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Today's Tasks</div>
                <div class="stat-value">{today_tasks}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Completed</div>
                <div class="stat-value">{completed_tasks}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Pending</div>
                <div class="stat-value">{pending_tasks}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{success_rate}%</div>
            </div>
        </div>
        
        <div class="sections">
            <div class="section full-width">
                <div class="section-header">
                    <span class="section-title">📊 KPI Progress</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {kpi_overall}%">
                        {kpi_overall}%
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return template.format(
        agent_name=agent_config['name'],
        agent_id=agent_config['agent_id'],
        today_tasks=agent_config.get('today_tasks', 0),
        completed_tasks=agent_config.get('completed_tasks', 0),
        pending_tasks=agent_config.get('pending_tasks', 0),
        success_rate=agent_config.get('success_rate', 0),
        kpi_overall=agent_config.get('kpi_overall', 0)
    )
```

---

## 📊 DASHBOARD METRICS

| Metric | Widget | Update |
|--------|--------|--------|
| Today's Tasks | Stat Card | Real-time |
| Completed | Stat Card | Real-time |
| Pending | Stat Card | Real-time |
| Success Rate | Stat Card | Hourly |
| KPI Progress | Progress Bar | Hourly |
| Current Tasks | List | Real-time |
| Recent Activity | Timeline | Real-time |
| Performance Trend | Chart | Daily |
| Improvement Suggestions | List | Daily |

---

## 📁 OUTPUT STRUCTURE

```
dashboards/
└── {agent-id}/
    └── dashboard.html
```

---

**Document Version:** 1.0.0
**Created:** 2026-07-03
**Status:** 🚀 ACTIVE
**Module:** 08 - Dashboard Factory
