<?php
/** MAHA LAKSHMI AIOS - AI Agent Class (Task #0010) */
class AIAgent {
    private static $agents = [
        ['id'=>1,'code'=>'AGENT001','name'=>'Sales AI Agent','type'=>'sales','status'=>'active','tasks'=>24,'performance'=>92],
        ['id'=>2,'code'=>'AGENT002','name'=>'Marketing AI Agent','type'=>'marketing','status'=>'active','tasks'=>18,'performance'=>88],
        ['id'=>3,'code'=>'AGENT003','name'=>'Finance AI Agent','type'=>'finance','status'=>'active','tasks'=>15,'performance'=>95],
        ['id'=>4,'code'=>'AGENT004','name'=>'HR AI Agent','type'=>'hr','status'=>'active','tasks'=>12,'performance'=>90],
        ['id'=>5,'code'=>'AGENT005','name'=>'Support AI Agent','type'=>'support','status'=>'active','tasks'=>30,'performance'=>85],
        ['id'=>6,'code'=>'AGENT006','name'=>'Daily Report Agent','type'=>'automation','status'=>'active','tasks'=>3,'performance'=>100]
    ];
    
    public function getAll() { return self::$agents; }
    public function getById($id) { foreach(self::$agents as $a) if($a['id']==$id) return $a; return null; }
    public function getByType($type) { return array_filter(self::$agents,fn($a)=>$a['type']==$type); }
    
    public function getStats() {
        $total = count(self::$agents);
        $active = count(array_filter(self::$agents,fn($a)=>$a['status']=='active'));
        $totalTasks = array_sum(array_column(self::$agents,'tasks'));
        $avgPerf = array_sum(array_column(self::$agents,'performance'))/$total;
        return ['total'=>$total,'active'=>$active,'total_tasks'=>$totalTasks,'avg_performance'=>round($avgPerf,1)];
    }
}
