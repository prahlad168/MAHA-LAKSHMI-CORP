#!/usr/bin/env python3
"""
🚀 TOKOCRYPTO CEO FEE TRANSFER
Transfer fee ke wallet crypto Pak Pur via Tokocrypto

PAK PUR - Jalankan script ini dari komputer/laptop Anda
yang terhubung ke internet Indonesia (tanpa VPN luar negeri)

SETIAP KALI JALANKAN, PASTIKAN:
1. Internet stabil (bukan VPN luar)
2. Python 3 sudah terinstall
3. Data di bawah sudah benar
"""

import urllib.request
import json
import hashlib
import hmac
import time
import os

# ============================================
# ⚠️ KONFIGURASI - PASTIKAN BENAR!
# ============================================

# Tokocrypto API Keys
# Dapatkan dari: https://www.tokocrypto.com/usercenter/settings/api-management
API_KEY = "d2050BeBEea0AbCB6bD44E4940b4776DDsWDYHAJ5FQK2exVsySNI0vTziRSfzKy"
SECRET_KEY = "96d395c894166AbAdec4cEBd938a868fhPTxJYbbEwR7yvUyWd2RdYasHOU4Hl0e"

# Wallet address tujuan - USDT TRC20 Pak Pur
RECIPIENT_WALLET = "TNFs1SP2C8HxGSZkSH3hJamf8ukgtnW7U6"

# Network (TRC20 = Tron network, fee lebih murah)
NETWORK = "TRC20"

# Jumlah transfer (dalam USDT)
AMOUNT = "50"  # ~Rp 750.000

# ============================================
# KODE DI BAWAH INI JANGAN DIUBAH
# ============================================

def generate_signature(secret_key, timestamp, method, path, body=""):
    """Generate Tokocrypto API signature"""
    message = f"{method}|{path}|{timestamp}|{body}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def api_request(method, path, body=""):
    """Execute Tokocrypto API request"""
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(SECRET_KEY, timestamp, method, path, body)
    
    headers = {
        "X-API-KEY": API_KEY,
        "X-SIGNATURE": signature,
        "X-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    
    url = f"https://www.tokocrypto.com{path}"
    
    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=headers)
        else:
            req = urllib.request.Request(
                url,
                data=body.encode() if body else b"{}",
                headers=headers,
                method=method
            )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return {"success": True, "data": json.loads(response.read())}
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"success": False, "error": f"HTTP {e.code}", "detail": error_body}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_account_info():
    """Ambil info akun Tokocrypto"""
    print("📊 Mengambil info akun...")
    result = api_request("GET", "/api/v1/account/info")
    return result

def get_balances():
    """Ambil semua saldo"""
    print("📊 Mengambil saldo...")
    result = api_request("GET", "/api/v1/account/balances")
    return result

def withdraw_crypto():
    """Withdraw USDT ke wallet Pak Pur"""
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/api/v1/withdraw/crypto"
    
    # Body untuk withdraw
    body = json.dumps({
        "symbol": "USDT",
        "address": RECIPIENT_WALLET,
        "amount": AMOUNT,
        "network": NETWORK,
        "uniqueId": f"TX{int(time.time())}"
    })
    
    print(f"📤 Mengirim {AMOUNT} USDT ke {RECIPIENT_WALLET[:15]}...")
    result = api_request(method, path, body)
    return result

def print_result(result, title):
    """Print hasil API call"""
    print()
    print(title)
    print("-" * 50)
    
    if result.get("success"):
        print("✅ BERHASIL!")
        print(json.dumps(result.get("data", {}), indent=2))
    else:
        print("❌ GAGAL!")
        print(f"Error: {result.get('error')}")
        if "detail" in result:
            print(f"Detail: {result['detail']}")
    
    print()
    return result.get("success", False)

def main():
    print("=" * 60)
    print("🚀 TOKOCRYPTO CEO FEE TRANSFER")
    print("=" * 60)
    print()
    
    # Validasi konfigurasi
    if "ISI_ADDRESS" in RECIPIENT_WALLET:
        print("❌ ERROR: Wallet address belum diisi!")
        print()
        print("📝 CARA MENGISI:")
        print("1. Buka Tokocrypto App")
        print("2. Pilih USDT")
        print("3. Klik 'Deposit' atau 'Receive'")
        print("4. Copy alamat TRC20 (dimulai huruf T)")
        print("5. Paste di script ini, gantikan 'ISI_ADDRESS...'")
        print()
        print("⚠️ PASTIKAN NETWORK = TRC20")
        print()
        return
    
    print(f"📋 KONFIGURASI:")
    print(f"   Wallet: {RECIPIENT_WALLET}")
    print(f"   Network: {NETWORK}")
    print(f"   Amount: {AMOUNT} USDT")
    print()
    
    # Step 1: Test koneksi
    print("STEP 1: Test Koneksi API")
    print("-" * 50)
    
    info = get_account_info()
    if not print_result(info, "📋 INFO AKUN"):
        print("💡 Kemungkinan penyebab:")
        print("   - VPN aktif dengan server luar Indonesia")
        print("   - API keys tidak valid atau expired")
        print("   - Koneksi internet terblokir")
        print()
        return
    
    print("✅ Koneksi berhasil!")
    print()
    
    # Step 2: Cek saldo
    print("STEP 2: Cek Saldo")
    print("-" * 50)
    
    balances = get_balances()
    if not print_result(balances, "📊 SALDO"):
        print("💡 Gagal mengambil saldo")
        return
    
    # Cari saldo USDT
    usdt_balance = 0
    if "data" in balances:
        for asset in balances["data"]:
            if asset.get("asset") == "USDT":
                usdt_balance = float(asset.get("free", 0))
                break
    
    print(f"💰 Saldo USDT: {usdt_balance}")
    print()
    
    # Step 3: Konfirmasi
    print("STEP 3: Konfirmasi Transfer")
    print("-" * 50)
    print(f"📤 Transfer: {AMOUNT} USDT")
    print(f"📍 Tujuan: {RECIPIENT_WALLET[:20]}...")
    print(f"🌐 Network: {NETWORK}")
    print()
    
    confirm = input("✅ Ketik 'YA' untuk konfirmasi: ").strip().upper()
    
    if confirm != "YA":
        print("Transfer dibatalkan.")
        return
    
    print()
    
    # Step 4: Execute transfer
    print("STEP 4: Eksekusi Transfer")
    print("-" * 50)
    
    result = withdraw_crypto()
    success = print_result(result, "📤 HASIL TRANSFER")
    
    # Final status
    print("=" * 60)
    if success:
        print("🎉 TRANSFER BERHASIL!")
        print()
        print("📋 Langkah selanjutnya:")
        print("1. Cek wallet untuk konfirmasi terima")
        print("2. Jual USDT di Tokocrypto ke IDR")
        print("3. Transfer IDR ke BCA 6485086645")
    else:
        print("❌ TRANSFER GAGAL!")
        print()
        print("📞 Hubungi Tokocrypto Support:")
        print("   https://t.me/tokocryptosupport")
    print("=" * 60)

if __name__ == "__main__":
    main()
