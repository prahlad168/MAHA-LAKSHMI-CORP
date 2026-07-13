# Agent Architecture - Payangan Hospital

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER                                           │
│                     (You - End User / Developer)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        API LAYER (NestJS)                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   REST     │  │   GraphQL   │  │  WebSocket  │  │   Webhook   │        │
│  │  Endpoints │  │   Schema   │  │   Real-time │  │   Handler   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAIN AGENT                                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     AGENT ORCHESTRATOR                                 │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │   │   Planner   │──│  Research   │──│  Coding     │                 │  │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  │        │                │                │                            │  │
│  │        ▼                ▼                ▼                            │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │   │     QA      │  │   Memory    │  │Skill Builder│                 │  │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  │        │                │                │                            │  │
│  │        ▼                ▼                ▼                            │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │   │Reflection   │  │Workflow Opt │  │Auto Manager │                 │  │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                          │
│                                                                             │
│  ┌─────────────────────────────┐    ┌────────────────────────────────────┐ │
│  │         FIRESTORE           │    │       VECTOR DATABASE             │ │
│  │                             │    │          (Qdrant)                 │ │
│  │  ┌───────────────────────┐  │    │                                    │ │
│  │  │ 📁 Skills             │  │    │  ┌────────────────────────────┐     │ │
│  │  │ 📁 Knowledge         │  │    │  │ 🔍 Semantic Search         │     │ │
│  │  │ 📁 Experiences       │  │    │  │ 🔄 RAG Pipeline            │     │ │
│  │  │ 📁 Workflows         │  │    │  │ 📊 Embeddings Storage      │     │ │
│  │  │ 📁 Templates         │  │    │  └────────────────────────────┘     │ │
│  │  │ 📁 Projects          │  │    │                                    │ │
│  │  │ 📁 Logs              │  │    └────────────────────────────────────┘ │
│  │  └───────────────────────┘  │                                           │
│  └─────────────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Firestore Collections

### 1. **skills**
```typescript
interface Skill {
  id: string;
  name: string;
  description: string;
  category: 'development' | 'devops' | 'data' | 'communication';
  commands: string[];
  files: string[];
  dependencies: string[];
  createdAt: Timestamp;
  updatedAt: Timestamp;
  usageCount: number;
  lastUsed: Timestamp;
}
```

### 2. **knowledge**
```typescript
interface Knowledge {
  id: string;
  title: string;
  content: string;
  embedding: number[]; // Vector
  tags: string[];
  source: 'manual' | 'auto-generated' | 'learned';
  projectId: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

### 3. **experiences**
```typescript
interface Experience {
  id: string;
  taskType: string;
  solution: string;
  result: 'success' | 'partial' | 'failed';
  rating: number; // 1-5
  context: {
    project: string;
    tools: string[];
    duration: number;
  };
  learnings: string[];
  createdAt: Timestamp;
}
```

### 4. **workflows**
```typescript
interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  triggers: ('manual' | 'scheduled' | 'event')[];
  schedule?: string; // Cron expression
  enabled: boolean;
  lastRun?: Timestamp;
  runCount: number;
  createdAt: Timestamp;
}

interface WorkflowStep {
  agent: string; // Agent name
  action: string;
  input: Record<string, any>;
  output: string;
  onSuccess?: string; // Next step
  onFailure?: string; // Fallback step
}
```

### 5. **templates**
```typescript
interface Template {
  id: string;
  name: string;
  category: 'code' | 'document' | 'workflow' | 'prompt';
  content: string;
  variables: TemplateVariable[];
  usageCount: number;
  createdAt: Timestamp;
}

interface TemplateVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object';
  required: boolean;
  default?: any;
}
```

### 6. **projects**
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  repository?: {
    provider: 'github' | 'gitlab' | 'bitbucket';
    url: string;
    branch: string;
  };
  hosting?: {
    provider: string;
    url: string;
    webhookSecret?: string;
  };
  agents: string[]; // Agent IDs assigned to project
  settings: Record<string, any>;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

### 7. **logs**
```typescript
interface Log {
  id: string;
  agentId: string;
  projectId: string;
  action: string;
  status: 'started' | 'completed' | 'failed';
  input: Record<string, any>;
  output?: Record<string, any>;
  error?: string;
  duration: number; // milliseconds
  createdAt: Timestamp;
}
```

---

## 🤖 Agent Modules

### 1. **Planner**
```typescript
// Responsibilities:
// - Break down user requests into actionable tasks
// - Create execution plan with dependencies
// - Prioritize tasks based on urgency/importance
// - Estimate time/resources needed

interface PlannerConfig {
  maxDepth: number; // Max sub-task depth
  timeout: number;
  allowParallel: boolean;
}
```

### 2. **Research**
```typescript
// Responsibilities:
// - Gather information needed for tasks
// - Search documentation and knowledge base
// - Analyze codebases and repositories
// - Find best practices and patterns

interface ResearchConfig {
  searchEngines: string[];
  maxResults: number;
  includeExternal: boolean;
}
```

### 3. **Coding**
```typescript
// Responsibilities:
// - Write and modify code
// - Create files and directories
// - Execute commands
// - Manage git operations

