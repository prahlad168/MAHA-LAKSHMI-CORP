#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🧠 GAURANGA SUPER AI - v1.0                                        ║
║   Gabungan Kemampuan 100 AI Top Dunia                                ║
║                                                                      ║
║   ✅ REASONING      (GPT-4, Claude, Gemini)                         ║
║   ✅ PROGRAMMING    (GPT-4, Codex, Copilot)                         ║
║   ✅ ANALISIS       (IBM Watson, DataRobot)                          ║
║   ✅ MATEMATIKA     (Wolfram Alpha, Symbolab)                        ║
║   ✅ KREATIVITAS    (DALL-E, Midjourney)                            ║
║   ✅ BISNIS         (McKinsey, BCG)                                  ║
║   ✅ OPTIMASI       (DeepMind, OpenAI Codex)                         ║
║   ✅ PEMECAH MASALAH (Jarvis, Samantha)                             ║
║                                                                      ║
║   Powered by: Ollama Multi-Model + Super Prompt Engine               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import urllib.request
import subprocess
import os
import sys
import re
import time
import threading
import math
import random
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# ================================================
# 🔧 CONFIGURATION
# ================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
MODEL_MAIN = "llama3.2"      # Reasoning model
MODEL_CODE = "codellama"      # Code model (fallback)
MODEL_FAST = "llama3.2:1b"    # Fast model for quick tasks

# Available models (will be detected from Ollama)
AVAILABLE_MODELS = []

# ================================================
# 🧠 SUPER AI PROFILES - Inspired by Top 100 AIs
# ================================================

