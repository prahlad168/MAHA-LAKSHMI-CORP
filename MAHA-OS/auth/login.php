<?php
/**
 * MAHA LAKSHMI AIOS - Login Page
 * Task #0002
 */
require_once __DIR__ . '/Auth.php';
$auth = new Auth();
if ($auth->check()) { header('Location: /dashboard'); exit; }
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - MAHA AIOS</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root { --primary: #1a5f5a; --primary-dark: #0d3d3a; --secondary: #c9a86c; --success: #22c55e; --danger: #ef4444; --gray: #64748b; }
        body { font-family: 'Nunito', sans-serif; background: linear-gradient(135deg, var(--primary-dark), var(--primary)); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: white; border-radius: 20px; box-shadow: 0 25px 50px rgba(0,0,0,0.25); max-width: 420px; width: 100%; overflow: hidden; }
        .header { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); padding: 40px 30px; text-align: center; color: white; }
        .logo { width: 70px; height: 70px; background: var(--secondary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 32px; }
        .header h1 { font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 5px; }
        .header p { opacity: 0.8; font-size: 0.9rem; }
        .body { padding: 35px 30px; }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; font-weight: 600; margin-bottom: 8px; color: #1e293b; }
        .form-input { width: 100%; padding: 14px 16px; border: 2px solid #e2e8f0; border-radius: 10px; font-size: 1rem; transition: all 0.3s; }
        .form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(26,95,90,0.1); }
        .btn { width: 100%; padding: 15px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(26,95,90,0.3); }
        .alert { padding: 14px; border-radius: 10px; margin-bottom: 20px; display: none; }
        .alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
        .alert-success { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
        .alert.show { display: flex; align-items: center; gap: 10px; }
        .demo { background: #f0fdf4; border-radius: 10px; padding: 15px; margin-top: 20px; text-align: center; }
        .demo h4 { font-size: 0.85rem; margin-bottom: 10px; }
        .demo code { background: #e2e8f0; padding: 5px 10px; border-radius: 5px; font-size: 0.85rem; }
        .use-demo { background: var(--primary); color: white; border: none; padding: 5px 12px; border-radius: 5px; cursor: pointer; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="logo">👑</div>
            <h1>MAHA LAKSHMI AIOS</h1>
            <p>AI Operating System - Enterprise</p>
        </div>
        <div class="body">
            <div id="alert" class="alert"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-input" id="email" placeholder="ceo@mahalakshmi.id" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" id="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn" id="btn">Masuk</button>
            </form>
            <div class="demo">
                <h4>🔑 Demo Account</h4>
                <code>ceo@mahalakshmi.id</code>
                <button class="use-demo" onclick="document.getElementById('email').value='ceo@mahalakshmi.id';document.getElementById('password').value='password'">Use</button>
            </div>
        </div>
    </div>
    <script>
    const API = '/api/auth.php';
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn');
        btn.disabled = true;
        btn.textContent = 'Loading...';
        try {
            const res = await fetch(API + '?action=login', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({email: document.getElementById('email').value, password: document.getElementById('password').value})
            });
            const data = await res.json();
            const alert = document.getElementById('alert');
            if (data.success) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                alert.className = 'alert alert-success show';
                alert.innerHTML = '<i class="fas fa-check-circle"></i> Login berhasil! Mengalihkan...';
                setTimeout(() => window.location.href = '/dashboard', 1000);
            } else {
                alert.className = 'alert alert-error show';
                alert.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + data.message;
            }
        } catch (err) {
            document.getElementById('alert').className = 'alert alert-error show';
            document.getElementById('alert').innerHTML = '<i class="fas fa-exclamation-circle"></i> Terjadi kesalahan';
        }
        btn.disabled = false;
        btn.textContent = 'Masuk';
    });
    </script>
</body>
</html>
