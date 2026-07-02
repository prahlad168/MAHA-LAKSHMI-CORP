<?php
/**
 * MAHA LAKSHMI - Login Page with Human Verification
 * CEO Dashboard Access
 */

session_start();

// Generate CSRF token
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// Credentials
define('VALID_USERNAME', 'admin');
define('VALID_PASSWORD', 'Lilasravana168$');

$error = "";
$success = "";

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    $success = "Anda sudah logout. Silakan login kembali.";
}

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Verify CSRF token
    if (!isset($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
        $error = "Invalid request. Silakan refresh halaman.";
    }
    // Verify human check (math challenge)
    elseif (!isset($_POST['human_verify']) || !isset($_POST['human_answer'])) {
        $error = "Verifikasi manusia wajib diisi!";
    }
    elseif (!isset($_SESSION['human_answer']) || (int)$_POST['human_verify'] !== (int)$_SESSION['human_answer']) {
        $error = "Jawaban verifikasi salah. Coba lagi!";
    }
    elseif (!isset($_POST['username']) || !isset($_POST['password'])) {
        $error = "Username dan password wajib diisi!";
    }
    else {
        $user = trim($_POST['username']);
        $pass = $_POST['password'];
        
        if ($user === VALID_USERNAME && $pass === VALID_PASSWORD) {
            // Regenerate session ID for security
            session_regenerate_id(true);
            
            $_SESSION['maha_lakshmi_auth'] = true;
            $_SESSION['login_time'] = time();
            $_SESSION['last_activity'] = time();
            $_SESSION['username'] = $user;
            
            // Regenerate CSRF token after login
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
            
            // Redirect to CEO report
            header('Location: ceo-report.html');
            exit;
        } else {
            $error = "Username atau password salah!";
        }
    }
}

// Generate math challenge
$num1 = rand(1, 9);
$num2 = rand(1, 9);
$_SESSION['human_answer'] = $num1 + $num2;
$human_question = "$num1 + $num2";

// Check if already logged in
if (isset($_SESSION['maha_lakshmi_auth']) && $_SESSION['maha_lakshmi_auth'] === true) {
    // Check session timeout (30 minutes)
    if (time() - $_SESSION['login_time'] > 1800) {
        session_destroy();
        $error = "Session expired. Silakan login ulang.";
    } else {
        // Update last activity
        $_SESSION['last_activity'] = time();
        header('Location: ceo-report.html');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maha Lakshmi - Login with Verification</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Nunito:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Nunito', sans-serif;
            background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 50%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: rgba(26, 26, 46, 0.98);
            border-radius: 25px;
            padding: 45px;
            width: 450px;
            max-width: 100%;
            border: 2px solid #FFD700;
            box-shadow: 0 25px 80px rgba(255, 215, 0, 0.15);
        }
        .logo {
            text-align: center;
            margin-bottom: 35px;
        }
        .logo-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
        .logo h1 {
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            background: linear-gradient(135deg, #FFD700 0%, #FFF8DC 50%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }
        .logo p {
            color: #888;
            font-size: 14px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #aaa;
            font-size: 13px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .form-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid rgba(255, 215, 0, 0.3);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 16px;
            transition: all 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #FFD700;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.2);
            background: rgba(255, 255, 255, 0.08);
        }
        .form-group input::placeholder {
            color: #555;
        }
        
        /* Human Verification */
        .human-verification {
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid rgba(255, 215, 0, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .human-verification h3 {
            color: #FFD700;
            font-size: 14px;
            margin-bottom: 15px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .human-verification .math-challenge {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .human-verification .question {
            color: #fff;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 15px;
            font-family: 'Playfair Display', serif;
        }
        .human-verification input {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid rgba(255, 215, 0, 0.5);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: #FFD700;
            font-size: 20px;
            text-align: center;
            font-weight: 700;
        }
        .human-verification input:focus {
            outline: none;
            border-color: #FFD700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }
        .human-verification .hint {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
            text-align: center;
        }
        
        .btn-login {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%);
            border: none;
            border-radius: 12px;
            color: #0F0F23;
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(255, 215, 0, 0.4);
        }
        .btn-login:active {
            transform: translateY(-1px);
        }
        
        .error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid #EF4444;
            color: #EF4444;
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            animation: shake 0.5s ease-in-out;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .success {
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid #22C55E;
            color: #22C55E;
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #555;
            font-size: 12px;
        }
        .footer span {
            color: #FFD700;
        }
        
        .security-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 15px;
            color: #666;
            font-size: 11px;
        }
        .security-badge i {
            color: #22C55E;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <div class="logo-icon">👑</div>
            <h1>MAHA LAKSHMI</h1>
            <p>CEO Dashboard</p>
        </div>
        
        <?php if ($error): ?>
        <div class="error">
            <i class="fas fa-exclamation-circle"></i> <?php echo htmlspecialchars($error); ?>
        </div>
        <?php endif; ?>
        
        <?php if ($success): ?>
        <div class="success">
            <i class="fas fa-check-circle"></i> <?php echo htmlspecialchars($success); ?>
        </div>
        <?php endif; ?>
        
        <form method="POST" action="">
            <!-- CSRF Token -->
            <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>">
            
            <div class="form-group">
                <label><i class="fas fa-user"></i> Username</label>
                <input type="text" name="username" placeholder="Masukkan username" required autofocus>
            </div>
            
            <div class="form-group">
                <label><i class="fas fa-lock"></i> Password</label>
                <input type="password" name="password" placeholder="Masukkan password" required>
            </div>
            
            <!-- Human Verification -->
            <div class="human-verification">
                <h3><i class="fas fa-shield-alt"></i> Verifikasi Manusia</h3>
                <div class="math-challenge">
                    <div class="question">Berapa hasil dari <?php echo $human_question; ?> ?</div>
                    <input type="number" name="human_verify" placeholder="?" required min="1" max="20">
                </div>
                <p class="hint">Jawab pertanyaan matematika di atas untuk verifikasi</p>
            </div>
            
            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt"></i> Masuk
            </button>
        </form>
        
        <div class="security-badge">
            <i class="fas fa-lock"></i>
            <span>Dilindungi dengan CSRF Token & Human Verification</span>
        </div>
        
        <div class="footer">
            <p>Powered by <span>GAURANGA</span> AI</p>
            <p style="margin-top: 5px;">© 2026 Maha Lakshmi</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh page if session expires
        setInterval(function() {
            fetch('check-session.php').then(r => r.json()).then(data => {
                if (!data.authenticated) {
                    window.location.reload();
                }
            }).catch(() => {});
        }, 60000);
    </script>
</body>
</html>
