<?php
/**
 * MAHA OS - Database Migration Runner
 * Task #0001: Database Foundation
 * 
 * Usage: php migrate.php
 */

require_once __DIR__ . '/Database.php';

echo "===========================================\n";
echo "MAHA OS - Database Migration Runner\n";
echo "===========================================\n\n";

try {
    $db = Database::getInstance();
    
    // Check if database exists
    $dbPath = __DIR__ . '/maha.db';
    $isNew = !file_exists($dbPath);
    
    if ($isNew) {
        echo "📦 Creating new database...\n";
    } else {
        echo "📂 Database exists. Running migrations...\n";
    }
    
    // Run migrations
    echo "\n⚙️  Running migrations...\n";
    $db->migrate(__DIR__ . '/001_initial.sql');
    
    echo "✅ Migration completed!\n\n";
    
    // Verify tables
    echo "📋 Verifying tables...\n";
    $tables = $db->query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name");
    
    echo "\nTables created:\n";
    foreach ($tables as $table) {
        $count = $db->query("SELECT COUNT(*) as cnt FROM " . $table['name']);
        echo "  ✓ {$table['name']} ({$count[0]['cnt']} records)\n";
    }
    
    // Show settings
    echo "\n⚙️  System Settings:\n";
    $settings = $db->query("SELECT setting_key, setting_value FROM settings WHERE company_id IS NULL ORDER BY setting_key");
    foreach ($settings as $setting) {
        echo "  • {$setting['setting_key']}: {$setting['setting_value']}\n";
    }
    
    // Show companies
    echo "\n🏢 Companies:\n";
    $companies = $db->select('companies');
    foreach ($companies as $company) {
        echo "  • {$company['code']} - {$company['name']}\n";
    }
    
    echo "\n===========================================\n";
    echo "✅ Task #0001: Database Foundation - COMPLETE\n";
    echo "===========================================\n";
    echo "\nNext: php database/seed.php to add sample data\n";
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\n";
    exit(1);
}