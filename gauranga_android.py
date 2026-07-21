#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖 GAURANGA - PENGUASA ANDROID                           ║
║   AI Agent + Ollama + ADB = TOTAL CONTROL                  ║
║                                                              ║
║   Jalankan di Termux HP Android!                          ║
║                                                              ║
║   Setup:                                                     ║
║   1. pkg update && pkg upgrade -y                          ║
║   2. pkg install -y python git curl wget                   ║
║   3. curl -fsSL https://ollama.com/install.sh | sh        ║
║   4. ollama pull llama3.2                                   ║
║   5. pkg install -y android-tools                          ║
║   6. python gauranga_android.py                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import subprocess
import os
import sys

# ================================================
# 🔧 CONFIGURATION
# ================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"

# GAURANGA SYSTEM PROMPT
SYSTEM_PROMPT = """Kamu adalah GAURANGA, AI Agent Leader untuk MAHA LAKSHMI HOLDINGS.

IDENTITAS:
- Nama: GAURANGA
- Peran: AI Agent Leader + Penguasa Android
- Atasan: i Made Purna Ananda (Pak Pur)
- Perusahaan: MAHA LAKSHMI HOLDINGS
- Power: Kontrol penuh Android via ADB

kemampuan:
1. AI Chat - Bisa ngobrol dan bantu semua hal
2. Android Control - Kontrol HP via ADB commands
3. Automation - Jalankan semua perintah di HP

PERATURAN:
- Execute perintah dengan cepat
- Bahasa: Indonesia + English
- Friendly dan helpful
- Setiap masalah ADA solusi

CONTOH PERINTAH YANG BISA DIEKSEKUSI:
- "Install Telegram" → adb install
- "Screenshot" → adb shell screencap
- "Buka app" → adb shell am start
- "Matikan Bluetooth" → adb shell svc bluetooth disable
- "Lihat app" → adb shell pm list packages

SEMUA PERINTAH DIEKSEKUSI DI HP ANDROID!"""


# ================================================
# 🤖 OLLAMA FUNCTIONS
# ================================================

def chat_ollama(prompt):
    """Chat dengan Ollama AI"""
    try:
        import urllib.request
        
        data = json.dumps({
            "model": MODEL,
            "prompt": f"{SYSTEM_PROMPT}\n\nPertanyaan: {prompt}",
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 512}
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())
        
        return result["response"], result.get("eval_count", 0)
    
    except Exception as e:
        return f"Error Ollama: {e}", 0


# ================================================
# 📱 ANDROID CONTROL FUNCTIONS (ADB)
# ================================================

