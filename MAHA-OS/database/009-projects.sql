-- MAHA LAKSHMI AIOS - Projects Tables (Task #0009)

CREATE TABLE IF NOT EXISTS `maha_projects` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `client_id` INT UNSIGNED DEFAULT NULL,
    `status` ENUM('planning','in_progress','review','completed','cancelled') DEFAULT 'planning',
    `priority` ENUM('low','medium','high','urgent') DEFAULT 'medium',
    `start_date` DATE DEFAULT NULL,
    `end_date` DATE DEFAULT NULL,
    `budget` DECIMAL(15,2) DEFAULT 0,
    `progress` INT UNSIGNED DEFAULT 0,
    `manager_id` INT UNSIGNED DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `maha_projects` (`code`,`name`,`status`,`priority`,`progress`) VALUES
('PRJ001','Website Redesign','in_progress','high',60),
('PRJ002','Mobile App Development','planning','medium',15);
