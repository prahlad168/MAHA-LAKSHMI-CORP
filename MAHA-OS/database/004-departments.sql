-- MAHA LAKSHMI AIOS - Department Tables
-- Task #0004: Department Module

-- Departments Table
CREATE TABLE IF NOT EXISTS `maha_departments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(20) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `short_name` VARCHAR(50) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `parent_id` INT UNSIGNED DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `level` TINYINT UNSIGNED DEFAULT 1,
    `icon` VARCHAR(50) DEFAULT '📁',
    `color` VARCHAR(20) DEFAULT '#1a5f5a',
    `status` ENUM('active','inactive') DEFAULT 'active',
    `head_user_id` INT UNSIGNED DEFAULT NULL,
    `budget` DECIMAL(15,2) DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    FOREIGN KEY (`parent_id`) REFERENCES `maha_departments`(`id`) ON DELETE SET NULL,
    INDEX `idx_code` (`code`),
    INDEX `idx_parent` (`parent_id`),
    INDEX `idx_company` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Department Staff Table
CREATE TABLE IF NOT EXISTS `maha_department_staff` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `department_id` INT UNSIGNED NOT NULL,
    `user_id` INT UNSIGNED NOT NULL,
    `role` ENUM('head','member','assistant') DEFAULT 'member',
    `is_active` TINYINT(1) DEFAULT 1,
    `joined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `left_at` DATETIME DEFAULT NULL,
    FOREIGN KEY (`department_id`) REFERENCES `maha_departments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `maha_users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_dept_user` (`department_id`, `user_id`),
    INDEX `idx_department` (`department_id`),
    INDEX `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Default Departments
INSERT INTO `maha_departments` (`code`, `name`, `short_name`, `description`, `parent_id`, `level`, `icon`, `color`) VALUES
-- Corporate Level (Level 1)
('DEPT01', 'Corporate AI CEO Office', 'CEO Office', 'Executive leadership and AI governance', NULL, 1, '👑', '#c9a86c'),
('DEPT02', 'Corporate Finance', 'Finance', 'Financial management and accounting', NULL, 1, '💰', '#10b981'),
('DEPT03', 'Corporate Marketing', 'Marketing', 'Brand and marketing activities', NULL, 1, '📢', '#f59e0b'),
('DEPT04', 'Corporate HR & AI Learning', 'HR', 'Human resources and AI training', NULL, 1, '👥', '#ec4899'),
('DEPT05', 'Corporate IT Infrastructure', 'IT', 'Technology and infrastructure', NULL, 1, '💻', '#3b82f6'),
-- SBU Level (Level 2)
('DEPT06', 'SBU Director', 'Director', 'SBU leadership', 1, 2, '🎯', '#8b5cf6'),
-- Functional Level (Level 3)
('DEPT07', 'Business AI', 'Business AI', 'Business analysis and strategy', 6, 3, '📊', '#22c55e'),
('DEPT08', 'Marketing AI', 'Marketing AI', 'Content, SEO, social media', 6, 3, '📱', '#f97316'),
('DEPT09', 'Sales AI', 'Sales AI', 'Lead generation and conversion', 6, 3, '🤝', '#06b6d4'),
('DEPT10', 'Finance AI', 'Finance AI', 'Invoice and financial tracking', 6, 3, '📈', '#84cc16');
