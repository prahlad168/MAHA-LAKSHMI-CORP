-- MAHA LAKSHMI AIOS - Finance Tables (Task #0007)

CREATE TABLE IF NOT EXISTS `maha_transactions` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `type` ENUM('income','expense') DEFAULT 'income',
    `category` VARCHAR(50) DEFAULT NULL,
    `amount` DECIMAL(15,2) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `user_id` INT UNSIGNED DEFAULT NULL,
    `date` DATE NOT NULL,
    `status` ENUM('pending','approved','rejected') DEFAULT 'approved',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`),
    FOREIGN KEY (`user_id`) REFERENCES `maha_users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `maha_invoices` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `invoice_number` VARCHAR(50) NOT NULL UNIQUE,
    `client_name` VARCHAR(200) DEFAULT NULL,
    `client_email` VARCHAR(255) DEFAULT NULL,
    `amount` DECIMAL(15,2) NOT NULL,
    `tax` DECIMAL(15,2) DEFAULT 0,
    `total` DECIMAL(15,2) NOT NULL,
    `status` ENUM('draft','sent','paid','overdue','cancelled') DEFAULT 'draft',
    `due_date` DATE DEFAULT NULL,
    `paid_date` DATE DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
