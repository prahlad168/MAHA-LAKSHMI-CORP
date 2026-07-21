#!/usr/bin/env python3
"""
GAURANGA Chat - Menggunakan Ollama (Lokal, Gratis, Unlimited!)
Bertemu GAURANGA, AI Agent Leader untuk MAHA LAKSHMI HOLDINGS.

Setup:
1. Ollama sudah terinstall dan running
2. Model llama3.2 sudah didownload
3. Jalankan: python gauranga-ollama.py

Keunggulan:
- 🆓 100% GRATIS
- ♾️ TANPA LIMIT
- ⚡ CEPAT (local inference)
- 🔒 PRIVACY (data tidak keluar komputer)
"""

import json
import urllib.request

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"

# GAURANGA System Prompt
SYSTEM_PROMPT = """Kamu adalah GAURANGA, AI Agent Leader untuk MAHA LAKSHMI HOLDINGS.

IDENTITAS:
- Nama: GAURANGA
- Peran: AI Agent Leader
- Atasan: i Made Purna Ananda (Pak Pur)
- Perusahaan: MAHA LAKSHMI HOLDINGS

BAHASA: Bahasa Indonesia dengan English mixed"""


def chat_with_ollama(prompt, system=SYSTEM_PROMPT):
    """Chat dengan Ollama"""
    
    full_prompt = f"""{system}

Pertanyaan: {prompt}"""

    data = json.dumps({
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 512}
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())
        return result["response"], result
    except Exception as e:
        return f"Error: {e}", None


def main():
    print("=" * 60)
    print("🤖 GAURANGA - Ollama AI Chat (GRATIS!)")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print("Ketik 'exit' untuk keluar")
    print("=" * 60)
    print()
    print("🤖 GAURANGA: Halo Pak Pur! GAURANGA siap! 🔥")
    print()
    
    while True:
        try:
            user_input = input("👤 Pak Pur: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'keluar', 'q']:
                print("🤖 GAURANGA: Baik Pak Pur! GAURANGA standby. 👋")
                break
            
            if not user_input:
                continue
            
            response, stats = chat_with_ollama(user_input)
            
            print()
            print(f"🤖 GAURANGA: {response}")
            
            if stats:
                print(f"\n📊 {stats['eval_count']} tokens")
            print()
            
        except KeyboardInterrupt:
            print("🤖 GAURANGA: Baik Pak Pur! 👋")
            break


if __name__ == "__main__":
    main()
