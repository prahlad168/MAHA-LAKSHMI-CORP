<?php
/**
 * MAHA LAKSHMI AIOS - Companies API
 * Task #0003: Company Module
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/../Company.php';

$company = new Company();
$method = $_SERVER['REQUEST_METHOD'];
$path = $_SERVER['REQUEST_URI'];
$id = null;

// Parse path
preg_match('/\/api\/companies(?:\/(\d+))?/', $path, $matches);
if (isset($matches[1])) {
    $id = (int)$matches[1];
}

// Route handling
try {
    switch ($method) {
        case 'GET':
            if ($id) {
                // Get single company
                $result = $company->getById($id);
                if ($result) {
                    http_response_code(200);
                    echo json_encode(['success' => true, 'data' => $result], JSON_PRETTY_PRINT);
                } else {
                    http_response_code(404);
                    echo json_encode(['success' => false, 'message' => 'Company not found']);
                }
            } elseif (isset($_GET['status'])) {
                // Get by status
                $result = $company->getByStatus($_GET['status']);
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => array_values($result)]);
            } elseif (isset($_GET['stats'])) {
                // Get statistics
                $result = $company->getStats();
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } elseif (isset($_GET['top'])) {
                // Get top performers
                $limit = (int)($_GET['top'] ?? 3);
                $result = $company->getTopPerformers($limit);
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } elseif (isset($_GET['lowest'])) {
                // Get lowest performers
                $limit = (int)($_GET['lowest'] ?? 3);
                $result = $company->getLowestPerformers($limit);
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } else {
                // Get all companies
                $result = $company->getAll();
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result, 'total' => count($result)]);
            }
            break;
            
        case 'POST':
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $result = $company->create($input);
            http_response_code($result['success'] ? 201 : 400);
            echo json_encode($result);
            break;
            
        case 'PUT':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Company ID required']);
                break;
            }
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $result = $company->update($id, $input);
            http_response_code($result['success'] ? 200 : 400);
            echo json_encode($result);
            break;
            
        case 'DELETE':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Company ID required']);
                break;
            }
            $result = $company->delete($id);
            http_response_code($result['success'] ? 200 : 404);
            echo json_encode($result);
            break;
            
        default:
            http_response_code(405);
            echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Server error', 'error' => $e->getMessage()]);
}
