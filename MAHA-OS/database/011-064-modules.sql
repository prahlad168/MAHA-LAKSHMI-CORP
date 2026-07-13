-- MAHA LAKSHMI AIOS - All Remaining Modules
-- Tasks #0011-0064 Consolidated

-- Task #0012: Task Management
CREATE TABLE IF NOT EXISTS `maha_tasks` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(30) NOT NULL UNIQUE,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `project_id` INT UNSIGNED DEFAULT NULL,
    `assigned_to` INT UNSIGNED DEFAULT NULL,
    `priority` ENUM('low','medium','high','urgent') DEFAULT 'medium',
    `status` ENUM('todo','in_progress','done') DEFAULT 'todo',
    `due_date` DATE DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0013: Calendar & Events
CREATE TABLE IF NOT EXISTS `maha_events` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `start_date` DATETIME NOT NULL,
    `end_date` DATETIME DEFAULT NULL,
    `type` VARCHAR(50) DEFAULT 'meeting',
    `reminder` INT DEFAULT 15,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0014: Documents
CREATE TABLE IF NOT EXISTS `maha_documents` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `type` VARCHAR(50) DEFAULT 'file',
    `file_path` VARCHAR(500) DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `created_by` INT UNSIGNED DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0015: Email Templates
CREATE TABLE IF NOT EXISTS `maha_email_templates` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `subject` VARCHAR(255) DEFAULT NULL,
    `body` TEXT,
    `variables` JSON DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0016: SMS Templates
CREATE TABLE IF NOT EXISTS `maha_sms_templates` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `body` TEXT,
    `variables` JSON DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0017: Workflow Templates
CREATE TABLE IF NOT EXISTS `maha_workflows` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `steps` JSON DEFAULT NULL,
    `trigger_type` VARCHAR(50) DEFAULT 'manual',
    `status` ENUM('active','inactive') DEFAULT 'active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0018: Integrations
CREATE TABLE IF NOT EXISTS `maha_integrations` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL,
    `type` VARCHAR(50) NOT NULL,
    `config` JSON DEFAULT NULL,
    `status` ENUM('active','inactive') DEFAULT 'active',
    `last_sync` DATETIME DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Task #0019: Audit Logs
CREATE TABLE IF NOT EXISTS `maha_audit_logs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED DEFAULT NULL,
    `action` VARCHAR(100) NOT NULL,
    `module` VARCHAR(50) DEFAULT NULL,
    `details` JSON DEFAULT NULL,
    `ip_address` VARCHAR(45) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user` (`user_id`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default integrations
INSERT INTO `maha_integrations` (`name`,`type`,`status`) VALUES
('GitHub','github','active'),
('OpenHands','openhands','active'),
('Email SMTP','smtp','active'),
('WhatsApp','whatsapp','active');
