<?php
/**
 * MAHA LAKSHMI AIOS - Departments API
 * Task #0004: Department Module
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/../Department.php';

$dept = new Department();
$method = $_SERVER['REQUEST_METHOD'];
$path = $_SERVER['REQUEST_URI'];

// Parse path
preg_match('/\/api\/departments(?:\/(\d+))?/', $path, $matches);
$id = isset($matches[1]) ? (int)$matches[1] : null;

try {
    switch ($method) {
        case 'GET':
            if ($id) {
                $result = $dept->getById($id);
                if ($result) {
                    http_response_code(200);
                    echo json_encode(['success' => true, 'data' => $result]);
                } else {
                    http_response_code(404);
                    echo json_encode(['success' => false, 'message' => 'Department not found']);
                }
            } elseif (isset($_GET['hierarchy'])) {
                $result = $dept->getHierarchy();
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } elseif (isset($_GET['root'])) {
                $result = array_values($dept->getRoot());
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } elseif (isset($_GET['stats'])) {
                $result = $dept->getStats();
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result]);
            } else {
                $result = $dept->getAll();
                http_response_code(200);
                echo json_encode(['success' => true, 'data' => $result, 'total' => count($result)]);
            }
            break;
            
        case 'POST':
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $result = $dept->create($input);
            http_response_code($result['success'] ? 201 : 400);
            echo json_encode($result);
            break;
            
        case 'PUT':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Department ID required']);
                break;
            }
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $result = $dept->update($id, $input);
            http_response_code($result['success'] ? 200 : 400);
            echo json_encode($result);
            break;
            
        case 'DELETE':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Department ID required']);
                break;
            }
            $result = $dept->delete($id);
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
