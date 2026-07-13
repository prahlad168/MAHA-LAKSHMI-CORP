-- MAHA LAKSHMI AIOS - Company Tables
-- Task #0003: Company Module

-- Companies Table
CREATE TABLE IF NOT EXISTS `maha_companies` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(20) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `short_name` VARCHAR(50) DEFAULT NULL,
    `niche` VARCHAR(200) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `website` VARCHAR(255) DEFAULT NULL,
    `email` VARCHAR(255) DEFAULT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `address` TEXT DEFAULT NULL,
    `logo` VARCHAR(255) DEFAULT NULL,
    `icon` VARCHAR(50) DEFAULT NULL,
    `color` VARCHAR(20) DEFAULT '#1a5f5a',
    `domain` VARCHAR(255) DEFAULT NULL,
    `status` ENUM('active','inactive','pending','suspended') DEFAULT 'active',
    `progress` INT UNSIGNED DEFAULT 0,
    `target_revenue` DECIMAL(15,2) DEFAULT 100000000,
    `current_revenue` DECIMAL(15,2) DEFAULT 0,
    `founded_at` DATE DEFAULT NULL,
    `created_by` INT UNSIGNED DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    INDEX `idx_code` (`code`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Company Settings Table
CREATE TABLE IF NOT EXISTS `maha_company_settings` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `company_id` INT UNSIGNED NOT NULL,
    `setting_key` VARCHAR(100) NOT NULL,
    `setting_value` TEXT DEFAULT NULL,
    `setting_type` ENUM('string','number','boolean','json') DEFAULT 'string',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_company_setting` (`company_id`, `setting_key`),
    INDEX `idx_company_id` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Company Statistics Table
CREATE TABLE IF NOT EXISTS `maha_company_stats` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `company_id` INT UNSIGNED NOT NULL,
    `stat_date` DATE NOT NULL,
    `revenue` DECIMAL(15,2) DEFAULT 0,
    `expense` DECIMAL(15,2) DEFAULT 0,
    `profit` DECIMAL(15,2) DEFAULT 0,
    `leads` INT UNSIGNED DEFAULT 0,
    `customers` INT UNSIGNED DEFAULT 0,
    `projects` INT UNSIGNED DEFAULT 0,
    `tasks_completed` INT UNSIGNED DEFAULT 0,
    `ai_agents` INT UNSIGNED DEFAULT 0,
    `automations` INT UNSIGNED DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_company_date` (`company_id`, `stat_date`),
    INDEX `idx_company_id` (`company_id`),
    INDEX `idx_stat_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert 10 SBU Companies
INSERT INTO `maha_companies` (`code`, `name`, `short_name`, `niche`, `icon`, `color`, `status`, `progress`, `founded_at`) VALUES
('SBU01', 'Payangan AI Solutions', 'Payangan AI', 'Healthcare SaaS', '🏥', '#22c55e', 'active', 25, '2026-01-01'),
('SBU02', 'Gianyar Tech Solutions', 'Gianyar Tech', 'Software Development', '💻', '#3b82f6', 'active', 15, '2026-01-01'),
('SBU03', 'Bali Digital Agency', 'Bali Digital', 'Digital Marketing', '🎨', '#f59e0b', 'active', 20, '2026-01-01'),
('SBU04', 'Gianyar E-Commerce Hub', 'Gianyar E-Com', 'Online Marketplace', '🛒', '#8b5cf6', 'active', 12, '2026-01-01'),
('SBU05', 'Bali EdTech Center', 'Bali EdTech', 'Education Technology', '📚', '#ec4899', 'active', 10, '2026-01-01'),
('SBU06', 'Gianyar Finance Tech', 'Gianyar Finance', 'Financial Services', '💰', '#10b981', 'active', 12, '2026-01-01'),
('SBU07', 'Bali Logistics Network', 'Bali Logistics', 'Delivery & Logistics', '🚚', '#f97316', 'active', 8, '2026-01-01'),
('SBU08', 'Gianyar Food Tech', 'Gianyar Food', 'Food Technology', '🍔', '#ef4444', 'active', 8, '2026-01-01'),
('SBU09', 'Bali Travel Platform', 'Bali Travel', 'Tourism & Travel', '✈️', '#06b6d4', 'active', 25, '2026-01-01'),
('SBU10', 'Gianyar Property Tech', 'Gianyar Property', 'Real Estate', '🏠', '#84cc16', 'active', 10, '2026-01-01');
