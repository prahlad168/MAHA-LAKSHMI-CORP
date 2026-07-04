<?php
/** MAHA LAKSHMI AIOS - Lead Class (Task #0008) */
class Lead {
    private static $leads = [
        ['id'=>1,'code'=>'LEAD001','name'=>'PT Maju Bersama','email'=>'contact@majubersama.co.id','company'=>'PT Maju Bersama','source'=>'Website','status'=>'new','score'=>75],
        ['id'=>2,'code'=>'LEAD002','name'=>'CV Sejahtera','email'=>'info@sejahtera.cv','company'=>'CV Sejahtera','source'=>'Referral','status'=>'qualified','score'=>85],
        ['id'=>3,'code'=>'LEAD003','name'=>'PT Indo Tech','email'=>'sales@indotech.id','company'=>'PT Indo Tech','source'=>'Cold Call','status'=>'contacted','score'=>60]
    ];
    
    public function getAll() { return self::$leads; }
    public function getById($id) { foreach(self::$leads as $l) if($l['id']==$id) return $l; return null; }
    public function getByStatus($status) { return array_filter(self::$leads,fn($l)=>$l['status']==$status); }
    
    public function getStats() {
        $total = count(self::$leads);
        $new = count(array_filter(self::$leads,fn($l)=>$l['status']=='new'));
        $qualified = count(array_filter(self::$leads,fn($l)=>$l['status']=='qualified'));
        $avgScore = array_sum(array_column(self::$leads,'score'))/$total;
        return ['total'=>$total,'new'=>$new,'qualified'=>$qualified,'avg_score'=>round($avgScore,1)];
    }
    
    public function create($data) { return ['success'=>true,'id'=>count(self::$leads)+1]; }
    public function update($id,$data) { return ['success'=>true,'message'=>'Lead updated']; }
}
