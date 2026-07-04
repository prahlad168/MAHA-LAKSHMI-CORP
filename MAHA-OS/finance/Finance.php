<?php
/** MAHA LAKSHMI AIOS - Finance Class (Task #0007) */
class Finance {
    private static $transactions = [];
    private static $invoices = [
        ['id'=>1,'number'=>'INV-2026-001','client'=>'Client A','amount'=>10000000,'tax'=>1100000,'total'=>11100000,'status'=>'paid','date'=>'2026-01-15'],
        ['id'=>2,'number'=>'INV-2026-002','client'=>'Client B','amount'=>25000000,'tax'=>2750000,'total'=>27750000,'status'=>'pending','date'=>'2026-02-01']
    ];
    
    public function getInvoices() { return self::$invoices; }
    public function getInvoice($id) { foreach(self::$invoices as $i) if($i['id']==$id) return $i; return null; }
    
    public function getStats() {
        $total = array_sum(array_column(self::$invoices,'total'));
        $paid = array_sum(array_filter(self::$invoices,fn($i)=>$i['status']=='paid'));
        return ['total_invoices'=>count(self::$invoices),'total_amount'=>$total,'paid'=>$paid,'pending'=>$total-$paid];
    }
    
    public function createInvoice($data) {
        return ['success'=>true,'id'=>count(self::$invoices)+1,'message'=>'Invoice created'];
    }
}