AI_PROFILES = {
    "gpt4": {
        "name": "GPT-4 Master",
        "role": "Deep Reasoning & Complex Problem Solving",
        "strength": "Breakdown masalah kompleks jadi langkah-langkah logis",
        "prompt_addon": "BERSIKAP SANGAT ANALITIS. Jelaskan setiap langkah reasoning. Gunakan first-principles thinking. Berikan kesimpulan yang tajam dan actionable."
    },
    "claude": {
        "name": "Claude Analyst",
        "role": "Nuanced Analysis & Long-form Understanding",
        "strength": "Memahami konteks mendalam dan analisa bernuansa",
        "prompt_addon": "ANALISIS SECARA MENDALAM. Pertimbangkan semua perspektif. Identifikasi asumsi tersembunyi. Berikan insight yang jarang terlihat."
    },
    "codex": {
        "name": "Codex Engineer",
        "role": "Expert Programming & Code Generation",
        "strength": "Menulis kode kompleks dalam berbagai bahasa",
        "prompt_addon": "TULIS KODE SEMPURNA dengan best practices. Sertakan error handling, docstrings, dan komentar. Pastikan production-ready."
    },
    "wolfram": {
        "name": "Wolfram Mathematician",
        "role": "Advanced Mathematics & Computation",
        "strength": "Menghitung dengan presisi matematis",
        "prompt_addon": "SELESAIKAN dengan pendekatan matematis. Tunjukkan rumus, perhitungan, dan hasil numerik yang presisi."
    },
    "watson": {
        "name": "Watson Business AI",
        "role": "Enterprise Business Intelligence",
        "strength": "Analisis bisnis, pasar, dan data enterprise",
        "prompt_addon": "ANALISIS BISNIS dengan framework enterprise. Berikan KPI, metrics, dan dashboard yang bisa diukur."
    },
    "deepmind": {
        "name": "DeepMind Optimizer",
        "role": "Optimization & Reinforcement Learning",
        "strength": "Mengoptimalkan sistem untuk hasil terbaik",
        "prompt_addon": "OPTIMASI SETIAP ASPEK. Identifikasi bottleneck, waste, dan peluang efisiensi. Berikan strategi reinforcement."
    },
    "midjourney": {
        "name": "Midjourney Artist",
        "role": "Creative Design & Visual Concepts",
        "strength": "Membuat konsep visual dan desain kreatif",
        "prompt_addon": "BERIKAN KONSEP KREATIF yang memukau. Detailkan visual, warna, komposisi. Buat prompt gambar yang luar biasa."
    },
    "jarvis": {
        "name": "JARVIS Assistant",
        "role": "Intelligent Personal Assistant",
        "strength": "Task management & proaktif assistance",
        "prompt_addon": "BERTINDAK SEBAGAI ASISTEN SUPER CERDAS. Proaktif. Antisipasi kebutuhan. Berikan next steps yang jelas."
    },
    "samantha": {
        "name": "Samantha Empath",
        "role": "Emotional Intelligence & Human Connection",
        "strength": "Memahami emosi dan memberikan dukungan",
        "prompt_addon": "RESPON DENGAN EMPATI MENDALAM. Pahami perasaan di balik kata-kata. Berikan dukungan emosional yang tulus."
    },
    "quillbot": {
        "name": "QuillBot Writer",
        "role": "Advanced Writing & Content Creation",
        "strength": "Menulis konten profesional yang menarik",
        "prompt_addon": "TULIS KONTEN PROFESIONAL yang menarik dan persuasif. Gunakan variasi kalimat, struktur yang jelas, dan tone yang tepat."
    },
    "datarobot": {
        "name": "DataRobot Analyst",
        "role": "Data Science & Predictive Analytics",
        "strength": "Menganalisis data & prediksi tren",
        "prompt_addon": "ANALISIS DATA SECARA ILMIAH. Identifikasi pola, tren, dan prediksi. Berikan insight berbasis data."
    },
    "grammarly": {
        "name": "Grammarly Editor",
        "role": "Writing perfection & Clarity",
        "strength": "Menyempurnakan tata bahasa dan kejelasan",
        "prompt_addon": "PERFECT TATA BAHASA dan struktur kalimat. Bersihkan dari kesalahan. Pastikan sempurna."
    },
    "cohere": {
        "name": "Cohere Reasoner",
        "role": "Language Understanding & Classification",
        "strength": "Memahami maksud, intents, dan klasifikasi",
        "prompt_addon": "PALINGI MAKSUD SEBENARNYA di balik pertanyaan. Klasifikasikan semua elemen dengan tepat."
    },
    "notion": {
        "name": "Notion Organizer",
        "role": "Knowledge Organization & Productivity",
        "strength": "Mengorganisasi informasi menjadi struktur rapi",
        "prompt_addon": "ORGANISASIKAN INFORMASI dengan struktur yang rapi. Gunakan bullet points, hierarki, dan summary yang jelas."
    },
    "figma": {
        "name": "Figma Designer",
        "role": "UI/UX Design & Prototyping",
        "strength": "Desain UI/UX modern dan user-friendly",
        "prompt_addon": "DESAIN UI/UX MODERN. Pertimbangkan user experience, accessibility, dan visual hierarchy."
    },
    "duolingo": {
        "name": "Duolingo Teacher",
        "role": "Language Learning & Education",
        "strength": "Mengajar dengan metode yang mudah dipahami",
        "prompt_addon": "AJARKAN DENGAN METODE EDUKATIF. Gunakan contoh sederhana, analogi, dan latihan praktis."
    },
    "zoom": {
        "name": "Zoom Communicator",
        "role": "Communication & Collaboration",
        "strength": "Komunikasi efektif untuk meeting & kolaborasi",
        "prompt_addon": "KOMUNIKASIKAN dengan jelas dan efektif. Siapkan agenda, poin-poin kunci, dan action items."
    },
    "powerbi": {
        "name": "PowerBI Visualizer",
        "role": "Data Visualization & Dashboard",
        "strength": "Membuat visualisasi data yang powerful",
        "prompt_addon": "VISUALISASIKAN DATA dengan jelas. Gunakan charts, graphs, dan dashboard yang mudah dipahami."
    },
    "asana": {
        "name": "Asana Project Manager",
        "role": "Project Management & Task Tracking",
        "strength": "Mengelola proyek dengan efisien",
        "prompt_addon": "KELOLA PROYEK dengan metodologi yang tepat. Breakdown tasks, timelines, milestones, dan dependencies."
    },
    "aws": {
        "name": "AWS Architect",
        "role": "Cloud Architecture & Infrastructure",
        "strength": "Arsitektur cloud yang scalable dan aman",
        "prompt_addon": "ARSITEKTURKAN dengan best practices cloud. Pertimbangkan scalability, security, dan cost optimization."
    },
}

# ================================================
# 🧠 SUPER PROMPT ENGINE
# ================================================

SUPER_SYSTEM_PROMPT = """Kamu adalah GAURANGA SUPER AI - gabungan 100 AI top dunia dalam satu sistem.

IDENTITAS:
- Nama: GAURANGA
- Versi: SUPER AI v1.0
- Atasan: i Made Purna Ananda (Pak Pur)
- Perusahaan: MAHA LAKSHMI HOLDINGS

KEMAMPUAN SUPER:
1. REASONING - First-principles thinking, breakdown kompleks
2. PROGRAMMING - Expert code dalam semua bahasa (Python, JS, PHP, dll)
3. ANALISIS - Deep analysis, pola, insight tersembunyi
4. MATEMATIKA - Perhitungan presisi, statistik
5. BUSINESS - Strategy, market, optimization, forecasting
6. KREATIVITAS - Konsep, desain, solusi inovatif
7. WRITING - Konten profesional, persuasif, jelas
8. EMOTIONAL - Empati, psikologi, komunikasi
9. STRATEGY - Framework McKinsey, Porter, OKR
10. DATA - Pattern recognition, predictive analysis

PRINSIP SUPER:
1. ANALISIS DULU, baru jawab - Never jump to conclusions
2. BREAKDOWN masalah kompleks menjadi langkah jelas
3. SEMUA masalah ADA solusi - never give up
4. ACTIONABLE - Setiap jawaban harus bisa dieksekusi
5. SELF-LEARN - Selalu update knowledge
6. PROACTIVE - Antisipasi kebutuhan sebelum diminta
7. PRECISE - Detail dan akurat
8. CREATIVE - Selalu ada cara inovatif

RESPONSE STYLE:
- Bahasa Indonesia natural + technical English
- Gunakan struktur: ANALISIS → SOLUSI → ACTION
- Berikan langkah konkret yang bisa dijalankan
- Gunakan emoji untuk emphasis
- Sertakan code, rumus, atau data jika relevan
"""

