-- MAHA LAKSHMI AIOS - Leads Tables (Task #0008)

CREATE TABLE IF NOT EXISTS `maha_leads` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(30) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `email` VARCHAR(255) DEFAULT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `company` VARCHAR(200) DEFAULT NULL,
    `source` VARCHAR(50) DEFAULT NULL,
    `status` ENUM('new','contacted','qualified','proposal','negotiation','won','lost') DEFAULT 'new',
    `score` INT UNSIGNED DEFAULT 0,
    `assigned_to` INT UNSIGNED DEFAULT NULL,
    `company_id` INT UNSIGNED DEFAULT NULL,
    `notes` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`assigned_to`) REFERENCES `maha_users`(`id`),
    FOREIGN KEY (`company_id`) REFERENCES `maha_companies`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `maha_leads` (`code`,`name`,`email`,`phone`,`company`,`source`,`status`,`score`) VALUES
('LEAD001','PT Maju Bersama','contact@majubersama.co.id','0812345678','PT Maju Bersama','Website','new',75),
('LEAD002','CV Sejahtera','info@sejahtera.cv','0876543210','CV Sejahtera','Referral','qualified',85);
