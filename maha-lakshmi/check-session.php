<?php
/**
 * Session Check API
 * Returns JSON with authentication status
 */

session_start();

header('Content-Type: application/json');

if (isset($_SESSION['maha_lakshmi_auth']) && $_SESSION['maha_lakshmi_auth'] === true) {
    // Check session timeout (30 minutes)
    if (time() - $_SESSION['login_time'] > 1800) {
        session_destroy();
        echo json_encode(['authenticated' => false, 'message' => 'Session expired']);
    } else {
        echo json_encode([
            'authenticated' => true, 
            'username' => $_SESSION['username'] ?? 'admin',
            'login_time' => date('Y-m-d H:i:s', $_SESSION['login_time']),
            'last_activity' => date('Y-m-d H:i:s', $_SESSION['last_activity'] ?? time())
        ]);
    }
} else {
    echo json_encode(['authenticated' => false, 'message' => 'Not logged in']);
}