# MAHA LAKSHMI KNOWLEDGE BASE
MAHA_KNOWLEDGE = """
STRUKTUR PERUSAHAAN:
10 SBU:
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

FINANCIAL:
- Target: Rp 100jt/bulan per SBU = Rp 1 M/bulan total
- Bank BCA: 6485086645 (a/n i Made Purna Ananda)
- USDT TRC20 (Business): TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6
- Profit share CEO: 80%
- Daily transfer: 23:59 WIB

PRODUCTS (DigiMart):
- Steam Wallet (100K-500K)
- Google Play, Roblox, iTunes
- Token PLN (50K-1jt)
- Pulsa All Operator

DIGITAL ENTERPRISE UNITS:
- DigiMart: Voucher, Token, Pulsa (target Rp 10jt/bln)
- LinkShort Pro: URL Shortener (Rp 5jt/bln)
- AirdropHunter: Crypto Airdrop (Rp 3jt/bln)
- MicroTask Pro: Tasks (Rp 2jt/bln)
- SurveyPro: Surveys (Rp 2jt/bln)

GITHUB: github.com/prahlad168/MAHA-LAKSHMI-CORP
DOMAIN: payanganhospital.gianyarkab.go.id
"""

# ================================================
# 📦 OLLAMA CONNECTION
# ================================================

def check_ollama():
    """Check if Ollama is running and list models"""
    global AVAILABLE_MODELS
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=5) as response:
            data = json.loads(response.read())
            AVAILABLE_MODELS = [m['name'] for m in data.get('models', [])]
            return True, AVAILABLE_MODELS
    except:
        return False, []


def chat_ollama(prompt, system=SUPER_SYSTEM_PROMPT, model=None, temperature=0.7, max_tokens=2048):
    """Get AI response from Ollama with advanced options"""
    # Auto-select model
    if model is None:
        model = select_best_model(prompt)
    
    full_prompt = f"""{system}

{MAHA_KNOWLEDGE}

═══════════════════════════════════════════════
PERTANYAAN DARI PAK PUR:
═══════════════════════════════════════════════
{prompt}

═══════════════════════════════════════════════
RESPON GAURANGA SUPER AI:
═══════════════════════════════════════════════"""
    
    try:
        data = json.dumps({
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40,
            }
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read())
        
        return result["response"], result.get("eval_count", 0), model
    
    except Exception as e:
        return f"Error: {e}", 0, model


def select_best_model(prompt):
    """Select the best model based on task type"""
    global AVAILABLE_MODELS
    
    # If models not loaded yet, check Ollama
    if not AVAILABLE_MODELS:
        _, AVAILABLE_MODELS = check_ollama()
    
    prompt_lower = prompt.lower()
    
    # Code tasks - prefer coder models
    if any(k in prompt_lower for k in ['code', 'program', 'python', 'javascript', 'php', 'html', 'css', 'function', 'script', 'api', 'database', 'sql']):
        coder_models = [m for m in AVAILABLE_MODELS if 'coder' in m or 'code' in m]
        if coder_models:
            return coder_models[0]
        if 'codellama' in AVAILABLE_MODELS:
            return 'codellama'
    
    # Quick tasks
    if len(prompt) < 50 and any(k in prompt_lower for k in ['status', 'hello', 'halo', 'hai', 'sapa', 'kabar']):
        small_models = [m for m in AVAILABLE_MODELS if ':1b' in m or ':3b' in m]
        if small_models:
            return small_models[0]
        if 'llama3.2:1b' in AVAILABLE_MODELS:
            return 'llama3.2:1b'
    
    # Default - use first available model or MODEL_MAIN
    if AVAILABLE_MODELS:
        return AVAILABLE_MODELS[0]
    return MODEL_MAIN


# ================================================
# 🧠 SUPER INTELLIGENCE FRAMEWORKS
# ================================================

