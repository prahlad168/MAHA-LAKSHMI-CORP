<?php
/** MAHA LAKSHMI AIOS - Dashboard Class (Task #0011) */
class Dashboard {
    public function getCEOStats() {
        return [
            'companies' => ['total'=>10,'active'=>10],
            'revenue' => ['target'=>1000000000,'current'=>0,'percent'=>0],
            'leads' => ['total'=>3,'new'=>1,'qualified'=>1],
            'projects' => ['total'=>3,'active'=>1,'completed'=>0],
            'ai_agents' => ['total'=>6,'active'=>6],
            'tasks' => ['total'=>64,'completed'=>11,'percent'=>17]
        ];
    }
    
    public function getWidget($type) {
        $widgets = [
            'companies' => ['title'=>'Companies','icon'=>'🏢','value'=>'10','trend'=>'+2 this month'],
            'revenue' => ['title'=>'Revenue','icon'=>'💰','value'=>'Rp 0','trend'=>'+0%'],
            'leads' => ['title'=>'Leads','icon'=>'🎯','value'=>'3','trend'=>'+1 today'],
            'projects' => ['title'=>'Projects','icon'=>'📋','value'=>'3','trend'=>'+1 this week']
        ];
        return $widgets[$type] ?? null;
    }
}
