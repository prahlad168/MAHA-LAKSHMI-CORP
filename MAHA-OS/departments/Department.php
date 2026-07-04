<?php
/**
 * MAHA LAKSHMI AIOS - Department Class
 * Task #0004: Department Module
 */

class Department {
    
    // Default departments
    private static $departments = [
        ['id' => 1, 'code' => 'DEPT01', 'name' => 'Corporate AI CEO Office', 'short_name' => 'CEO Office', 'parent_id' => null, 'level' => 1, 'icon' => '👑', 'color' => '#c9a86c'],
        ['id' => 2, 'code' => 'DEPT02', 'name' => 'Corporate Finance', 'short_name' => 'Finance', 'parent_id' => null, 'level' => 1, 'icon' => '💰', 'color' => '#10b981'],
        ['id' => 3, 'code' => 'DEPT03', 'name' => 'Corporate Marketing', 'short_name' => 'Marketing', 'parent_id' => null, 'level' => 1, 'icon' => '📢', 'color' => '#f59e0b'],
        ['id' => 4, 'code' => 'DEPT04', 'name' => 'Corporate HR & AI Learning', 'short_name' => 'HR', 'parent_id' => null, 'level' => 1, 'icon' => '👥', 'color' => '#ec4899'],
        ['id' => 5, 'code' => 'DEPT05', 'name' => 'Corporate IT Infrastructure', 'short_name' => 'IT', 'parent_id' => null, 'level' => 1, 'icon' => '💻', 'color' => '#3b82f6'],
        ['id' => 6, 'code' => 'DEPT06', 'name' => 'SBU Director', 'short_name' => 'Director', 'parent_id' => 1, 'level' => 2, 'icon' => '🎯', 'color' => '#8b5cf6'],
        ['id' => 7, 'code' => 'DEPT07', 'name' => 'Business AI', 'short_name' => 'Business AI', 'parent_id' => 6, 'level' => 3, 'icon' => '📊', 'color' => '#22c55e'],
        ['id' => 8, 'code' => 'DEPT08', 'name' => 'Marketing AI', 'short_name' => 'Marketing AI', 'parent_id' => 6, 'level' => 3, 'icon' => '📱', 'color' => '#f97316'],
        ['id' => 9, 'code' => 'DEPT09', 'name' => 'Sales AI', 'short_name' => 'Sales AI', 'parent_id' => 6, 'level' => 3, 'icon' => '🤝', 'color' => '#06b6d4'],
        ['id' => 10, 'code' => 'DEPT10', 'name' => 'Finance AI', 'short_name' => 'Finance AI', 'parent_id' => 6, 'level' => 3, 'icon' => '📈', 'color' => '#84cc16']
    ];
    
    public function __construct() {}
    
    /**
     * Get all departments
     */
    public function getAll(): array {
        return array_map(function($dept) {
            $dept['children'] = $this->getChildren($dept['id']);
            $dept['staff_count'] = $this->getStaffCount($dept['id']);
            return $dept;
        }, self::$departments);
    }
    
    /**
     * Get department by ID
     */
    public function getById(int $id): ?array {
        foreach (self::$departments as $dept) {
            if ($dept['id'] === $id) {
                $dept['children'] = $this->getChildren($id);
                $dept['staff_count'] = $this->getStaffCount($id);
                return $dept;
            }
        }
        return null;
    }
    
    /**
     * Get department by code
     */
    public function getByCode(string $code): ?array {
        foreach (self::$departments as $dept) {
            if ($dept['code'] === $code) {
                return $dept;
            }
        }
        return null;
    }
    
    /**
     * Get root departments (no parent)
     */
    public function getRoot(): array {
        return array_filter(self::$departments, function($dept) {
            return $dept['parent_id'] === null;
        });
    }
    
    /**
     * Get children of a department
     */
    public function getChildren(int $parentId): array {
        return array_filter(self::$departments, function($dept) use ($parentId) {
            return $dept['parent_id'] === $parentId;
        });
    }
    
    /**
     * Get department hierarchy (tree)
     */
    public function getHierarchy(): array {
        $roots = $this->getRoot();
        return array_map(function($dept) {
            return $this->buildTree($dept);
        }, $roots);
    }
    
    /**
     * Build tree recursively
     */
    private function buildTree(array $dept): array {
        $dept['children'] = array_values($this->getChildren($dept['id']));
        foreach ($dept['children'] as &$child) {
            $child = $this->buildTree($child);
        }
        return $dept;
    }
    
    /**
     * Get staff count for department
     */
    public function getStaffCount(int $deptId): int {
        // Mock count - in real app, query from database
        $counts = [1 => 1, 2 => 2, 3 => 2, 4 => 2, 5 => 2, 6 => 1, 7 => 1, 8 => 1, 9 => 1, 10 => 1];
        return $counts[$deptId] ?? 0;
    }
    
    /**
     * Create department
     */
    public function create(array $data): array {
        if (empty($data['name'])) {
            return ['success' => false, 'message' => 'Nama department wajib diisi'];
        }
        
        return [
            'success' => true,
            'message' => 'Department created',
            'id' => count(self::$departments) + 1
        ];
    }
    
    /**
     * Update department
     */
    public function update(int $id, array $data): array {
        if (!$this->getById($id)) {
            return ['success' => false, 'message' => 'Department tidak ditemukan'];
        }
        
        return ['success' => true, 'message' => 'Department updated'];
    }
    
    /**
     * Delete department
     */
    public function delete(int $id): array {
        if (!$this->getById($id)) {
            return ['success' => false, 'message' => 'Department tidak ditemukan'];
        }
        
        return ['success' => true, 'message' => 'Department deleted'];
    }
    
    /**
     * Get statistics
     */
    public function getStats(): array {
        return [
            'total_departments' => count(self::$departments),
            'root_departments' => count($this->getRoot()),
            'total_levels' => 3
        ];
    }
}