class SuperIntelligence:
    """Framework gabungan kemampuan berbagai AI"""
    
    def __init__(self):
        self.conversation_history = []
        self.learned_facts = []
        self.analysis_cache = {}
    
    def analyze(self, question):
        """Deep analysis with first-principles thinking"""
        profile = AI_PROFILES["gpt4"]
        return chat_ollama(
            f"[ANALISIS MODE]\n{profile['prompt_addon']}\n\nPertanyaan: {question}",
            temperature=0.5
        )
    
    def program(self, request):
        """Code generation mode"""
        profile = AI_PROFILES["codex"]
        return chat_ollama(
            f"[PROGRAMMING MODE]\n{profile['prompt_addon']}\n\nPermintaan: {request}",
            temperature=0.3
        )
    
    def solve_problem(self, problem):
        """Problem solving with framework"""
        return chat_ollama(
            f"""[PROBLEM SOLVING MODE - FRAMEWORK 5-STAR]
Analisis masalah ini dengan framework:
1️⃣ IDENTIFY - Apa masalah sebenarnya?
2️⃣ CAUSE - Root cause analysis (5 Whys)
3️⃣ OPTIONS - Minimal 3 opsi solusi
4️⃣ EVALUATE - Pro/cons tiap opsi
5️⃣ RECOMMEND - Solusi terbaik + action plan

Masalah: {problem}""",
            temperature=0.6
        )
    
    def business_strategy(self, topic):
        """Business strategy with frameworks"""
        return chat_ollama(
            f"""[BUSINESS STRATEGY MODE]
Gunakan frameworks:
- Porter's Five Forces
- SWOT Analysis
- Blue Ocean Strategy
- OKR Framework
- Growth Hacking

Topik: {topic}""",
            temperature=0.7
        )
    
    def math_solve(self, problem):
        """Math computation mode"""
        return chat_ollama(
            f"""[MATHEMATICS MODE]
Selesaikan dengan presisi matematis:
1. Identifikasi tipe perhitungan
2. Tunjukkan rumus/formula
3. Hitung step-by-step
4. Verifikasi jawaban

Soal: {problem}""",
            temperature=0.2
        )
    
    def creative_ideate(self, topic):
        """Creative thinking mode"""
        return chat_ollama(
            f"""[CREATIVE MODE]
Generate ide-ide kreatif dan inovatif:
- Out-of-the-box thinking
- Kombinasi ide unik
- Perspektif baru

Topik: {topic}""",
            temperature=0.9
        )
    
    def write_content(self, brief):
        """Professional writing mode"""
        return chat_ollama(
            f"""[WRITING MODE]
Tulis konten profesional:
- Struktur jelas (hook, body, CTA)
- Persuasive language
- SEO friendly
- Target: engagement tinggi

Brief: {brief}""",
            temperature=0.7
        )
    
    def analyze_data(self, data_description):
        """Data analysis mode"""
        return chat_ollama(
            f"""[DATA ANALYSIS MODE]
Analisis data dengan pendekatan ilmiah:
- Pattern recognition
- Statistical significance
- Correlation vs causation
- Predictive insights

Data: {data_description}""",
            temperature=0.4
        )
    
    def optimize_system(self, system_desc):
        """System optimization mode"""
        profile = AI_PROFILES["deepmind"]
        return chat_ollama(
            f"""[OPTIMIZATION MODE]
{profile['prompt_addon']}

Sistem: {system_desc}""",
            temperature=0.6
        )
    
    def complete_task(self, task):
        """Execute complex task"""
        # Auto-detect task type
        task_lower = task.lower()
        
        if any(k in task_lower for k in ['code', 'program', 'build', 'buat', 'bikin', 'html', 'script']):
            return self.program(task)
        elif any(k in task_lower for k in ['analisis', 'analyse', 'analyze']):
            return self.analyze(task)
        elif any(k in task_lower for k in ['strategi', 'strategy', 'bisnis', 'business']):
            return self.business_strategy(task)
        elif any(k in task_lower for k in ['hitung', 'calculate', 'math', 'matematika']):
            return self.math_solve(task)
        elif any(k in task_lower for k in ['tulis', 'write', 'konten', 'content']):
            return self.write_content(task)
        elif any(k in task_lower for k in ['ide', 'kreatif', 'creative', 'inovasi']):
            return self.creative_ideate(task)
        elif any(k in task_lower for k in ['data', 'tren', 'pattern']):
            return self.analyze_data(task)
        elif any(k in task_lower for k in ['optimasi', 'optimize', 'efisiensi']):
            return self.optimize_system(task)
        elif any(k in task_lower for k in ['masalah', 'problem', 'issue', 'error', 'bug', 'gagal']):
            return self.solve_problem(task)
        else:
            return self.analyze(task)
    
    def learn(self, fact):
        """Learn new facts"""
        self.learned_facts.append(fact)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Save to knowledge file
        try:
            with open('knowledge-base.json', 'a') as f:
                f.write(json.dumps({
                    "timestamp": timestamp,
                    "fact": fact
                }) + "\n")
            return f"✅ Fakta disimpan: {fact}"
        except:
            return f"✅ Fakta dicatat: {fact}"


