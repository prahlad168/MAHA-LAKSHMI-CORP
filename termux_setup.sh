#!/bin/bash
# =====================================================
# 🚀 GAURANGA ANDROID - TERMUX SETUP
# =====================================================
# Jalankan di Termux HP Android
# =====================================================

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🤖 GAURANGA PENGUASA ANDROID - SETUP                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ================================================
# STEP 1: UPDATE
# ================================================
echo "📦 Step 1: Update Termux packages..."
pkg update && pkg upgrade -y

# ================================================
# STEP 2: INSTALL BASIC TOOLS
# ================================================
echo ""
echo "📦 Step 2: Install basic tools..."
pkg install -y python git curl wget

# ================================================
# STEP 3: INSTALL OLLAMA
# ================================================
echo ""
echo "📦 Step 3: Install Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# ================================================
# STEP 4: DOWNLOAD AI MODEL
# ================================================
echo ""
echo "📦 Step 4: Download AI Model (llama3.2)..."
echo "   ⚠️ Ukuran ~2GB, membutuhkan waktu..."
ollama pull llama3.2

# ================================================
# STEP 5: INSTALL ADB
# ================================================
echo ""
echo "📦 Step 5: Install ADB (Android Debug Bridge)..."
pkg install -y android-tools

# ================================================
# STEP 6: ENABLE USB DEBUGGING INFO
# ================================================
echo ""
echo "📦 Step 6: USB Debugging Setup"
echo "   ⚠️ Di HP Anda, lakukan:"
echo "   1. Settings → About Phone"
echo "   2. Tap 'Build Number' 7x"
echo "   3. Settings → Developer Options"
echo "   4. Enable USB Debugging"
echo ""
echo "   Di Termux, jalankan:"
echo "   adb devices"
echo "   (授权电脑调试)
echo ""

# ================================================
# STEP 7: ENABLE WIRELESS ADB
# ================================================
echo ""
echo "📦 Step 7: Enable Wireless ADB"
echo "   Di Termux, jalankan:"
echo "   adb tcpip 5555"
echo "   adb connect 127.0.0.1:5555"
echo ""

# ================================================
# DOWNLOAD GAURANGA SCRIPT
# ================================================
echo ""
echo "📦 Step 8: Download GAURANGA Script..."
cd ~
wget -O gauranga_android.py "https://raw.githubusercontent.com/prahlad168/MAHA-LAKSHMI-CORP/main/gauranga_android.py"
chmod +x gauranga_android.py

# ================================================
# FINISH
# ================================================
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅ SETUP COMPLETE!                                        ║"
echo "║                                                              ║"
echo "║   NEXT STEPS:                                               ║"
echo "║   1. Start Ollama: ollama serve                            ║"
echo "║   2. Run GAURANGA: python gauranga_android.py              ║"
echo "║                                                              ║"
echo "║   Contoh perintah:                                          ║"
echo "║   • 'Apa kabar?'                                            ║"
echo "║   • 'Screenshot'                                            ║"
echo "║   • 'Matikan WiFi'                                         ║"
echo "║   • 'Buka Telegram'                                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════╝"
