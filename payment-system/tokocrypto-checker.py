#!/usr/bin/env python3
"""
🚀 TOKOCRYPTO WALLET CHECKER - SIMPEL VERSION
Cek saldo dan status wallet Tokocrypto

PAK PUR - Jalankan script ini dari komputer/laptop Anda
yang terhubung ke internet Indonesia (tanpa VPN)
"""

import urllib.request
import json
import hashlib
import hmac
import time

# ============================================
# ⚠️ KONFIGURASI
# ============================================

# Tokocrypto API Keys
# Dapatkan dari: https://www.tokocrypto.com/usercenter/settings/api-management
API_KEY = "d2050BeBEea0AbCB6bD44E4940b4776DDsWDYHAJ5FQK2exVsySNI0vTziRSfzKy"
SECRET_KEY = "96d395c894166AbAdec4cEBd938a868fhPTxJYbbEwR7yvUyWd2RdYasHOU4Hl0e"

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

def main():
    print()
    print("=" * 60)
    print("🚀 TOKOCRYPTO WALLET CHECKER")
    print("=" * 60)
    print()
    
    # Step 1: Test Koneksi
    print("STEP 1: Test Koneksi API...")
    print("-" * 40)
    
    result = api_request("GET", "/api/v1/account/info")
    
    if result.get("success"):
        print("✅ Koneksi BERHASIL!")
        print()
        data = result.get("data", {})
        print(f"📋 Info Akun:")
        print(f"   User ID: {data.get('userId', 'N/A')}")
        print(f"   Email: {data.get('email', 'N/A')}")
    else:
        print("❌ Koneksi GAGAL!")
        print(f"Error: {result.get('error')}")
        print()
        print("💡 Kemungkinan penyebab:")
        print("   1. VPN aktif - MATIKAN VPN!")
        print("   2. API keys expired - cek di tokocrypto.com")
        print("   3. Koneksi internet bermasalah")
        return
    
    print()
    print("STEP 2: Cek Saldo Wallet...")
    print("-" * 40)
    
    balances = api_request("GET", "/api/v1/account/balances")
    
    if balances.get("success"):
        print("✅ Berhasil mengambil data saldo!")
        print()
        
        assets = balances.get("data", [])
        
        # Cari USDT
        usdt_found = False
        print("📊 SALDO TOKOCRYPTO:")
        print("-" * 40)
        
        for asset in assets:
            free = float(asset.get('free', 0))
            locked = float(asset.get('locked', 0))
            total = free + locked
            
            if total > 0:
                symbol = asset.get('asset', 'N/A')
                print(f"   {symbol:8} | Free: {free:>15} | Locked: {locked:>15}")
                
                if symbol == 'USDT':
                    usdt_found = True
                    usdt_free = free
                    usdt_locked = locked
                    usdt_total = total
        
        if not usdt_found:
            print("   (Tidak ada aset dengan saldo)")
        
        print()
        print("=" * 60)
        
        # Summary USDT
        if usdt_found:
            print(f"💰 SALDO USDT:")
            print(f"   Available: {usdt_free:,.2f} USDT")
            print(f"   Locked:    {usdt_locked:,.2f} USDT")
            print(f"   TOTAL:     {usdt_total:,.2f} USDT")
            
            # Convert ke IDR (estimasi)
            price_idr = 16000  # Estimasi 1 USDT = Rp 16.000
            total_idr = usdt_total * price_idr
            print()
            print(f"💵 ESTIMASI DALAM RUPIAH:")
            print(f"   Total: Rp {total_idr:,.0f}")
            print()
            print(f"📝 NOTE: Kurs bisa berubah, cek harga aktual di Tokocrypto")
        else:
            print("❌ USDT TIDAK DITEMUKAN")
            print("   Buka app Tokocrypto → Wallet → Deposit USDT")
            print("   Gunakan network TRC20")
        
    else:
        print("❌ Gagal mengambil saldo!")
        print(f"Error: {balances.get('error')}")
    
    print()
    print("=" * 60)
    print("✅ CHECK SELESAI")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
