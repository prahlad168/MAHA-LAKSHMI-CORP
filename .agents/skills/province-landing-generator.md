# 🏪 Province Landing Page Generator Skill

## Purpose
Generate landing pages for all 38 Indonesian provinces × 5 business units = 190 pages

## Usage
```bash
python3 generate-province.py
```

## Configuration

### Provinces (38)
```python
PROVINCES = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi",
    "Sumatera Selatan", "Bengkulu", "Lampung", "DKI Jakarta", "Jawa Barat",
    "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten", "Bali",
    "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat",
    "Kalimantan Tengah", "Kalimantan Selatan", "Kalimantan Timur",
    "Kalimantan Utara", "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan",
    "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat", "Maluku", "Maluku Utara",
    "Papua", "Papua Barat", "Papua Tengah", "Papua Pegunungan", "Papua Barat Daya",
    "Papua Selatan", "Papua Jaya Wijaya"
]
```

### Business Units (5)
1. **DigiMart** - Voucher, Token, Pulsa
2. **LinkShort Pro** - URL Shortener
3. **AirdropHunter** - Crypto Airdrop
4. **MicroTask Pro** - Micro Tasks
5. **SurveyPro** - Surveys

## Output Structure
```
province-pages/
├── digimart/
│   ├── aceh.html
│   ├── sumut.html
│   └── ... (38 files)
├── linkshort/
├── airdrop/
├── microtask/
└── survey/
```

## Features
- 10 Bahasa support
- Mobile responsive
- Region categorization
- Contact info per province
- Payment methods (BCA 6485086645)
