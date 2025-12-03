# Instagram Automation - Node.js Edition

🚀 **Backend Node.js dengan Z.ai API Integration untuk Instagram Automation**

## 📋 Fitur

- ✅ **Z.ai API Integration** - Real AI content generation
- ✅ **URL-based Content Extraction** - Generate dari berita spesifik
- ✅ **Instagram Caption Generation** - GLM-4.6 powered
- ✅ **Image Generation** - CogView-4 untuk Instagram visuals
- ✅ **Simple Web Interface** - HTML + JavaScript frontend
- ✅ **RESTful API** - Endpoint lengkap untuk automation
- ✅ **File Storage** - Save hasil generate ke JSON
- ✅ **History Tracking** - Tracking semua generated content

## 🛠️ Tech Stack

**Backend:**
- Node.js dengan Express.js
- Z.ai API Integration (GLM-4.6 + CogView-4)
- Web Reader untuk content extraction
- File system untuk storage
- CORS untuk frontend integration

**Frontend:**
- Vanilla HTML + CSS + JavaScript
- Responsive design
- Real-time API calls
- Modern UI/UX

**Deployment:**
- Railway (Node.js hosting)
- Atau Vercel (serverless functions)
- Atau DigitalOcean, AWS, dll

## 🚀 Quick Start

### 1. Setup Backend

```bash
# Navigate ke project
cd instagram_automation

# Install dependencies
cd backend
npm install

# Copy environment file
cp .env.example .env

# Edit .env dengan Z.ai API key
# ZAI_API_KEY=your_api_key_here
```

### 2. Jalankan Lokal

```bash
# Dalam folder backend
npm start

# Atau untuk development
npm run dev
```

**Akses di:** http://localhost:3000

### 3. Generate Instagram Content

1. **Setup API Key** - Masukkan Z.ai API key Anda
2. **Pilih Topic** - Pilih atau masukkan custom topic
3. **Masukkan URL Berita** - URL berita yang mau di-convert
4. **Generate Content** - Klik tombol untuk generate caption + image

## 📁 Struktur Project

```
instagram_automation/
├── backend/
│   ├── server.js              # Main Express server
│   ├── package.json           # Dependencies dan scripts
│   └── .env.example          # Environment template
├── frontend.html             # HTML interface (bisa di-buka langsung)
├── index.html               # Original HTML interface
├── Procfile                 # Railway deployment config
└── README-NODEJS.md         # Documentation ini
```

## 🔧 Konfigurasi

### Environment Variables (.env)

```bash
# Z.ai API Configuration (REQUIRED)
ZAI_API_KEY=your_zai_api_key_here

# Server Configuration
PORT=3000
NODE_ENV=production

# Optional untuk auto-posting ke Instagram
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id
INSTAGRAM_PAGE_ID=your_page_id
```

## 📱 API Endpoints

### Core Operations

| Method | Endpoint | Description |
|---------|-----------|-------------|
| POST | `/api/setup` | Validate Z.ai API key |
| POST | `/api/generate` | Generate content from URL |
| GET | `/api/topics` | Get available topics |
| GET | `/api/history` | Get generation history |

### API Response Format

```json
{
  "success": true,
  "content": {
    "topic": "teknologi",
    "originalUrl": "https://example.com/news",
    "newsSummary": "Summary dari berita...",
    "generatedCaption": "Caption untuk Instagram...",
    "generatedImageUrl": "https://z.ai/generated/image.jpg",
    "hashtags": ["#teknologi", "#inovasi", "#digital"],
    "createdAt": "2024-01-01T12:00:00.000Z"
  }
}
```

## 🚀 Deployment ke Railway

### 1. Persiapkan Repository

```bash
# Add semua file ke git
git add .

# Commit changes
git commit -m "Add Node.js backend for Instagram automation"

# Push ke GitHub
git push origin master
```

### 2. Deploy ke Railway

1. **Buka railway.app**
2. **Login dengan GitHub**
3. **Klik "New Project"**
4. **Pilih repository Anda**
5. **Settings Environment Variables:**
   - `ZAI_API_KEY`: Masukkan Z.ai API key Anda
   - `NODE_ENV`: `production`
6. **Deploy!** 🚀

### 3. Test Deployment

1. **Akses URL Railway** Anda (misal: `https://your-app.up.railway.app`)
2. **Test API Key Setup**
3. **Coba Generate Content**
4. **Check hasilnya!**

## 🔌 Alternative Deployment

### Vercel (Serverless)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### DigitalOcean App Platform

```bash
# Install doctl
npm i -g doctl

# Deploy
doctl apps create --spec .do/app.yaml
```

## 📊 Fitur Detail

### Z.ai API Integration

**GLM-4.6 untuk Text Generation:**
- News summary extraction
- Instagram caption generation
- Hashtag suggestions
- Call-to-action optimization

**CogView-4 untuk Image Generation:**
- Instagram-optimized visuals (1024x1024)
- Professional design
- Text overlay support
- High quality rendering