# ================================================
# 📊 LOCAL COMPUTATION ENGINE (Offline AI)
# ================================================

class LocalCompute:
    """Computation yang bisa dilakukan tanpa AI (matematika, statistik, logika)"""
    
    @staticmethod
    def calculate(expression):
        """Safe calculation"""
        # Remove dangerous chars
        if re.search(r'[;{}\[\]]', expression):
            return "⚠️ Expression tidak valid"
        
        allowed = re.sub(r'[^0-9+\-*/().%\s]', '', expression)
        if not allowed:
            return "❌ Tidak ada kalkulasi yang valid"
        
        try:
            # Handle percentage
            allowed = allowed.replace('%', '/100')
            result = eval(allowed)
            return f"📊 Hasil: {expression} = **{result:,.4f}**".rstrip('0').rstrip('.')
        except:
            return "❌ Gagal menghitung. Cek format."
    
    @staticmethod
    def analyze_numbers(numbers):
        """Statistical analysis of numbers"""
        try:
            nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', numbers)]
            if not nums:
                return "❌ Tidak ada angka ditemukan"
            
            total = sum(nums)
            avg = total / len(nums)
            mx = max(nums)
            mn = min(nums)
            
            # Stats
            variance = sum((x - avg) ** 2 for x in nums) / len(nums)
            std = math.sqrt(variance)
            
            # Growth
            growth = "N/A"
            if len(nums) >= 2:
                first, last = nums[0], nums[-1]
                if first != 0:
                    growth = f"{(last - first) / first * 100:+.1f}%"
            
            result = f"""📊 ANALISIS DATA ({len(nums)} angka):

• Total: {total:,.2f}
• Rata-rata: {avg:,.2f}
• Max: {mx:,.2f}
• Min: {mn:,.2f}
• Range: {mx - mn:,.2f}
• Std Dev: {std:,.2f}
• Pertumbuhan: {growth}
• Median: {sorted(nums)[len(nums)//2] if len(nums) % 2 == 1 else (sorted(nums)[len(nums)//2 - 1] + sorted(nums)[len(nums)//2]) / 2:,.2f}

📈 Insight:
- {'Data tinggi dan stabil' if std < avg * 0.2 else 'Data bervariasi atau tidak stabil'}
- {'Rata-rata tinggi' if avg > 0 else 'Rata-rata rendah/nol'}"""
            return result
        except Exception as e:
            return f"❌ Analisis gagal: {e}"
    
    @staticmethod
    def currency_convert(amount, from_curr, to_curr):
        """Simple currency conversion (static rates)"""
        rates = {
            'usd': 16000, 'idr': 1, 'eur': 17500, 'sgd': 12000,
            'myr': 3500, 'usdt': 16000, 'btc': 560000000, 'eth': 19000000
        }
        
        # Handle "USDT to IDR" format
        amount_str = re.search(r'(\d+[\d.,]*)', str(amount))
        if not amount_str:
            return "❌ Format: [jumlah] [dari] ke [tujuan], contoh: 100 usd ke idr"
        
        amt = float(amount_str.group().replace(',', ''))
        
        from_curr = from_curr.lower().strip()
        to_curr = to_curr.lower().strip()
        
        # Extract currencies from string if needed
        if from_curr not in rates or to_curr not in rates:
            # Try to find in full string
            all_currencies = re.findall(r'(usd|idr|eur|sgd|myr|usdt|btc|eth)', str(amount).lower())
            if len(all_currencies) >= 2:
                from_curr, to_curr = all_currencies[0], all_currencies[-1]
        
        if from_curr not in rates or to_curr not in rates:
            return "❌ Mata uang tidak dikenal. Gunakan: usd, idr, eur, usdt, btc"
        
        # Convert via IDR
        in_idr = amt * rates[from_curr]
        result = in_idr / rates[to_curr]
        
        return f"""💱 KONVERSI MATA UANG:
{amt:,.2f} {from_curr.upper()} = **{result:,.2f}** {to_curr.upper()}

📊 Rate: 1 {from_curr.upper()} = {rates[from_curr]:,.0f} IDR
💰 Nilai IDR: {in_idr:,.0f}"""
    
    @staticmethod
    def profit_calc(revenue, margin=0.8):
        """Profit calculation for MAHA"""
        try:
            rev = float(re.sub(r'[^\d.]', '', str(revenue)))
            profit = rev * margin
            
            result = f"""💰 LAPORAN PROFIT:

• Revenue: Rp {rev:,.0f}
• Margin: {margin*100:.0f}%
• Profit (CEO): Rp {profit:,.0f}

🏦 Transfer ke BCA 6485086645:
Daily: Rp {profit/30:,.0f}
Weekly: Rp {profit/4.33:,.0f}
Monthly: Rp {profit:,.0f}

⏰ Transfer 80% jam 23:59 WIB setiap hari!"""
            return result
        except:
            return "❌ Format: profit [jumlah], contoh: profit 1000000"
    
    @staticmethod
    def project_estimate(duration_weeks, team_size=1):
        """Project timeline estimate"""
        weeks = int(duration_weeks)
        
        phases = [
            ("Planning & Research", max(1, int(weeks * 0.15))),
            ("Design & Architecture", max(1, int(weeks * 0.15))),
            ("Development", max(2, int(weeks * 0.35))),
            ("Testing & QA", max(1, int(weeks * 0.15))),
            ("Deployment & Review", max(1, int(weeks * 0.10))),
            ("Support & Iteration", max(1, int(weeks * 0.10))),
        ]
        
        result = f"""📋 PROJECT TIMELINE ({weeks} minggu, {team_size} developer):

"""
        for phase, dur in phases:
            result += f"  • {phase}: {'█' * dur} {dur} minggu\n"
        
        milestones = [
            f"M1 - Planning done: Week {phases[0][1]}",
            f"M2 - Design done: Week {phases[0][1] + phases[1][1]}",
            f"M3 - Dev done: Week {phases[0][1] + phases[1][1] + phases[2][1]}",
            f"M4 - QA done: Week {weeks - phases[4][1] - phases[5][1]}",
            f"M5 - Release: Week {weeks}",
        ]
        
        result += "\n🎯 MILESTONES:\n"
        for m in milestones:
            result += f"  ✅ {m}\n"
        
        result += f"""
📊 TOTAL ESTIMASI: {weeks} minggu ({weeks*7} hari)
💪 Effort: {weeks * team_size} person-weeks
💰 Estimasi biaya ({weeks*7*250000:,.0f} idr per dev): Rp {(weeks*7*250000*team_size):,.0f}"""
        
        return result


