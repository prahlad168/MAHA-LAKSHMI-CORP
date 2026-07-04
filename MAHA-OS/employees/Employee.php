<?php
/** MAHA LAKSHMI AIOS - Employee Class (Task #0006) */
class Employee {
    private static $employees = [
        ['id'=>1,'user_id'=>1,'code'=>'EMP001','name'=>'CEO - Prahlad','dept'=>'CEO Office','position'=>'CEO','status'=>'active'],
        ['id'=>2,'user_id'=>2,'code'=>'EMP002','name'=>'AI Finance','dept'=>'Finance','position'=>'AI Agent','status'=>'active'],
        ['id'=>3,'user_id'=>3,'code'=>'EMP003','name'=>'AI Marketing','dept'=>'Marketing','position'=>'AI Agent','status'=>'active'],
        ['id'=>4,'user_id'=>4,'code'=>'EMP004','name'=>'AI Sales','dept'=>'Sales','position'=>'AI Agent','status'=>'active'],
        ['id'=>5,'user_id'=>5,'code'=>'EMP005','name'=>'AI Support','dept'=>'Support','position'=>'AI Agent','status'=>'active']
    ];
    
    public function getAll() { return self::$employees; }
    public function getById($id) { foreach(self::$employees as $e) if($e['id']==$id) return $e; return null; }
    public function getByDepartment($deptId) { return array_filter(self::$employees, fn($e)=>$e['dept_id']==$deptId); }
    public function getStats() {
        return ['total'=>count(self::$employees),'active'=>count(array_filter(self::$employees,fn($e)=>$e['status']=='active'))];
    }
}