### Content Processing Workflow

1. **URL Content Extraction** - Z.ai Web Reader API
2. **AI News Summary** - GLM-4.6 processing
3. **Instagram Caption** - Optimized untuk engagement
4. **Image Generation** - CogView-4 dengan custom prompts
5. **Hashtag Extraction** - Auto-generate relevant hashtags
6. **File Storage** - Save hasil ke JSON files

### Supported Topics

- Teknologi, Bisnis, Kesehatan
- Olahraga, Hiburan, Politik
- Sains, Travel, Kuliner
- Fashion, Startup, AI, Cryptocurrency

## 🛠️ Customization

### Menambah Custom Topics

Edit `frontend.html` di bagian topic selection:

```javascript
const customTopics = [
    "your-custom-topic-1",
    "your-custom-topic-2",
    "your-custom-topic-3"
];
```

### Modifikasi Prompt Generation

Edit `server.js` di bagian prompt generation:

```javascript
const captionPrompt = `
// Custom prompt untuk caption generation
// Modify sesuai kebutuhan Anda
`;
```

### Image Customization

```javascript
const imagePrompt = `
// Custom prompt untuk image generation
// Modify style, colors, layout sesuai brand Anda
`;
```

## 📈 Monitoring & Analytics

### Generated Content Storage

- **Format:** JSON files
- **Location:** `backend/generated_content_*.json`
- **Structure:** Complete metadata untuk tracking

### Performance Metrics

- **Processing time:** Duration per generation
- **API usage:** Track Z.ai API calls
- **Success rate:** Monitor generation failures
- **Content quality:** Review generated outputs

## 🔒 Security Best Practices

### API Key Management

1. **Environment Variables** - Jangan hardcode API keys
2. **Server-side Only** - API keys tidak ter-expose ke frontend
3. **Rate Limiting** - Implement rate limiting untuk production
4. **Input Validation** - Validate semua user inputs

### Input Sanitization

```javascript
// Example input validation
if (!url || !isValidUrl(url)) {
    return res.status(400).json({ success: false, error: 'Invalid URL' });
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"ZAI_API_KEY not found"**
   - Check file `.env` sudah dibuat
   - Verify API key benar

2. **"Failed to extract content"**
   - URL mungkin tidak accessible
   - Coba dengan URL yang berbeda

3. **"Image generation failed"**
   - Check Z.ai API limits
   - Verify prompt tidak mengandung restricted content

4. **"Deployment failed"**
   - Verify `package.json` lengkap
   - Check `Procfile` untuk deployment
   - Environment variables sudah di-set

### Debug Mode

```bash
# Enable debug logging
NODE_ENV=development npm start

# Check server logs
tail -f logs/production.log
```

## 💡 Tips untuk Success

### Content Generation

- **Pilih URL berkualitas** - Berita yang lengkap dan aktual
- **Topic yang relevan** - Sesuai dengan target audience Anda
- **Test berbagai prompt** - Optimize untuk brand Anda
- **Review hasil AI** - Edit caption sebelum post

### Instagram Best Practices

- **Posting schedule** - 8AM, 12PM, 6PM, 8PM
- **Hashtag optimization** - 3-5 hashtags yang trending
- **Engagement** - Call-to-action untuk komentar/shares
- **Consistency** - Regular posting schedule

### Performance Optimization

- **Caching** - Cache frequently accessed data
- **Async processing** - Background jobs untuk heavy tasks
- **Error handling** - Graceful error recovery
- **Monitoring** - Track API usage and costs

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd instagram_automation

# Install dependencies
cd backend && npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

### Adding Features

1. **New API endpoints** - Tambah ke `server.js`
2. **Frontend components** - Modify `frontend.html`
3. **Database integration** - Replace file storage dengan DB
4. **Instagram auto-posting** - Integrasikan Instagram Graph API

## 📞 Support

### Documentation

- **Z.ai API Docs**: https://docs.z.ai
- **Node.js Docs**: https://nodejs.org/docs
- **Express.js**: https://expressjs.com/
- **Railway**: https://docs.railway.app/

### Help Resources

- **Check logs** untuk error details
- **Review API responses** untuk debugging
- **Monitor Railway dashboard** untuk deployment status
- **Test locally sebelum deploy**

---

## 🎉 Selamat!

Sekarang Anda punya **Instagram automation system dengan Node.js** yang:

✅ **Production-ready** - Siap deploy ke Railway
✅ **Real AI integration** - Bukan mock data
✅ **Simple & Effective** - Fokus ke core functionality
✅ **Scalable** - Mudah dikembangkan
✅ **Modern Tech Stack** - Node.js + Z.ai API

**Next Steps:**

1. **Deploy ke Railway** 🚀
2. **Test semua fitur** 🧪
3. **Optimize prompts** ⚙️
4. **Scale up** 📈

**Happy Instagramming!** 📸✨