#!/bin/bash
# =====================================================
# 🚀 GAURANGA + OLLAMA - SATU PERINTAH SAJA!
# =====================================================

echo "=========================================="
echo "🤖 GAURANGA - AI AGENT + OLLAMA AKTIF"
echo "=========================================="
echo ""

# 1. Start Ollama di background
echo "⚡ Memulai Ollama..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

# 2. Verify Ollama running
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama AKTIF di port 11434"
else
    echo "❌ Ollama gagal start"
    echo "   Jalankan manual: ollama serve"
    exit 1
fi

# 3. List available models
echo ""
echo "📋 Model Tersedia:"
curl -s http://127.0.0.1:11434/api/tags | python3 -c "import sys,json; [print(f'  • {m[\"name\"]}') for m in json.load(sys.stdin)['models']]" 2>/dev/null || echo "  • llama3.2"

# 4. Test GAURANGA
echo ""
echo "🧪 Testing GAURANGA..."
RESPONSE=$(curl -s http://127.0.0.1:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Kamu GAURANGA, AI Agent untuk MAHA LAKSHMI HOLDINGS. Jawab: Halo! Saya GAURANGA siap! 🔥",
  "stream": false
}' | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])" 2>/dev/null)

echo "🤖 GAURANGA: $RESPONSE"

# 5. Start interactive chat
echo ""
echo "=========================================="
echo "🎯 GAURANGA CHAT AKTIF!"
echo "=========================================="
echo "Ketik pesan untuk chat dengan GAURANGA"
echo "Ketik 'exit' untuk keluar"
echo "=========================================="
echo ""

# Interactive loop
python3 << 'PYTHON'
import json
import urllib.request
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"

SYSTEM = """Kamu adalah GAURANGA, AI Agent Leader untuk MAHA LAKSHMI HOLDINGS.
Nama: GAURANGA
Atasan: i Made Purna Ananda (Pak Pur)
Bahasa: Bahasa Indonesia"""

print("🤖 GAURANGA: Halo Pak Pur! GAURANGA siap menerima perintah! 🔥")
print()

while True:
    try:
        user = input("👤 Pak Pur: ").strip()
        if user.lower() in ['exit', 'quit', 'keluar', 'q']:
            print("🤖 GAURANGA: Baik Pak Pur! GAURANGA standby. 👋")
            break
        if not user:
            continue
        
        data = json.dumps({
            "model": MODEL,
            "prompt": f"{SYSTEM}\n\nPertanyaan: {user}",
            "stream": False
        }).encode()
        
        req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        
        print()
        print(f"🤖 GAURANGA: {result['response']}")
        print()
        
    except KeyboardInterrupt:
        print("\n🤖 GAURANGA: Baik Pak Pur! 👋")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
PYTHON