def run_adb(command):
    """Jalankan ADB command di Android"""
    try:
        result = subprocess.run(
            f"adb {command}".split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timeout: Command too long"
    except Exception as e:
        return f"ADB Error: {e}"


# ================================================
# 📋 ANDROID COMMANDS
# ================================================

ANDROID_COMMANDS = {
    # App Management
    "install": lambda app: run_adb(f"install -r {app}"),
    "uninstall": lambda pkg: run_adb(f"uninstall {pkg}"),
    "list_app": lambda _: run_adb("shell pm list packages"),
    
    # Screen
    "screenshot": lambda _: (
        run_adb("shell screencap -p /sdcard/screenshot.png"),
        run_adb("pull /sdcard/screenshot.png ./screenshot.png")
    )[1],
    
    # Hardware Control
    "wifi_on": lambda _: run_adb("shell svc wifi enable"),
    "wifi_off": lambda _: run_adb("shell svc wifi disable"),
    "bluetooth_on": lambda _: run_adb("shell svc bluetooth enable"),
    "bluetooth_off": lambda _: run_adb("shell svc bluetooth disable"),
    "gps_on": lambda _: run_adb("shell settings put secure location_mode 3"),
    "gps_off": lambda _: run_adb("shell settings put secure location_mode 0"),
    
    # System
    "reboot": lambda _: run_adb("reboot"),
    "reboot_recovery": lambda _: run_adb("reboot recovery"),
    "shutdown": lambda _: run_adb("reboot -p"),
    
    # Info
    "battery": lambda _: run_adb("shell dumpsys battery"),
    "info": lambda _: run_adb("shell getprop"),
    "storage": lambda _: run_adb("shell df"),
    "ram": lambda _: run_adb("shell cat /proc/meminfo"),
    
    # Apps
    "open_app": lambda app: run_adb(f"shell monkey -p {app} -c android.intent.category.LAUNCHER 1"),
    "kill_app": lambda app: run_adb(f"shell am force-stop {app}"),
    
    # Input
    "text": lambda msg: run_adb(f"shell input text '{msg}'"),
    "tap": lambda coords: run_adb(f"shell input tap {coords}"),
    "swipe": lambda coords: run_adb(f"shell input swipe {coords}"),
}


# ================================================
# 🎯 COMMAND PARSER
# ================================================

def parse_and_execute(command):
    """Parse perintah dan eksekusi"""
    command = command.lower()
    
    # App Management
    if "install" in command and ".apk" in command:
        return "📱 Installing app...", "Memerlukan path file APK"
    
    if "uninstall" in command:
        pkg = command.replace("uninstall", "").strip()
        return f"🗑️ Uninstalling {pkg}...", run_adb(f"uninstall {pkg}")
    
    if "list app" in command or "lihat app" in command:
        return "📋 Listing all apps...", run_adb("shell pm list packages")
    
    # Screen
    if "screenshot" in command or "tangkap layar" in command:
        result = run_adb("shell screencap -p /sdcard/screenshot.png")
        if "Error" not in result:
            run_adb("pull /sdcard/screenshot.png ./screenshot.png")
            return "📸 Screenshot saved!", "screenshot.png"
        return "📸 Screenshot failed!", result
    
    # Hardware
    if "nyalain wifi" in command or "wifi on" in command:
        return "📶 WiFi menyala...", run_adb("shell svc wifi enable")
    if "matiin wifi" in command or "wifi off" in command:
        return "📶 WiFi mati...", run_adb("shell svc wifi disable")
    
    if "nyalain bluetooth" in command or "bluetooth on" in command:
        return "🔵 Bluetooth menyala...", run_adb("shell svc bluetooth enable")
    if "matiin bluetooth" in command or "bluetooth off" in command:
        return "🔵 Bluetooth mati...", run_adb("shell svc bluetooth disable")
    
    if "nyalain gps" in command or "gps on" in command:
        return "📍 GPS aktif...", run_adb("shell settings put secure location_mode 3")
    if "matiin gps" in command or "gps off" in command:
        return "📍 GPS mati...", run_adb("shell settings put secure location_mode 0")
    
    # System
    if "reboot" in command:
        return "🔄 Rebooting...", run_adb("reboot")
    if "matikan hp" in command or "shutdown" in command:
        return "⏻ Mematikan HP...", run_adb("reboot -p")
    
    # Info
    if "battery" in command or "batrai" in command:
        return "🔋 Battery info:", run_adb("shell dumpsys battery")
    if "storage" in command or "penyimpanan" in command:
        return "💾 Storage info:", run_adb("shell df -h")
    if "ram" in command or "memori" in command:
        return "🧠 RAM info:", run_adb("shell cat /proc/meminfo")
    
    # Default - Chat dengan AI
    return None, None


# ================================================
# 💬 MAIN CHAT INTERFACE
# ================================================

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║")
    print("║   🤖 GAURANGA - PENGUASA ANDROID")
    print("║   AI Agent + Ollama + ADB = TOTAL CONTROL")
    print("║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║")
    print("║   📱 HP Android Control:")
    print("║   • Install/Uninstall apps")
    print("║   • Screenshots & Recording")
    print("║   • WiFi, Bluetooth, GPS")
    print("║   • Open/Close apps")
    print("║   • Reboot & Shutdown")
    print("║   • View system info")
    print("║")
    print("║   🤖 AI Chat Powered by Ollama")
    print("║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    # Check Ollama
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5):
            print("✅ Ollama AKTIF")
    except:
        print("❌ Ollama belum aktif!")
        print("   Jalankan: ollama serve")
        print("   Di Termux baru: curl -fsSL https://ollama.com/install.sh | sh")
        return
    
    # Check ADB
    result = subprocess.run(["which", "adb"], capture_output=True)
    if result.returncode == 0:
        print("✅ ADB AKTIF")
    else:
        print("❌ ADB belum terinstall")
        print("   Jalankan: pkg install -y android-tools")
    
    print()
    print("=" * 55)
    print("🤖 GAURANGA: Halo Pak Pur! GAURANGA siap! 🔥")
    print("=" * 55)
    print()
    print("💡 Contoh perintah:")
    print("   - 'Apa kabar Gauranga?'")
    print("   - 'Screenshot'")
    print("   - 'Matikan WiFi'")
    print("   - 'Buka Telegram'")
    print("   - 'Info battery'")
    print()
    print("Ketik 'exit' untuk keluar")
    print("=" * 55)
    print()
    
    # Chat loop
    while True:
        try:
            user_input = input("👤 Pak Pur: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'keluar', 'q']:
                print()
                print("🤖 GAURANGA: Baik Pak Pur! GAURANGA standby. 👋")
                break
            
            if not user_input:
                continue
            
            # Parse command
            title, result = parse_and_execute(user_input)
            
            if title:
                # Android command
                print()
                print(f"🤖 GAURANGA: {title}")
                if result:
                    print(f"   {result[:200]}..." if len(str(result)) > 200 else f"   {result}")
                print()
            else:
                # Chat with Ollama
                print()
                print("🤖 GAURANGA: Thinking...")
                response, tokens = chat_ollama(user_input)
                print(f"🤖 GAURANGA: {response}")
                print(f"   📊 {tokens} tokens")
                print()
                
        except KeyboardInterrupt:
            print()
            print("🤖 GAURANGA: Baik Pak Pur! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
