<?php
session_start();

// Simple password protection
$PASSWORD = "mahalakshmi2024"; // Change this password
$USERNAME = "admin";

$error = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user = $_POST['username'] ?? '';
    $pass = $_POST['password'] ?? '';
    
    if ($user === $USERNAME && $pass === $PASSWORD) {
        $_SESSION['maha_lakshmi_auth'] = true;
        $_SESSION['login_time'] = time();
        header('Location: index.html');
        exit;
    } else {
        $error = "Username atau password salah!";
    }
}

// Check if already logged in
if (isset($_SESSION['maha_lakshmi_auth']) && $_SESSION['maha_lakshmi_auth'] === true) {
    // Check session timeout (30 minutes)
    if (time() - $_SESSION['login_time'] > 1800) {
        session_destroy();
        $error = "Session expired. Silakan login ulang.";
    } else {
        header('Location: index.html');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maha Lakshmi - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 50%, #2D1B4E 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: rgba(26, 26, 46, 0.95);
            border-radius: 20px;
            padding: 50px;
            width: 400px;
            max-width: 90%;
            border: 2px solid #FFD700;
            box-shadow: 0 20px 60px rgba(255, 215, 0, 0.2);
        }
        .logo {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo-icon {
            font-size: 64px;
            margin-bottom: 15px;
        }
        .logo h1 {
            font-size: 28px;
            background: linear-gradient(135deg, #FFD700 0%, #FFF8DC 50%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
        }
        .logo p {
            color: #888;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            color: #888;
            font-size: 13px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .form-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid rgba(255, 215, 0, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 16px;
            transition: all 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #FFD700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        }
        .form-group input::placeholder {
            color: #555;
        }
        .btn-login {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #B8860B 0%, #FFD700 100%);
            border: none;
            border-radius: 10px;
            color: #0F0F23;
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.4);
        }
        .error {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #EF4444;
            color: #EF4444;
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 25px;
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
        .lock-icon {
            text-align: center;
            margin-bottom: 20px;
        }
        .lock-icon svg {
            width: 50px;
            height: 50px;
            fill: #FFD700;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <div class="logo-icon">💰</div>
            <h1>Maha Lakshmi</h1>
            <p>Revenue Intelligence</p>
        </div>
        
        <?php if ($error): ?>
        <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Masukkan username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Masukkan password" required>
            </div>
            <button type="submit" class="btn-login">🔓 Masuk</button>
        </form>
        
        <div class="footer">
            <p>Powered by <span>GAURANGA</span> AI</p>
            <p style="margin-top: 5px;">© 2024 Maha Lakshmi</p>
        </div>
    </div>
</body>
</html>