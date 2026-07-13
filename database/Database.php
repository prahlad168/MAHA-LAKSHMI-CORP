<?php
/**
 * MAHA OS - Database Connection & Helper
 * Task #0001: Database Foundation
 */

class Database {
    private static $instance = null;
    private $pdo;
    private $dbPath;
    
    private function __construct() {
        $this->dbPath = __DIR__ . '/maha.db';
        $this->connect();
    }
    
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function connect() {
        try {
            $this->pdo = new PDO('sqlite:' . $this->dbPath);
            $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            die('Database connection failed: ' . $e->getMessage());
        }
    }
    
    /**
     * Run migrations
     */
    public function migrate($migrationFile = null) {
        if ($migrationFile) {
            $this->runMigrationFile($migrationFile);
        } else {
            // Run all migrations
            $migrations = glob(__DIR__ . '/migrations/*.sql');
            sort($migrations);
            foreach ($migrations as $migration) {
                $this->runMigrationFile($migration);
            }
        }
        return true;
    }
    
    private function runMigrationFile($file) {
        $sql = file_get_contents($file);
        $statements = array_filter(array_map('trim', explode(';', $sql)));
        
        foreach ($statements as $statement) {
            if (!empty($statement) && strpos($statement, '--') !== 0) {
                $this->pdo->exec($statement);
            }
        }
        
        // Log migration
        $filename = basename($file);
        $this->insert('settings', [
            'setting_key' => 'last_migration',
            'setting_value' => $filename
        ]);
        
        return true;
    }
    
    /**
     * Backup database
     */
    public function backup($backupPath = null) {
        if ($backupPath === null) {
            $backupPath = __DIR__ . '/backups/maha_' . date('Y-m-d_His') . '.db';
        }
        
        // Create backup directory if not exists
        $dir = dirname($backupPath);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        return copy($this->dbPath, $backupPath);
    }
    
    /**
     * Query builder - SELECT
     */
    public function select($table, $conditions = [], $fields = '*') {
        $sql = "SELECT $fields FROM $table";
        $params = [];
        
        if (!empty($conditions)) {
            $where = [];
            foreach ($conditions as $key => $value) {
                if (is_null($value)) {
                    $where[] = "$key IS NULL";
                } else {
                    $where[] = "$key = ?";
                    $params[] = $value;
                }
            }
            $sql .= ' WHERE ' . implode(' AND ', $where);
        }
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        return $stmt->fetchAll();
    }
    
    /**
     * Find one record
     */
    public function find($table, $conditions = [], $fields = '*') {
        $results = $this->select($table, $conditions, $fields);
        return $results ? $results[0] : null;
    }
    
    /**
     * Insert record
     */
    public function insert($table, $data) {
        $fields = implode(', ', array_keys($data));
        $placeholders = implode(', ', array_fill(0, count($data), '?'));
        
        $sql = "INSERT INTO $table ($fields) VALUES ($placeholders)";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute(array_values($data));
        
        return $this->pdo->lastInsertId();
    }
    
    /**
     * Update records
     */
    public function update($table, $data, $conditions = []) {
        $set = [];
        foreach (array_keys($data) as $key) {
            $set[] = "$key = ?";
        }
        
        $sql = "UPDATE $table SET " . implode(', ', $set);
        $params = array_values($data);
        
        if (!empty($conditions)) {
            $where = [];
            foreach ($conditions as $key => $value) {
                $where[] = "$key = ?";
                $params[] = $value;
            }
            $sql .= ' WHERE ' . implode(' AND ', $where);
        }
        
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute($params);
    }
    
    /**
     * Delete records
     */
    public function delete($table, $conditions = []) {
        $sql = "DELETE FROM $table";
        $params = [];
        
        if (!empty($conditions)) {
            $where = [];
            foreach ($conditions as $key => $value) {
                $where[] = "$key = ?";
                $params[] = $value;
            }
            $sql .= ' WHERE ' . implode(' AND ', $where);
        }
        
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute($params);
    }
    
    /**
     * Execute raw SQL
     */
    public function query($sql, $params = []) {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        return $stmt->fetchAll();
    }
    
    /**
     * Get settings value
     */
    public function getSetting($key, $companyId = null) {
        $conditions = ['setting_key' => $key];
        if ($companyId !== null) {
            $conditions['company_id'] = $companyId;
        }
        
        $setting = $this->find('settings', $conditions);
        return $setting ? $setting['setting_value'] : null;
    }
    
    /**
     * Set settings value
     */
    public function setSetting($key, $value, $companyId = null) {
        $data = [
            'setting_key' => $key,
            'setting_value' => $value,
            'setting_type' => is_numeric($value) ? 'number' : 'string',
            'updated_at' => date('Y-m-d H:i:s')
        ];
        
        if ($companyId !== null) {
            $data['company_id'] = $companyId;
        }
        
        // Check if exists
        $existing = $this->find('settings', ['setting_key' => $key, 'company_id' => $companyId]);
        
        if ($existing) {
            return $this->update('settings', $data, ['id' => $existing['id']]);
        } else {
            return $this->insert('settings', $data);
        }
    }
    
    /**
     * Log audit trail
     */
    public function audit($userId, $action, $module = null, $recordId = null, $oldValue = null, $newValue = null) {
        return $this->insert('audit_logs', [
            'user_id' => $userId,
            'action' => $action,
            'module' => $module,
            'record_id' => $recordId,
            'old_value' => $oldValue ? json_encode($oldValue) : null,
            'new_value' => $newValue ? json_encode($newValue) : null,
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? null,
            'created_at' => date('Y-m-d H:i:s')
        ]);
    }
    
    /**
     * Get audit logs
     */
    public function getAuditLogs($filters = [], $limit = 100) {
        $sql = "SELECT * FROM audit_logs al 
                LEFT JOIN users u ON al.user_id = u.id 
                LEFT JOIN employees e ON u.employee_id = e.id
                WHERE 1=1";
        $params = [];
        
        if (!empty($filters['user_id'])) {
            $sql .= " AND al.user_id = ?";
            $params[] = $filters['user_id'];
        }
        
        if (!empty($filters['action'])) {
            $sql .= " AND al.action LIKE ?";
            $params[] = '%' . $filters['action'] . '%';
        }
        
        if (!empty($filters['module'])) {
            $sql .= " AND al.module = ?";
            $params[] = $filters['module'];
        }
        
        if (!empty($filters['date_from'])) {
            $sql .= " AND al.created_at >= ?";
            $params[] = $filters['date_from'];
        }
        
        if (!empty($filters['date_to'])) {
            $sql .= " AND al.created_at <= ?";
            $params[] = $filters['date_to'];
        }
        
        $sql .= " ORDER BY al.created_at DESC LIMIT ?";
        $params[] = $limit;
        
        return $this->query($sql, $params);
    }
}

// Helper function for quick access
function db() {
    return Database::getInstance();
}