<?php
/**
 * MAHA LAKSHMI AIOS - Company Class
 * Task #0003: Company Module
 * CEO: Prahlad | ceo@mahalakshmi.id
 */

class Company {
    private $db;
    
    // Default 10 SBU companies
    private static $defaultCompanies = [
        ['code' => 'SBU01', 'name' => 'Payangan AI Solutions', 'short_name' => 'Payangan AI', 'niche' => 'Healthcare SaaS', 'icon' => '🏥', 'color' => '#22c55e', 'progress' => 25],
        ['code' => 'SBU02', 'name' => 'Gianyar Tech Solutions', 'short_name' => 'Gianyar Tech', 'niche' => 'Software Development', 'icon' => '💻', 'color' => '#3b82f6', 'progress' => 15],
        ['code' => 'SBU03', 'name' => 'Bali Digital Agency', 'short_name' => 'Bali Digital', 'niche' => 'Digital Marketing', 'icon' => '🎨', 'color' => '#f59e0b', 'progress' => 20],
        ['code' => 'SBU04', 'name' => 'Gianyar E-Commerce Hub', 'short_name' => 'Gianyar E-Com', 'niche' => 'Online Marketplace', 'icon' => '🛒', 'color' => '#8b5cf6', 'progress' => 12],
        ['code' => 'SBU05', 'name' => 'Bali EdTech Center', 'short_name' => 'Bali EdTech', 'niche' => 'Education Technology', 'icon' => '📚', 'color' => '#ec4899', 'progress' => 10],
        ['code' => 'SBU06', 'name' => 'Gianyar Finance Tech', 'short_name' => 'Gianyar Finance', 'niche' => 'Financial Services', 'icon' => '💰', 'color' => '#10b981', 'progress' => 12],
        ['code' => 'SBU07', 'name' => 'Bali Logistics Network', 'short_name' => 'Bali Logistics', 'niche' => 'Delivery & Logistics', 'icon' => '🚚', 'color' => '#f97316', 'progress' => 8],
        ['code' => 'SBU08', 'name' => 'Gianyar Food Tech', 'short_name' => 'Gianyar Food', 'niche' => 'Food Technology', 'icon' => '🍔', 'color' => '#ef4444', 'progress' => 8],
        ['code' => 'SBU09', 'name' => 'Bali Travel Platform', 'short_name' => 'Bali Travel', 'niche' => 'Tourism & Travel', 'icon' => '✈️', 'color' => '#06b6d4', 'progress' => 25],
        ['code' => 'SBU10', 'name' => 'Gianyar Property Tech', 'short_name' => 'Gianyar Property', 'niche' => 'Real Estate', 'icon' => '🏠', 'color' => '#84cc16', 'progress' => 10]
    ];
    
    public function __construct($database = null) {
        if ($database) {
            $this->db = $database;
        }
    }
    
    /**
     * Get all companies
     */
    public function getAll(): array {
        $companies = [];
        
        foreach (self::$defaultCompanies as $index => $data) {
            $companies[] = [
                'id' => $index + 1,
                'code' => $data['code'],
                'name' => $data['name'],
                'short_name' => $data['short_name'],
                'niche' => $data['niche'],
                'icon' => $data['icon'],
                'color' => $data['color'],
                'progress' => $data['progress'],
                'status' => 'active',
                'target_revenue' => 100000000,
                'current_revenue' => 0
            ];
        }
        
        return $companies;
    }
    
    /**
     * Get company by ID
     */
    public function getById(int $id): ?array {
        $companies = $this->getAll();
        
        foreach ($companies as $company) {
            if ($company['id'] === $id) {
                return $company;
            }
        }
        
        return null;
    }
    
    /**
     * Get company by code
     */
    public function getByCode(string $code): ?array {
        $companies = $this->getAll();
        
        foreach ($companies as $company) {
            if ($company['code'] === $code) {
                return $company;
            }
        }
        
        return null;
    }
    
    /**
     * Get companies by status
     */
    public function getByStatus(string $status): array {
        $companies = $this->getAll();
        
        return array_filter($companies, function($company) use ($status) {
            return $company['status'] === $status;
        });
    }
    
    /**
     * Create company
     */
    public function create(array $data): array {
        $result = [
            'success' => false,
            'message' => '',
            'id' => null
        ];
        
        // Validate required fields
        if (empty($data['name'])) {
            $result['message'] = 'Nama perusahaan wajib diisi';
            return $result;
        }
        
        $result['success'] = true;
        $result['message'] = 'Company created';
        $result['id'] = count($this->getAll()) + 1;
        
        return $result;
    }
    
    /**
     * Update company
     */
    public function update(int $id, array $data): array {
        $result = [
            'success' => false,
            'message' => ''
        ];
        
        $company = $this->getById($id);
        if (!$company) {
            $result['message'] = 'Company tidak ditemukan';
            return $result;
        }
        
        $result['success'] = true;
        $result['message'] = 'Company updated';
        
        return $result;
    }
    
    /**
     * Delete company
     */
    public function delete(int $id): array {
        $result = [
            'success' => false,
            'message' => ''
        ];
        
        $company = $this->getById($id);
        if (!$company) {
            $result['message'] = 'Company tidak ditemukan';
            return $result;
        }
        
        $result['success'] = true;
        $result['message'] = 'Company deleted';
        
        return $result;
    }
    
    /**
     * Get statistics
     */
    public function getStats(): array {
        $companies = $this->getAll();
        
        $totalRevenue = 0;
        $totalTarget = 0;
        $activeCount = 0;
        $totalProgress = 0;
        
        foreach ($companies as $company) {
            $totalRevenue += $company['current_revenue'];
            $totalTarget += $company['target_revenue'];
            if ($company['status'] === 'active') $activeCount++;
            $totalProgress += $company['progress'];
        }
        
        return [
            'total_companies' => count($companies),
            'active_companies' => $activeCount,
            'total_revenue' => $totalRevenue,
            'total_target' => $totalTarget,
            'average_progress' => round($totalProgress / count($companies), 1),
            'target_reached' => $totalRevenue >= $totalTarget
        ];
    }
    
    /**
     * Get top performing companies
     */
    public function getTopPerformers(int $limit = 3): array {
        $companies = $this->getAll();
        
        usort($companies, function($a, $b) {
            return $b['progress'] - $a['progress'];
        });
        
        return array_slice($companies, 0, $limit);
    }
    
    /**
     * Get lowest performing companies
     */
    public function getLowestPerformers(int $limit = 3): array {
        $companies = $this->getAll();
        
        usort($companies, function($a, $b) {
            return $a['progress'] - $b['progress'];
        });
        
        return array_slice($companies, 0, $limit);
    }
}
