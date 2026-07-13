-- =====================================================
-- MAHA OS - Database Schema v1.0
-- Task #0001: Database Foundation
-- Created: 2026-07-03
-- =====================================================

-- =====================================================
-- MASTER DATA TABLES
-- =====================================================

-- Companies (SBU/Perusahaan)
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,           -- SBU-01, SBU-02, etc
    name VARCHAR(255) NOT NULL,                 -- Payangan AI Solutions
    type VARCHAR(50) NOT NULL,                   -- AI, Software, Agency, etc
    domain VARCHAR(255),                          -- payanganhospital.gianyarkab.go.id
    target_revenue DECIMAL(15,2) DEFAULT 100000000,  -- Rp 100.000.000
    current_revenue DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',          -- active, inactive, archived
    founded_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER,                           -- For hierarchy
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (parent_id) REFERENCES departments(id)
);

-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    name VARCHAR(100) NOT NULL,                 -- CEO, Director, Manager, Staff
    level INTEGER DEFAULT 1,                      -- 1=lowest, higher=more authority
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,              -- System role (built-in)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Permissions
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,                  -- view_dashboard, manage_users
    module VARCHAR(50) NOT NULL,                  -- dashboard, users, finance, etc
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role-Permission Mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    UNIQUE(role_id, permission_id)
);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    department_id INTEGER,
    role_id INTEGER,
    employee_code VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    position VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',          -- active, inactive, on_leave
    hire_date DATE,
    termination_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- =====================================================
-- USER AUTHENTICATION
-- =====================================================

-- Users (includes AI agents)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    company_id INTEGER,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    user_type VARCHAR(20) DEFAULT 'human',       -- human, ai_agent, system
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50),
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =====================================================
-- SETTINGS & CONFIGURATION
-- =====================================================

-- Settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string',   -- string, number, boolean, json
    is_encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(company_id, setting_key)
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_departments_company ON departments(company_id);
CREATE INDEX IF NOT EXISTS idx_employees_company ON employees(company_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

-- =====================================================
-- SEED DATA - SYSTEM ROLES
-- =====================================================

INSERT INTO roles (name, level, is_system, description) VALUES
('System Administrator', 100, TRUE, 'Full system access'),
('CEO', 90, TRUE, 'Chief Executive Officer - full company access'),
('Director', 80, TRUE, 'Director - department management'),
('Manager', 60, TRUE, 'Manager - team management'),
('Staff', 30, TRUE, 'Staff - basic access'),
('AI Agent', 40, TRUE, 'AI Agent - automated tasks');

-- =====================================================
-- SEED DATA - PERMISSIONS
-- =====================================================

INSERT INTO permissions (name, module, description) VALUES
-- Dashboard
('view_dashboard', 'dashboard', 'View dashboard'),
('view_reports', 'dashboard', 'View reports'),

-- Companies
('manage_companies', 'companies', 'Manage companies'),
('view_companies', 'companies', 'View companies'),

-- Departments
('manage_departments', 'departments', 'Manage departments'),
('view_departments', 'departments', 'View departments'),

-- Employees
('manage_employees', 'employees', 'Manage employees'),
('view_employees', 'employees', 'View employees'),

-- Users
('manage_users', 'users', 'Manage users'),
('view_users', 'users', 'View users'),

-- Finance
('manage_finance', 'finance', 'Manage finance'),
('view_finance', 'finance', 'View finance'),
('approve_expenses', 'finance', 'Approve expenses'),

-- CRM
('manage_crm', 'crm', 'Manage CRM'),
('view_crm', 'crm', 'View CRM'),

-- Projects
('manage_projects', 'projects', 'Manage projects'),
('view_projects', 'projects', 'View projects'),

-- Knowledge
('manage_knowledge', 'knowledge', 'Manage knowledge base'),
('view_knowledge', 'knowledge', 'View knowledge base'),

-- AI Agents
('manage_agents', 'agents', 'Manage AI agents'),
('view_agents', 'agents', 'View AI agents'),

-- Settings
('manage_settings', 'settings', 'Manage settings'),

-- Audit
('view_audit_logs', 'audit', 'View audit logs');

-- =====================================================
-- SEED DATA - SYSTEM PERMISSIONS FOR ADMIN
-- =====================================================

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'System Administrator';

-- CEO gets all except system admin
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'CEO' AND p.name NOT LIKE 'manage_%';

-- =====================================================
-- SEED DATA - HOLDINGS COMPANY
-- =====================================================

INSERT INTO companies (code, name, type, domain, status) VALUES
('SBU-HQ', 'MAHA LAKSHMI DIGITAL HOLDINGS', 'Holdings', 'mahalakshmi.id', 'active');

-- =====================================================
-- SEED DATA - SETTINGS
-- =====================================================

INSERT INTO settings (company_id, setting_key, setting_value, setting_type, description) VALUES
(NULL, 'app_name', 'MAHA OS', 'string', 'Application name'),
(NULL, 'app_version', '1.0.0', 'string', 'Application version'),
(NULL, 'timezone', 'Asia/Makassar', 'string', 'Timezone (WITA)'),
(NULL, 'currency', 'IDR', 'string', 'Currency code'),
(NULL, 'date_format', 'd/m/Y', 'string', 'Date format'),
(NULL, 'maintenance_mode', 'false', 'boolean', 'Maintenance mode'),
(NULL, 'ai_strategy', 'human_decisions', 'string', 'AI should assist, not decide critical things'),
(NULL, 'profit_distribution_owner', '60', 'number', 'Owner share percentage'),
(NULL, 'profit_distribution_reinvest', '25', 'number', 'Reinvestment percentage'),
(NULL, 'profit_distribution_team', '10', 'number', 'Team bonus percentage'),
(NULL, 'profit_distribution_charity', '5', 'number', 'Charity percentage');

-- =====================================================
-- SEED DATA - AI AGENT TEMPLATE
-- =====================================================

-- Insert CEO employee and user
INSERT INTO employees (company_id, name, email, position, status) VALUES
(1, 'Prahlad', 'ceo@mahalakshmi.id', 'CEO', 'active');

INSERT INTO users (employee_id, company_id, username, email, user_type, is_active) VALUES
(1, 1, 'ceo', 'ceo@mahalakshmi.id', 'human', TRUE);

-- =====================================================
-- METADATA
-- =====================================================

INSERT INTO settings (company_id, setting_key, setting_value, setting_type, description) VALUES
(NULL, 'db_version', '1.0.0', 'string', 'Database schema version'),
(NULL, 'db_created_at', datetime('now'), 'string', 'Database creation timestamp'),
(NULL, 'db_migration', '001_initial', 'string', 'Latest migration'),
(NULL, 'owner_bank', 'BCA', 'string', 'Owner bank'),
(NULL, 'owner_account', '6485086645', 'string', 'Owner bank account');

-- =====================================================
-- COMPLETED
-- =====================================================
-- Task #0001: Database Foundation - COMPLETE
-- Tables created: 12
-- Indexes created: 8
-- Seed data inserted: System roles, permissions, CEO
-- Ready for: Authentication, Company Module, etc
-- =====================================================