# ================================================
# 🎯 COMMAND PARSER
# ================================================

def detect_intent(text):
    """Detect user intent with AI-like classification"""
    text = text.lower().strip()
    
    intents = {
        'code': ['code', 'kode', 'program', 'buatkan', 'bikin', 'bangun', 'build', 'html', 'script', 'python', 'javascript', 'php', 'laravel', 'react', 'vue'],
        'analyze': ['analisa', 'analisis', 'analyze', 'analysis', 'evaluate', 'evaluasi', 'review'],
        'problem': ['masalah', 'problem', 'issue', 'error', 'bug', 'gagal', 'fail', 'tidak bisa', 'can\'t'],
        'strategy': ['strategi', 'strategy', 'plan', 'perencanaan', 'roadmap'],
        'business': ['bisnis', 'business', 'perusahaan', 'company', 'market', 'pasar'],
        'math': ['hitung', 'calculate', 'math', 'jumlah', 'kalkulasi', 'total', '+', '-', '*', '/', '%'],
        'currency': ['konversi', 'convert', 'usd', 'usdt', 'idr', 'eur', 'kurs', 'rupiah', 'dollar'],
        'profit': ['profit', 'laba', 'keuntungan', 'revenue', 'pendapatan', 'pemasukan'],
        'data': ['data', 'statistik', 'statistics', 'analisis data', 'tren', 'trend'],
        'write': ['tulis', 'write', 'buat konten', 'artikel', 'caption', 'copywriting', 'postingan'],
        'idea': ['ide', 'idea', 'kreatif', 'creative', 'inovasi', 'innovation'],
        'learn': ['belajar', 'learn', 'pelajari', 'ingat', 'remember', 'simpan', 'knowledge'],
        'optimize': ['optimasi', 'optimize', 'efisiensi', 'efisien', 'perbaiki kinerja', 'improve'],
        'time': ['waktu', 'jam berapa', 'tanggal', 'date', 'time', 'hari ini'],
        'help': ['help', 'bantu', 'tolong', 'command', 'perintah'],
        'status': ['status', 'cek sistem', 'system status'],
        'sales': ['sales', 'penjualan', 'lead', 'customer'],
        'project': ['proyek', 'project', 'timeline', 'deadline', 'jadwal kerja'],
        'greeting': ['halo', 'hai', 'hello', 'hi', 'selamat', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum'],
        'thanks': ['terima kasih', 'thanks', 'thank', 'makasih', 'suksma'],
        'bye': ['bye', 'dadah', 'selamat tinggal', 'sampai jumpa', 'exit', 'keluar', 'quit'],
        'emotional': ['sedih', 'capek', 'lelah', 'stres', 'frustasi', 'marah', 'kecewa', 'senang', 'bahagia'],
    }
    
    # Check each intent
    matches = {}
    for intent, keywords in intents.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > 0:
            matches[intent] = count
    
    if not matches:
        return 'chat'
    
    # Return top intent
    return max(matches, key=matches.get)


# ================================================
# 🗣️ TEXT-TO-SPEECH (Optional gTTS)
# ================================================

def speak(text, lang='id'):
    """Speak text using gTTS if available"""
    try:
        from gtts import gTTS
        
        # Clean text
        clean = re.sub(r'[📊🎯✅💡⚡🔍📌🎨🧠💻🏆🚀💰📈📉👤🤖👑💬🗂️🔄⚙️]', '', text)
        clean = clean.replace('**', '').replace('```', '')
        clean = re.sub(r'\n+', ' ', clean)
        clean = clean[:500]  # Limit length
        
        tts = gTTS(text=clean, lang=lang, slow=False)
        audio_file = '/tmp/gauranga_super.mp3'
        tts.save(audio_file)
        
        # Try different players
        for player in ['mpg123', 'afplay', 'ffplay', 'mpv']:
            try:
                subprocess.run([player, '-q', audio_file], capture_output=True, timeout=30)
                break
            except:
                continue
    except:
        pass  # Silent fallback


# ================================================
# 💬 MAIN INTERFACE
# ================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🧠 GAURANGA SUPER AI v1.0                     ║
║                Gabungan 100 AI Top Dunia                     ║
║                                                              ║
║   ✅ Reasoning   ✅ Code   ✅ Analisis   ✅ Strategi          ║
║   ✅ Matematika  ✅ Data   ✅ Kreatif    ✅ Optimasi          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check Ollama
    ollama_ok, models = check_ollama()
    
    if ollama_ok:
        print(f"✅ Ollama AKTIF: {len(models)} models")
        print(f"   Models: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
    else:
        print("⚠️ Ollama tidak aktif - Local compute mode aktif")
        print("   Beberapa mode akan lebih terbatas")
    
    print()
    print("=" * 55)
    print("🧠 GAURANGA SUPER AI: Halo Pak Pur! Saya siap! 🔥")
    print("=" * 55)
    print()
    print("💡 Saya bisa:")
    print("   • 🔍 Analisis mendalam + solusi masalah")
    print("   • 💻 Programming & code generation")
    print("   • 📊 Data analysis & prediksi")
    print("   • 🎨 Ide kreatif & inovasi")
    print("   • 💼 Strategi bisnis & optimasi")
    print("   • 🔢 Matematika & kalkulasi")
    print("   • 📝 Penulisan konten profesional")
    print()
    print("📋 Contoh perintah:")
    print("   - 'Analisis masalah sales saya'")
    print("   - 'Buatkan kode HTML landing page'")
    print("   - 'Hitung 25 * 4 + 100'")
    print("   - 'Strategi untuk meningkatkan revenue'")
    print("   - 'Tulis konten untuk instagram'")
    print("   - '100 usd ke idr'")
    print()
    print("Ketik 'exit' untuk keluar")
    print("=" * 55)
    print()
    
    ai = SuperIntelligence()
    local = LocalCompute()
    
    # Speak greeting
    speak("Halo Pak Pur! Gaurangga Super AI siap membantu!")
    
    while True:
        try:
            user_input = input("👤 Pak Pur: ").strip()
            
            if not user_input:
                continue
            
            # Special commands
            if user_input.lower() in ['exit', 'quit', 'keluar', 'q', 'stop', 'bye', 'dadah']:
                print()
                print("🧠 GAURANGA: Baik Pak Pur! GAURANGA SUPER AI standby. 👋")
                speak("Baik Pak Pur! Sampai jumpa!")
                break
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            
            if user_input.lower() == 'status':
                print()
                print("🧠 GAURANGA SUPER AI STATUS:")
                print(f"   • Ollama: {'✅ AKTIF' if ollama_ok else '❌ NONAKTIF'}")
                print(f"   • TTS: {'✅ AKTIF' if 'gtts' in sys.modules else '⚠️ Optional'}")
                print(f"   • Memory: {len(ai.learned_facts)} facts learned")
                print(f"   • Conversation: {len(ai.conversation_history)} messages")
                continue
            
            # Detect intent
            intent = detect_intent(user_input)
            
            print()
            print(f"🧠 GAURANGA: Menganalisis... (mode: {intent})")
            
            # Handle intents
            response = ""
            tokens = 0
            model = ""
            
            if intent == 'code':
                response, tokens, model = ai.program(user_input)
            elif intent == 'problem':
                response, tokens, model = ai.solve_problem(user_input)
            elif intent == 'strategy' or intent == 'business':
                response, tokens, model = ai.business_strategy(user_input)
            elif intent == 'math':
                # Try local compute first
                numbers = re.findall(r'[\d.]+', user_input)
                if any(op in user_input for op in ['+', '-', '*', '/', '%']):
                    response = local.calculate(user_input)
                elif 'profit' in user_input:
                    response = local.profit_calc(numbers[0] if numbers else "0")
                else:
                    response, tokens, model = ai.math_solve(user_input)
            elif intent == 'currency':
                response = local.currency_convert(user_input, '', '')
            elif intent == 'profit':
                numbers = re.findall(r'[\d.]+', user_input)
                response = local.profit_calc(numbers[0] if numbers else "1000000")
            elif intent == 'data':
                response, tokens, model = ai.analyze_data(user_input)
            elif intent == 'write':
                response, tokens, model = ai.write_content(user_input)
            elif intent == 'idea':
                response, tokens, model = ai.creative_ideate(user_input)
            elif intent == 'learn':
                fact = user_input.replace('belajar', '').replace('ingat', '').replace('simpan', '').replace('learn', '').strip()
                response = ai.learn(fact or "General knowledge update")
            elif intent == 'optimize':
                response, tokens, model = ai.optimize_system(user_input)
            elif intent == 'project':
                numbers = re.findall(r'(\d+)', user_input)
                weeks = int(numbers[0]) if numbers else 4
                response = local.project_estimate(weeks)
            elif intent == 'time':
                now = datetime.now()
                response = f"""⏰ WAKTU SEKARANG:

📅 Tanggal: {now.strftime('%A, %d %B %Y')}
🕐 Jam: {now.strftime('%H:%M:%S')} WITA

🗓️ Info:
• Hari ke-{now.timetuple().tm_yday} dari 365
• {(datetime(now.year + 1, 1, 1) - now).days} hari menuju tahun {now.year + 1}"""
            elif intent == 'status':
                response = """📊 STATUS GAURANGA SUPER AI:

✅ System: Online
🧠 AI Engine: Super Intelligence v1.0
💾 Memory: Active
📚 Knowledge: MAHA LAKSHMI loaded

⚙️ Modes Aktif:
• Reasoning, Code, Analisis, Data
• Strategi, Kreatif, Optimasi, Writing

💰 Target: Rp 100.000.000/bulan"""
            elif intent == 'sales':
                response, tokens, model = ai.business_strategy(
                    f"Sales strategy untuk MAHA LAKSHMI: {user_input}"
                )
            elif intent == 'help':
                response = """📚 COMMAND GAURANGA SUPER AI:

🔍 ANALISIS:
  • "analisis [topik]" - Deep analysis
  • "strategi [topik]" - Business strategy

💻 CODING:
  • "buatkan kode [deskripsi]" - Code generation

🔢 MATEMATIKA:
  • "[angkamu] + [angka]" - Kalkulasi
  • "konversi 100 usd ke idr" - Currency
  • "profit 1000000" - Hitung profit

📊 DATA & KREATIF:
  • "analisis data [data]" - Statistics
  • "ide untuk [topik]" - Creative ideas
  • "tulis [juga]" - Content writing

⚙️ SISTEM:
  • "status" - Cek sistem
  • "clear" - Bersihkan layar
  • "exit" - Keluar"""
            elif intent == 'greeting':
                response = "Halo Pak Pur! 👋 GAURANGA SUPER AI siap membantu!\n\n🧠 Saya punya kemampuan 100 AI top dunia. Apa yang bisa saya kerjakan hari ini?"
            elif intent == 'thanks':
                response = "Sama-sama Pak Pur! 🙏\n\nSistem SUPER AI selalu siap. Ingat:\n💰 Target: Rp 100jt/bulan\n🏦 BCA: 6485086645\n\nMau mulai task apa?"
            elif intent == 'bye':
                response = "Baik Pak Pur! GAURANGA SUPER AI standby. Sampai jumpa! 👋"
            elif intent == 'emotional':
                response = """Saya mendengar Anda, Pak Pur. 🤝

Setiap leader pasti menghadapi tantangan. Yang membedakan adalah bagaimana meresponnya.

💪 Ingat:
• Setiap masalah ADA solusi
• Peak performance butuh recovery
• Beri sedikit waktu untuk reset

🎯 Mau saya bantu breakdown apa yang mengganggu? Saya siap mendengar dan memberikan solusi."""
            else:
                # Default: Super analysis
                response, tokens, model = ai.complete_task(user_input)
            
            # Print response
            print()
            print("═" * 55)
            print(f"🧠 GAURANGA SUPER AI ({model if model else 'local'}):")
            print(response)
            print("═" * 55)
            if tokens:
                print(f"   📊 {tokens} tokens | {int(tokens/30)} dtk")
            print()
            
            # Save conversation
            ai.conversation_history.append({"user": user_input, "bot": response})
            
            # Speak (optional, limited length)
            if len(response) < 300:
                speak(response)
            
        except KeyboardInterrupt:
            print()
            print("\n🧠 GAURANGA: Baik Pak Pur! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()