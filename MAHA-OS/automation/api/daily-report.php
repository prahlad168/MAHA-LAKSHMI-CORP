<?php
header("Content-Type: application/json");
require_once __DIR__ . "/../DailyAutomation.php";
$gen = new DailyAutomation();
$data = $gen->run();
echo json_encode(["success"=>true,"date"=>date("Y-m-d"),"income_today"=>$data["income_generated"],"leads"=>$data["leads_generated"],"deals"=>$data["deals_generated"],"daily_target"=>33333333,"progress"=>round(($data["income_generated"]/33333333)*100,1),"deals_detail"=>$data["deals"]],JSON_PRETTY_PRINT);
