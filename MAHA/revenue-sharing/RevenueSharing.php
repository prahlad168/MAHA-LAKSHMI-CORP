<?php
/**
 * MAHA LAKSHMI - Revenue Sharing System
 * CEO: Pak Pur | Bank: BCA 6485086645
 */
class RevenueSharing {
    private $distribution = [
        'ceo' => ['percent' => 60, 'name' => 'CEO Pak Pur', 'account' => 'BCA 6485086645'],
        'reinvestment' => ['percent' => 25, 'name' => 'Company Reserve'],
        'team_bonus' => ['percent' => 10, 'name' => 'Team Bonus'],
        'charity' => ['percent' => 5, 'name' => 'Charity/CSR']
    ];
    private $usdToIdr = 15500;
    
    public function calculate($revenueUsd) {
        $revenueIdr = $revenueUsd * $this->usdToIdr;
        $result = ['date' => date('Y-m-d'), 'total_usd' => $revenueUsd, 'total_idr' => $revenueIdr, 'distribution' => []];
        foreach ($this->distribution as $key => $item) {
            $result['distribution'][$key] = [
                'name' => $item['name'],
                'percent' => $item['percent'],
                'usd' => ($item['percent'] / 100) * $revenueUsd,
                'idr' => ($item['percent'] / 100) * $revenueIdr,
                'account' => $item['account'] ?? null
            ];
        }
        return $result;
    }
}
header('Content-Type: application/json');
$sales = new RevenueSharing();
$revenue = isset($_GET['revenue']) ? floatval($_GET['revenue']) : 26150;
echo json_encode($sales->calculate($revenue), JSON_PRETTY_PRINT);
