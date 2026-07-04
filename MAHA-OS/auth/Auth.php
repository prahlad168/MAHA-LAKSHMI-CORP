<?php
/**
 * MAHA LAKSHMI AIOS - Authentication Class
 * Task #0002
 * CEO: ceo@mahalakshmi.id | WhatsApp: 081337558787
 */

class Auth {
    private $db;
    
    public function __construct($database = null) {
        if ($database) {
            $this->db = $database;
        }
    }
    
    public function login(string $email, string $password): array {
        $result = ['success' => false, 'message' => '', 'user' => null, 'token' => null];
        
        $email = filter_var(trim($email), FILTER_VALIDATE_EMAIL);
        if (!$email) {
            $result['message'] = 'Email tidak valid';
            return $result;
        }
        
        // Get user from database (simulated)
        $user = $this->getUserByEmail($email);
        
        if (!$user) {
            $result['message'] = 'Email atau password salah';
            return $result;
        }
        
        if ($user['status'] !== 'active') {
            $result['message'] = 'Akun tidak aktif';
            return $result;
        }
        
        if (!password_verify($password, $user['password_hash'])) {
            $result['message'] = 'Email atau password salah';
            return $result;
        }
        
        // Success
        $token = bin2hex(random_bytes(32));
        
        $result['success'] = true;
        $result['message'] = 'Login berhasil';
        $result['user'] = $this->sanitizeUser($user);
        $result['token'] = $token;
        
        return $result;
    }
    
    public function register(array $data): array {
        $result = ['success' => false, 'message' => '', 'user_id' => null];
        
        if (empty($data['email']) || empty($data['password']) || empty($data['name'])) {
            $result['message'] = 'Field wajib diisi';
            return $result;
        }
        
        $email = filter_var(trim($data['email']), FILTER_VALIDATE_EMAIL);
        if (!$email) {
            $result['message'] = 'Email tidak valid';
            return $result;
        }
        
        $result['success'] = true;
        $result['message'] = 'Registrasi berhasil';
        $result['user_id'] = rand(1000, 9999);
        
        return $result;
    }
    
    public function logout(string $token = null): bool {
        if (session_status() === PHP_SESSION_ACTIVE) {
            session_destroy();
        }
        return true;
    }
    
    public function check(): bool {
        return isset($_SESSION['auth_token']) || isset($_COOKIE['auth_token']);
    }
    
    public function user(): ?array {
        if (!$this->check()) return null;
        return [
            'id' => 1,
            'email' => 'ceo@mahalakshmi.id',
            'name' => 'CEO - Prahlad',
            'role' => 'ceo',
            'status' => 'active'
        ];
    }
    
    public function hasRole(string $role): bool {
        $user = $this->user();
        if (!$user) return false;
        $roles = ['ceo' => 5, 'director' => 4, 'manager' => 3, 'staff' => 2, 'ai' => 1];
        return ($roles[$user['role']] ?? 0) >= ($roles[$role] ?? 0);
    }
    
    private function getUserByEmail(string $email): ?array {
        // Demo user
        if ($email === 'ceo@mahalakshmi.id') {
            return [
                'id' => 1,
                'email' => 'ceo@mahalakshmi.id',
                'password_hash' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // password
                'name' => 'CEO - Prahlad',
                'phone' => '081337558787',
                'role' => 'ceo',
                'status' => 'active'
            ];
        }
        return null;
    }
    
    private function sanitizeUser(array $user): array {
        unset($user['password_hash'], $user['deleted_at']);
        return $user;
    }
}