interface CodingConfig {
  allowedExtensions: string[];
  autoFormat: boolean;
  lintOnSave: boolean;
  testOnCommit: boolean;
}
```

### 4. **QA (Quality Assurance)**
```typescript
// Responsibilities:
// - Run tests and linters
// - Check code quality
// - Verify functionality
// - Generate test coverage reports

interface QAConfig {
  testCommand: string;
  lintCommand: string;
  coverageThreshold: number;
  autoFix: boolean;
}
```

### 5. **Memory**
```typescript
// Responsibilities:
// - Store conversation context
// - Manage short-term and long-term memory
// - Track task progress
// - Handle session persistence

interface MemoryConfig {
  shortTermLimit: number; // Max items
  longTermRetention: number; // Days
  compressionEnabled: boolean;
}
```

### 6. **Skill Builder**
```typescript
// Responsibilities:
// - Create new skills from interactions
// - Update existing skills
// - Manage skill dependencies
// - Optimize skill performance

interface SkillBuilderConfig {
  autoLearn: boolean;
  minConfidence: number; // 0-1
  reviewBeforeSave: boolean;
}
```

### 7. **Reflection**
```typescript
// Responsibilities:
// - Analyze past performance
// - Identify patterns and improvements
// - Generate insights
// - Self-correct mistakes

interface ReflectionConfig {
  afterEveryNTasks: number;
  generateInsights: boolean;
  updateKnowledge: boolean;
}
```

### 8. **Workflow Optimizer**
```typescript
// Responsibilities:
// - Optimize workflow execution
// - Reduce redundancy
// - Improve efficiency
// - Suggest improvements

interface WorkflowOptimizerConfig {
  analyzeFrequency: 'realtime' | 'hourly' | 'daily';
  autoOptimize: boolean;
  trackMetrics: string[];
}
```

### 9. **Automation Manager**
```typescript
// Responsibilities:
// - Manage scheduled automations
// - Handle webhook triggers
// - Monitor automation health
// - Handle failures and retries

interface AutomationManagerConfig {
  maxRetries: number;
  retryDelay: number;
  alertOnFailure: boolean;
  cleanupOldRuns: boolean;
}
```

---

## 🔄 RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RAG PIPELINE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌─────────────────────────────────────┐
│  1. Query Embedding                 │
│     (Convert to vector)             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  2. Vector Search (Qdrant)          │
│     - Semantic similarity search     │
│     - Top-K results                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  3. Context Assembly                │
│     - Combine retrieved docs        │
│     - Deduplicate                   │
│     - Rank by relevance             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  4. Prompt Engineering              │
│     - Insert context into prompt    │
│     - Add system instructions       │
│     - Format for LLM                │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  5. LLM Inference                   │
│     - Generate response             │
│     - Cite sources                  │
└─────────────────────────────────────┘
    │
    ▼
Response + Citations
```

---

## 📊 Implementation Roadmap

### Phase 1: Foundation (Current)
- [x] Basic automation setup
- [x] Webhook integration
- [x] GitHub API integration
- [x] Simple daily report generation

### Phase 2: API Layer
- [ ] NestJS API setup
- [ ] REST endpoints
- [ ] WebSocket support
- [ ] Authentication

### Phase 3: Agent Enhancement
- [ ] Implement Planner module
- [ ] Implement Memory module
- [ ] Implement QA module
- [ ] Implement Reflection module

### Phase 4: Data Layer
- [ ] Firestore setup
- [ ] Qdrant setup
- [ ] RAG pipeline implementation
- [ ] Knowledge base population

### Phase 5: Advanced Features
- [ ] Workflow Optimizer
- [ ] Skill Builder automation
- [ ] Multi-agent collaboration
- [ ] Advanced analytics

---

## 🔧 Configuration

### NestJS API Config
```yaml
# config.yaml
api:
  host: "0.0.0.0"
  port: 3000
  cors:
    enabled: true
    origins: ["*"]

database:
  firestore:
    projectId: "payangan-hospital"
    database: "(default)"

vector:
  qdrant:
    url: "http://localhost:6333"
    collection: "payangan-knowledge"

agent:
  orchestrator:
    maxConcurrentTasks: 5
    defaultTimeout: 600000
```

### Environment Variables
```bash
# .env
OPENAI_API_KEY=sk-xxx
GITHUB_TOKEN=ghp_xxx
QWDRANT_URL=http://localhost:6333
QWDRANT_API_KEY=xxx
GOOGLE_APPLICATION_CREDENTIALS=./config/service-account.json
```

---

## 📈 Monitoring & Observability

### Metrics to Track
- Task completion rate
- Average response time
- Error rate by module
- Skill usage frequency
- User satisfaction score
- API latency
- Token usage

### Logging Strategy
```typescript
interface LogEntry {
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error';
  module: string;
  action: string;
  userId?: string;
  projectId?: string;
  metadata: Record<string, any>;
  duration?: number;
}
```

---

**Created:** 2026-07-02
**Last Updated:** 2026-07-02
**Version:** 1.0.0
