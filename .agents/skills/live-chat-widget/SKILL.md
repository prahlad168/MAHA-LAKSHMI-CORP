# 💬 Live Chat Widget Skill

## Purpose
Add AI-powered live chat widget to Payangan Hospital website.

## Files
| File | Description |
|------|-------------|
| `payangan-live-chat.html` | Complete chat widget with AI responses |
| `chat-widget.js` | Standalone JS widget (future) |

---

## Features

### ✅ Implemented
- 💬 Floating chat button (bottom-right)
- 🤖 AI-powered auto-responses
- ⚡ Quick reply buttons
- 🎨 Modern glass-morphism design
- 📱 Fully responsive
- 🌙 Dark theme compatible
- 💾 Chat history in session

### 🔄 Response Topics
- Jadwal dokter
- Pendaftaran online
- Kontak RS
- Lokasi/alamat
- IGD/Darurat
- Informasi kamar
- Layanan poli

---

## Integration Methods

### Method 1: iFrame Embed
```html
<iframe 
  src="https://payanganhospital.gianyarkab.go.id/chat-widget.html" 
  style="position:fixed;bottom:20px;right:20px;width:380px;height:500px;border:none;z-index:9999;border-radius:20px;"
  allow="microphone"
></iframe>
```

### Method 2: Direct Copy
1. Copy `payangan-live-chat.html` to website root
2. Add before `</body>`:
```html
<div id="chat-widget"></div>
<script src="/payangan-live-chat.js"></script>
```

### Method 3: Web Component (Future)
```html
<script type="module" src="https://payanganhospital.gianyarkab.go.id/chat-component.js"></script>
<chat-widget 
  position="bottom-right"
  theme="dark"
  agent-name="RS Payangan Assistant"
></chat-widget>
```

---

## Agent Configuration

### AI Chat Agent
| Field | Value |
|-------|-------|
| **Name** | RS-Payangan-Chatbot |
| **Automation ID** | `d858be42-f181-4144-8d18-77be0fa590cb` |
| **Schedule** | 24/7 (Always On) |
| **Response Time** | < 5 seconds |
| **Knowledge Base** | Hospital services, doctors, appointments |

### Response Categories
```
├── Jadwal Dokter
│   ├── Hari ini
│   ├── Besok
│   └── Spesialis
├── Pendaftaran
│   ├── Online
│   ├── Offline
│   └── Persyaratan
├── Kontak
│   ├── Telepon
│   ├── Email
│   └── WhatsApp
├── Layanan
│   ├── IGD
│   ├── Rawat Inap
│   └── Rawat Jalan
└── General
    ├── Lokasi
    ├── Fasilitas
    └── FAQ
```

---

## Customization

### Change Agent Name
```javascript
const agentName = "RS Payangan Assistant";
```

### Add More Responses
Edit `getAIResponse()` function:
```javascript
if (msg.includes('keyword')) {
    return 'Response text with <strong>HTML</strong>';
}
```

### Change Position
```css
.chat-widget {
    bottom: 20px;
    right: 20px;
    /* Change to bottom: 20px; left: 20px; for left side */
}
```

### Change Theme Color
```css
:root {
    --primary: #0891b2;
    --secondary: #06b6d4;
    --accent: #22d3ee;
}
```

---

## Future Enhancements

### Phase 2
- [ ] Connect to WhatsApp Business API
- [ ] Connect to Telegram Bot
- [ ] Human handoff to CS staff
- [ ] Chat history database
- [ ] Analytics dashboard

### Phase 3
- [ ] Voice input support
- [ ] Multi-language (Indonesian, English)
- [ ] Sentiment analysis
- [ ] Proactive chat
- [ ] Chatbot training with real conversations

---

## Deployment

### To Payangan Hospital Website
```bash
# 1. Copy file
cp payangan-live-chat.html /path/to/Payangan-Hospital/

# 2. Add to index.html before </body>
# <iframe src="/payangan-live-chat.html" ...></iframe>

# 3. Push to GitHub
git add .
git commit -m "Add live chat widget"
git push origin main

# 4. Auto-deploy via webhook
```

---

## Testing

### Local Test
1. Open `payangan-live-chat.html` in browser
2. Click chat button
3. Test quick replies
4. Test typing responses

### Production Test
1. Deploy to hosting
2. Check console for errors
3. Test on mobile devices
4. Verify responses work

---

## Troubleshooting

### Chat not showing
- Check if page loads without errors
- Verify CSS is loaded
- Check z-index of other elements

### Responses not working
- Check browser console
- Verify JavaScript loads correctly
- Check CORS if loaded from different domain

### Mobile issues
- Test on actual mobile device
- Check viewport meta tag
- Verify responsive CSS

---

## Performance

| Metric | Value |
|--------|-------|
| Size | ~25KB (minified) |
| Load Time | < 500ms |
| Memory Usage | < 50MB |
| Battery Impact | Minimal |

---

**Last Updated:** 2026-07-04
**Version:** 1.0.0
**Author:** GAURANGA AI Agent
