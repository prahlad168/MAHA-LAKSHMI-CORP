-- MAHA LAKSHMI AIOS - Roles & Permissions Tables
-- Task #0005

CREATE TABLE IF NOT EXISTS `maha_roles` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `level` TINYINT UNSIGNED DEFAULT 1,
    `is_system` TINYINT(1) DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `maha_permissions` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `module` VARCHAR(50) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `maha_role_permissions` (
    `role_id` INT UNSIGNED NOT NULL,
    `permission_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `maha_roles` (`code`, `name`, `level`, `is_system`) VALUES
('CEO', 'Chief Executive Officer', 10, 1),
('CTO', 'Chief Technology Officer', 9, 1),
('CFO', 'Chief Financial Officer', 9, 1),
('COO', 'Chief Operating Officer', 9, 1),
('DIRECTOR', 'Director', 8, 1),
('MANAGER', 'Manager', 7, 1),
('STAFF', 'Staff', 5, 1),
('AI', 'AI Agent', 1, 1);

INSERT INTO `maha_permissions` (`code`, `name`, `module`) VALUES
('company.view', 'View Companies', 'company'),
('company.create', 'Create Company', 'company'),
('company.edit', 'Edit Company', 'company'),
('company.delete', 'Delete Company', 'company'),
('dept.view', 'View Departments', 'department'),
('dept.manage', 'Manage Departments', 'department'),
('user.view', 'View Users', 'user'),
('user.manage', 'Manage Users', 'user'),
('finance.view', 'View Finance', 'finance'),
('finance.manage', 'Manage Finance', 'finance'),
('report.view', 'View Reports', 'report'),
('report.export', 'Export Reports', 'report'),
('ai.manage', 'Manage AI Agents', 'ai'),
('settings.manage', 'Manage Settings', 'settings');
