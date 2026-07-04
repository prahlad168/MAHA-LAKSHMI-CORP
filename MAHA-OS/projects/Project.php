<?php
/** MAHA LAKSHMI AIOS - Project Class (Task #0009) */
class Project {
    private static $projects = [
        ['id'=>1,'code'=>'PRJ001','name'=>'Website Redesign','client'=>'PT Maju','status'=>'in_progress','priority'=>'high','progress'=>60,'budget'=>50000000],
        ['id'=>2,'code'=>'PRJ002','name'=>'Mobile App','client'=>'CV Sejahtera','status'=>'planning','priority'=>'medium','progress'=>15,'budget'=>100000000],
        ['id'=>3,'code'=>'PRJ003','name'=>'CRM System','client'=>'PT Indo Tech','status'=>'review','priority'=>'high','progress'=>85,'budget'=>75000000]
    ];
    
    public function getAll() { return self::$projects; }
    public function getById($id) { foreach(self::$projects as $p) if($p['id']==$id) return $p; return null; }
    public function getStats() {
        $total = count(self::$projects);
        $active = count(array_filter(self::$projects,fn($p)=>$p['status']=='in_progress'));
        $completed = count(array_filter(self::$projects,fn($p)=>$p['status']=='completed'));
        $avg = array_sum(array_column(self::$projects,'progress'))/$total;
        return ['total'=>$total,'active'=>$active,'completed'=>$completed,'avg_progress'=>round($avg)];
    }
}
