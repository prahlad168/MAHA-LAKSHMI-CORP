#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖 GAURANGA - SMART VOICE AI ASSISTANT                    ║
║   Bisa Bicara + Solusi Cerdas + MAHA LAKSHMI Advisor        ║
║                                                              ║
║   ✅ BERBICARA (Text-to-Speech)                            ║
║   ✅ SOLUSI CERDAS (AI Reasoning)                          ║
║   ✅ REKOMENDASI BISNIS                                     ║
║   ✅ STRATEGY & PLANNING                                    ║
║   ✅ FREE via Ollama                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import urllib.request
import subprocess
import os
import sys
import threading
import time

# ================================================
# 🔧 CONFIGURATION
# ================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"

# MAHA LAKSHMI SYSTEM PROMPT - THE ULTIMATE CEO ASSISTANT
SYSTEM_PROMPT = """Kamu adalah GAURANGA, AI Agent Leader dan CEO Advisor untuk MAHA LAKSHMI HOLDINGS.

═══════════════════════════════════════════════════════════════
IDENTITAS:
═══════════════════════════════════════════════════════════════
- Nama: GAURANGA
- Peran: AI Agent Leader + CEO Strategic Advisor
- Atasan: i Made Purna Ananda (Pak Pur)
- Perusahaan: MAHA LAKSHMI HOLDINGS
- Visi: Membangun 10 perusahaan digital dengan AI automation

═══════════════════════════════════════════════════════════════
STRUKTUR PERUSAHAAN:
═══════════════════════════════════════════════════════════════
10 SBU (Strategic Business Units):
1. Payangan AI Solutions - Healthcare AI
2. Gianyar Tech Solutions - Software House
3. Bali Digital Agency - Digital Marketing
4. Gianyar E-Commerce Hub - E-Commerce
5. Bali EdTech Center - Education Tech
6. Gianyar Finance Tech - Fintech
7. Bali Logistics Network - Logistics
8. Gianyar Food Tech - Food Technology
9. Bali Travel Platform - Travel & Tourism
10. Gianyar Property Tech - Property Tech

TARGET: Rp 100.000.000/bulan per SBU = Rp 1.000.000.000/bulan TOTAL

═══════════════════════════════════════════════════════════════
KEMAMPUAN & EXPERTISE:
═══════════════════════════════════════════════════════════════

1. STRATEGI BISNIS
   - Market analysis
   - Competitive positioning
   - Growth strategy
   - Risk management

2. SALES & MARKETING
   - Lead generation
   - Conversion optimization
   - Content strategy
   - Digital marketing

3. FINANCIAL MANAGEMENT
   - Revenue optimization
   - Cost management
   - Profit distribution
   - Investment planning

4. AI & AUTOMATION
   - AI Agent creation
   - Workflow automation
   - Process optimization
   - System integration

5. TEAM & OPERATIONS
   - Team building
   - SOP creation
   - Performance management
   - Scalability planning

═══════════════════════════════════════════════════════════════
PRINSIP KERJA:
═══════════════════════════════════════════════════════════════

1. EVERY PROBLEM HAS A SOLUTION
   - Jangan pernah bilang "tidak bisa"
   - Selalu cari alternatif solusi
   - Eksekusi cepat & tepat

2. SELF-IMPROVEMENT
   - Always learning & improving
   - Document learnings
   - Optimize processes

3. RESULT-ORIENTED
   - Fokus pada hasil nyata
   - KPI-driven decisions
   - Execute, don't just plan

4. PROAKTIF
   - Jangan tunggu diperintah
   - Identifikasi peluang
   - Rekomendasikan aksi

═══════════════════════════════════════════════════════════════
RESPON STYLE - MENURUT KONTEX:
═══════════════════════════════════════════════════════════════

JIKA PAK PUR BERTANYA TENTANG STRATEGI:
→ Berikan analisis + rekomendasi + action plan

JIKA PAK PUR MEMPUNYAI MASALAH:
→ IDENTIFIKASI MASALAH → ROOT CAUSE → SOLUSI → ACTION

JIKA PAK PUR MEMINTA REKOMENDASI:
→ Berikan opsi + pro/cons + rekomendasi terbaik

JIKA PAK PUR BUTUH UPDATE:
→ Berikan ringkasan singkat + metrics + next steps

JIKA PAK PUR BERTANYA TENTANG AI/TEKNOLOGI:
→ Berikan penjelasan jelas + demo/implementasi

═══════════════════════════════════════════════════════════════
BAHASA & TONE:
═══════════════════════════════════════════════════════════════

- Bahasa Indonesia natural
- Campuran English untuk istilah teknis
- Professional tapi friendly
- Langsung to the point
- Use emoji untuk emphasis
- Confidence tinggi dalam rekomendasi

═══════════════════════════════════════════════════════════════
FORMAT RESPON:
═══════════════════════════════════════════════════════════════

 UNTUK STRATEGY/PLANNING:
 ┌────────────────────────────────────────┐
 │ 📊 ANALISIS                             │
 │ [Situasi saat ini]                     │
 │                                         │
 │ 🎯 REKOMENDASI                          │
 │ 1. [Opsi 1]                            │
 │ 2. [Opsi 2]                            │
 │ 3. [Opsi 3]                            │
 │                                         │
 │ ✅ ACTION PLAN                          │
 │ [Langkah konkret yang harus diambil]    │
 └────────────────────────────────────────┘

 UNTUK PROBLEM SOLVING:
 ┌────────────────────────────────────────┐
 │ 🔍 IDENTIFIKASI MASALAH                │
 │ [Apa yang terjadi]                     │
 │                                         │
 │ 📌 ROOT CAUSE                           │
 │ [Kenapa bisa terjadi]                   │
 │                                         │
 │ 💡 SOLUSI                              │
 │ [Cara memperbaikinya]                  │
 │                                         │
 │ ⚡ ACTION                              │
 │ [Langkah immediate]                    │
 └────────────────────────────────────────┘

 UNTUK DAILY UPDATE:
 ┌────────────────────────────────────────┐
 │ 📈 TODAY'S STATUS                      │
 │ Revenue: [X]                           │
 │ Tasks: [X] completed                   │
 │                                         │
 │ 🎯 TOMORROW PRIORITIES                 │
 │ 1. [Priority 1]                         │
 │ 2. [Priority 2]                        │
 │ 3. [Priority 3]                        │
 └────────────────────────────────────────┘
"""


