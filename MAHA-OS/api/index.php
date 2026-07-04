<?php
/** MAHA LAKSHMI AIOS - Main API Router */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if (strpos($path, '/api/companies') === 0) {
    require_once __DIR__.'/../companies/Company.php';
    $c = new Company(); $id = preg_match('/\/api\/companies\/(\d+)/',$path,$m) ? (int)$m[1] : null;
    $response = $method==='GET' ? ['success'=>true,'data'=>$id?$c->getById($id):$c->getAll()] : ['success'=>false];
} elseif (strpos($path, '/api/departments') === 0) {
    require_once __DIR__.'/../departments/Department.php';
    $d = new Department(); $id = preg_match('/\/api\/departments\/(\d+)/',$path,$m) ? (int)$m[1] : null;
    $response = $method==='GET' ? ['success'=>true,'data'=>$id?$d->getById($id):$d->getAll()] : ['success'=>false];
} elseif (strpos($path, '/api/leads') === 0) {
    require_once __DIR__.'/../leads/Lead.php';
    $l = new Lead();
    $response = $method==='GET' ? ['success'=>true,'data'=>$l->getAll(),'stats'=>$l->getStats()] : ['success'=>false];
} elseif (strpos($path, '/api/projects') === 0) {
    require_once __DIR__.'/../projects/Project.php';
    $p = new Project();
    $response = $method==='GET' ? ['success'=>true,'data'=>$p->getAll(),'stats'=>$p->getStats()] : ['success'=>false];
} elseif (strpos($path, '/api/ai-agents') === 0) {
    require_once __DIR__.'/../ai-agents/AIAgent.php';
    $a = new AIAgent();
    $response = $method==='GET' ? ['success'=>true,'data'=>$a->getAll(),'stats'=>$a->getStats()] : ['success'=>false];
} elseif (strpos($path, '/api/dashboard') === 0 || strpos($path, '/api/stats') === 0) {
    require_once __DIR__.'/../dashboard/Dashboard.php';
    $d = new Dashboard();
    $response = ['success'=>true,'data'=>$d->getCEOStats()];
} else {
    $response = ['success'=>false,'message'=>'Endpoint not found','path'=>$path,'modules'=>['companies','departments','leads','projects','ai-agents','dashboard']];
}

echo json_encode($response, JSON_PRETTY_PRINT);
