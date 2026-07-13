-- MAHA LAKSHMI AIOS - Employee Tables (Task #0006)

CREATE TABLE IF NOT EXISTS `maha_employees` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED NOT NULL,
    `employee_code` VARCHAR(20) UNIQUE,
    `department_id` INT UNSIGNED DEFAULT NULL,
    `position` VARCHAR(100) DEFAULT NULL,
    `hire_date` DATE DEFAULT NULL,
    `salary` DECIMAL(15,2) DEFAULT 0,
    `status` ENUM('active','inactive','resigned') DEFAULT 'active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `maha_users`(`id`),
    FOREIGN KEY (`department_id`) REFERENCES `maha_departments`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `maha_employees` (`user_id`, `employee_code`, `department_id`, `position`, `hire_date`, `salary`, `status`)
VALUES (1, 'EMP001', 1, 'CEO', '2026-01-01', 50000000, 'active');