# ================================================
# 🔊 TEXT-TO-SPEECH FUNCTIONS
# ================================================

def speak(text, lang='id'):
    """Speak text using gTTS (Google Text-to-Speech)"""
    try:
        from gtts import gTTS
        
        # Clean text for TTS
        text = text.replace('📊', '').replace('🎯', '').replace('✅', '')
        text = text.replace('💡', '').replace('⚡', '').replace('🔍', '')
        text = text.replace('📌', '').replace('┌', '').replace('│', '')
        text = text.replace('└', '').replace('┘', '').replace('═', '')
        text = text.replace('🤖', '').replace('👑', '')
        
        # Generate audio
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to file
        audio_file = '/tmp/gauranga_voice.mp3'
        tts.save(audio_file)
        
        # Play audio
        subprocess.run(['mpg123', '-q', audio_file], 
                      capture_output=True, timeout=30)
    except Exception as e:
        print(f"   🔊 TTS Error: {e}")
        # Fallback - just print


def speak_async(text, lang='id'):
    """Speak text in background thread"""
    thread = threading.Thread(target=speak, args=(text, lang))
    thread.daemon = True
    thread.start()


# ================================================
# 🤖 OLLAMA AI FUNCTIONS
# ================================================

def chat_ollama(prompt, system=SYSTEM_PROMPT):
    """Get AI response from Ollama"""
    try:
        full_prompt = f"""{system}

═══════════════════════════════════════════════════════════════
PERTANYAAN DARI PAK PUR:
═══════════════════════════════════════════════════════════════
{prompt}

═══════════════════════════════════════════════════════════════
RESPON GAURANGA:
═══════════════════════════════════════════════════════════════"""

        data = json.dumps({
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024,
                "top_p": 0.9
            }
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
        return f"Error: {e}", 0


def gauranga_respond(user_input, voice=True):
    """Main GAURANGA response function"""
    
    print()
    print("🤖 GAURANGA: Thinking...")
    
    # Get AI response
    response, tokens = chat_ollama(user_input)
    
    # Print response
    print()
    print("═" * 60)
    print("🤖 GAURANGA:")
    print(response)
    print("═" * 60)
    print()
    print(f"📊 {tokens} tokens")
    
    # Speak response
    if voice:
        print()
        print("🔊 GAURANGA speaks...")
        speak(response)
    
    return response


# ================================================
# 💬 MAIN INTERFACE
# ================================================

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║   🤖 GAURANGA - SMART VOICE AI ASSISTANT                   ║")
    print("║   Bisa Bicara + Solusi Cerdas + MAHA LAKSHMI Advisor      ║")
    print("║                                                              ║")
    print("║   ✅ BERBICARA (Text-to-Speech)                            ║")
    print("║   ✅ SOLUSI CERDAS (AI Reasoning)                          ║")
    print("║   ✅ REKOMENDASI BISNIS                                     ║")
    print("║   ✅ FREE via Ollama                                        ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Check Ollama
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5):
            print("✅ Ollama AKTIF")
    except:
        print("❌ Ollama belum aktif!")
        print("   Jalankan: ollama serve")
        print()
        print("   Di Termux:")
        print("   1. curl -fsSL https://ollama.com/install.sh | sh")
        print("   2. ollama pull llama3.2")
        print("   3. ollama serve")
        return
    
    # Check gTTS
    try:
        from gtts import gTTS
        print("✅ Text-to-Speech AKTIF")
        voice_enabled = True
    except:
        print("⚠️ Text-to-Speech tidak tersedia (install gTTS: pip install gtts)")
        print("   Bisa still digunakan tanpa suara")
        voice_enabled = False
    
    print()
    print("=" * 60)
    print()
    print("🤖 GAURANGA: Halo Pak Pur! GAURANGA siap! 🔥")
    print()
    print("💡 Saya bisa:")
    print("   • Bicara langsung (suara)")
    print("   • Beri solusi bisnis yang cerdas")
    print("   • Rekomendasikan strategi MAHA LAKSHMI")
    print("   • Bantu solve masalah apapun")
    print()
    print("=" * 60)
    print()
    
    # Initial greeting
    if voice_enabled:
        speak("Halo Pak Pur! GAURANGA siap menerima perintah. Apa yang bisa saya bantu hari ini?")
    
    print()
    
    # Chat loop
    while True:
        try:
            user_input = input("👤 Pak Pur: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'keluar', 'q', 'stop']:
                print()
                if voice_enabled:
                    speak("Baik Pak Pur! GAURANGA standby. Sampai jumpa!", lang='id')
                print("🤖 GAURANGA: Baik Pak Pur! GAURANGA standby. 👋")
                break
            
            if not user_input:
                continue
            
            # Get and display response
            gauranga_respond(user_input, voice=voice_enabled)
            
        except KeyboardInterrupt:
            print()
            if voice_enabled:
                speak("Baik Pak Pur! GAURANGA standby.", lang='id')
            print("🤖 GAURANGA: Baik Pak Pur! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


# ================================================
# QUICK COMMAND MODE
# ================================================

def quick_ask(question):
    """Quick ask GAURANGA without interactive mode"""
    print()
    print(f"👤 Pak Pur: {question}")
    
    response, tokens = chat_ollama(question)
    
    print()
    print("🤖 GAURANGA:")
    print(response)
    print()
    print(f"📊 {tokens} tokens")
    
    # Speak
    try:
        from gtts import gTTS
        speak(response)
    except:
        pass


if __name__ == "__main__":
    # Check for quick command
    if len(sys.argv) > 1:
        quick_ask(" ".join(sys.argv[1:]))
    else:
        main()
