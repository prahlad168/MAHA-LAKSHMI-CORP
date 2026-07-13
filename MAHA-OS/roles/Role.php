<?php
/** MAHA LAKSHMI AIOS - Role Class (Task #0005) */
class Role {
    private static $roles = [
        ['id'=>1,'code'=>'CEO','name'=>'Chief Executive Officer','level'=>10,'permissions'=>['*']],
        ['id'=>2,'code'=>'CTO','name'=>'Chief Technology Officer','level'=>9,'permissions'=>['company.*','dept.*','user.*','ai.manage','settings.manage']],
        ['id'=>3,'code'=>'CFO','name'=>'Chief Financial Officer','level'=>9,'permissions'=>['finance.*','report.*','company.view']],
        ['id'=>4,'code'=>'COO','name'=>'Chief Operating Officer','level'=>9,'permissions'=>['company.*','dept.*','user.*','report.*']],
        ['id'=>5,'code'=>'DIRECTOR','name'=>'Director','level'=>8,'permissions'=>['company.view','dept.manage','user.view','report.view']],
        ['id'=>6,'code'=>'MANAGER','name'=>'Manager','level'=>7,'permissions'=>['company.view','dept.view','report.view']],
        ['id'=>7,'code'=>'STAFF','name'=>'Staff','level'=>5,'permissions'=>['company.view','report.view']],
        ['id'=>8,'code'=>'AI','name'=>'AI Agent','level'=>1,'permissions'=>['ai.manage','report.view']]
    ];
    
    public function getAll() { return self::$roles; }
    public function getById($id) { foreach(self::$roles as $r) if($r['id']==$id) return $r; return null; }
    public function hasPermission($roleId, $perm) {
        $role = $this->getById($roleId);
        if(!$role) return false;
        return in_array('*',$role['permissions']) || in_array($perm,$role['permissions']);
    }
}
