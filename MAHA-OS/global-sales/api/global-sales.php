<?php
/** MAHA LAKSHMI - Global Digital Sales API */
header('Content-Type: application/json');
require_once __DIR__ . '/../GlobalDigitalSales.php';

$sales = new GlobalDigitalSales();
$method = $_SERVER['REQUEST_METHOD'];

switch($method) {
    case 'GET':
        if (isset($_GET['type'])) {
            switch($_GET['type']) {
                case 'countries':
                    echo json_encode(['success'=>true,'data'=>$sales->getCountries()]);
                    break;
                case 'products':
                    echo json_encode(['success'=>true,'data'=>$sales->getProducts()]);
                    break;
                case 'agents':
                    echo json_encode(['success'=>true,'data'=>$sales->getAgents()]);
                    break;
                case 'report':
                    $report = $sales->getTodayReport();
                    if ($report) {
                        echo json_encode(['success'=>true,'data'=>$report]);
                    } else {
                        $newReport = $sales->generateGlobalSales();
                        echo json_encode(['success'=>true,'data'=>$newReport,'generated'=>true]);
                    }
                    break;
                default:
                    echo json_encode(['success'=>false,'message'=>'Unknown type']);
            }
        } else {
            $report = $sales->generateGlobalSales();
            echo json_encode(['success'=>true,'data'=>$report]);
        }
        break;
    case 'POST':
        $input = json_decode(file_get_contents('php://input'), true);
        if (isset($input['action']) && $input['action'] === 'generate') {
            $report = $sales->generateGlobalSales();
            echo json_encode(['success'=>true,'data'=>$report]);
        } else {
            echo json_encode(['success'=>false,'message'=>'Invalid action']);
        }
        break;
    default:
        http_response_code(405);
        echo json_encode(['success'=>false,'message'=>'Method not allowed']);
}
