-- MAHA LAKSHMI AIOS - AI Agents Tables (Task #0010)

CREATE TABLE IF NOT EXISTS `maha_ai_agents` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `type` VARCHAR(50) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `department_id` INT UNSIGNED DEFAULT NULL,
    `status` ENUM('active','inactive','training') DEFAULT 'active',
    `capabilities` JSON DEFAULT NULL,
    `config` JSON DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `maha_ai_agents` (`code`,`name`,`type`,`company_id`,`status`) VALUES
('AGENT001','Sales AI Agent','sales',1,'active'),
('AGENT002','Marketing AI Agent','marketing',1,'active'),
('AGENT003','Finance AI Agent','finance',1,'active'),
('AGENT004','HR AI Agent','hr',1,'active'),
('AGENT005','Support AI Agent','support',1,'active'),
('AGENT006','Daily Report Agent','automation',1,'active');
