# 🚀 Instagram Automation - Deployment Guide

**Production deployment dengan GitHub + Vercel + Supabase**

## 📋 Prerequisites

1. **GitHub Repository** - ✅ sudah setup: `https://github.com/aimastermebjm-byte/instagram-automation`

2. **Z.ai API Key** - Dapatkan dari https://z.ai

3. **Supabase Project** - Setup di https://supabase.com

4. **Vercel Account** - Connect dengan GitHub

## 🔧 Setup Database (Supabase)

### 1. Create Supabase Project
1. Buka [Supabase Dashboard](https://supabase.com/dashboard)
2. Klik "New Project"
3. Pilih organization, beri nama: `instagram-automation`
4. Set password dan region (pilih yang terdekat)
5. Wait hingga project selesai dibuat

### 2. Get Supabase Credentials
```bash
# Dapatkan dari Project Settings > API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

### 3. Create Database Tables
Copy SQL dari `database.py` atau jalankan:

```sql
-- Create tables
CREATE TABLE users (...);
CREATE TABLE jobs (...);
CREATE TABLE posts (...);
CREATE TABLE analytics (...);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ... (lainnya dari database.py)
```

### 4. Supabase SQL Editor
Buka Supabase > SQL Editor > New query, paste SQL dari `database.py`, lalu "Run".

## 🌐 Setup Vercel Deployment

### 1. Connect GitHub ke Vercel
1. Buka [Vercel Dashboard](https://vercel.com/dashboard)
2. Klik "Add New..." > "Project"
3. Import GitHub repository: `aimastermebjm-byte/instagram-automation`
4. Vercel akan otomatis detect Python/Flask

### 2. Configure Environment Variables
```bash
# Add di Vercel > Project Settings > Environment Variables

# Z.ai API
ZAI_API_KEY=your_zai_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Instagram (optional)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_id
INSTAGRAM_PAGE_ID=your_page_id

# Facebook (optional)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

### 3. Deploy!
Klik "Deploy" - Vercel akan otomatis build dan deploy.

## 🔗 GitHub Actions CI/CD

### 1. Setup Repository Secrets
Di GitHub repo > Settings > Secrets and variables > Actions:

```bash
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id
VERCEL_TOKEN=your_vercel_token

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key

SLACK_WEBHOOK_URL=your_slack_webhook (optional)
```

### 2. Deployment Workflow
- **Push to main** → Deploy to production
- **Pull request** → Deploy preview
- **Auto tests** → Code quality & security
- **Cleanup** → Remove old deployments

## 📱 PWA Configuration

### 1. Update Manifest
Edit `static/manifest.json`:
```json
{
  "name": "Instagram Automation",
  "short_name": "IG Automator",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F8F9FA",
  "theme_color": "#E4405F",
  "scope": "/",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

### 2. Service Worker
`static/sw.js` sudah setup untuk:
- Offline caching
- Background sync
- Push notifications

## 🌍 Custom Domain (Optional)

### 1. Add Custom Domain di Vercel
1. Vercel > Project Settings > Domains
2. Add custom domain: `yourdomain.com`
3. Update DNS records

### 2. Update Environment Variables
```bash
CORS_ORIGINS=https://yourdomain.com
SITE_URL=https://yourdomain.com
```

## 🔍 Monitoring & Analytics

### 1. Supabase Analytics
- Built-in dashboard
- Real-time data
- User behavior tracking

### 2. Vercel Analytics
- Performance metrics
- Error tracking
- Usage statistics

### 3. Google Analytics (Optional)
```bash
# Add GA tracking ID
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

## 🧪 Testing Production

### 1. Manual Testing
```bash
# Test API endpoints
curl https://your-app.vercel.app/api/topics

# Test database connection
curl https://your-app.vercel.app/api/test-connection

# Test job creation
curl -X POST https://your-app.vercel.app/api/start-job \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_test_key" \
  -d '{"topics": ["teknologi"], "options": {}}'
```

### 2. PWA Testing
- Open di mobile browser
- Test offline functionality
- Check install prompt
- Verify service worker

## 🔄 CI/CD Pipeline

### 1. Automated Deployment
```
Git Push → GitHub Actions → Tests → Deploy to Vercel
```

### 2. Branch Strategy
- `main` → Production
- `develop` → Staging
- `feature/*` → Preview

### 3. Rollback
```bash
# Rollback ke deployment sebelumnya
vercel rollback [deployment-url] --confirm
```

## 📊 Performance Optimization

### 1. Caching Strategy
```python
# In Flask app
@app.before_request
def before_request():
    # Cache static assets
    # Rate limiting
    # Compression
```

### 2. Database Optimization
- Supabase auto-indexing
- Connection pooling
- Query optimization

### 3. Asset Optimization
- Minified CSS/JS
- Image optimization
- CDN distribution

## 🛡️ Security

### 1. API Security
```python
# Rate limiting
@app.before_request
def rate_limit():
    # Implement rate limiting

# CORS
CORS(app, origins=[os.getenv("CORS_ORIGINS")])
```

### 2. Data Protection
- Environment variables
- Encrypted data storage
- RLS policies di Supabase

### 3. HTTPS
- Vercel auto-SSL
- Force HTTPS redirects
- Secure headers

## 📱 Mobile App Features

### 1. PWA Features
- Install to home screen
- Offline functionality
- Push notifications
- App-like experience

### 2. Mobile Optimization
- Responsive design
- Touch interactions
- Performance optimized
- Small bundle sizes

## 🎯 Production Checklist

- [ ] Supabase project created & tables setup
- [ ] Environment variables configured
- [ ] Vercel deployment successful
- [ ] GitHub Actions working
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active
- [ ] Monitoring enabled
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Mobile testing complete
- [ ] Backup strategy configured

## 🚀 Go Live!

Once semua setup complete:

1. **Production URL**: `https://your-app.vercel.app`
2. **Custom Domain**: `https://yourdomain.com` (if configured)
3. **PWA**: Install di mobile devices
4. **Monitoring**: Dashboard aktif
5. **CI/CD**: Auto-deployment enabled

**🎉 Your Instagram Automation Web App is now live!**

## 🆘 Troubleshooting

### Common Issues:
1. **Deployment failed** → Check environment variables
2. **Database connection** → Verify Supabase credentials
3. **API errors** → Check Z.ai API key and limits
4. **PWA not working** → Check service worker registration
5. **Mobile issues** → Test responsive design

### Debug Commands:
```bash
# Local testing
FLASK_ENV=development python app.py

# Check logs
vercel logs [deployment-url]

# Database test
python database.py
```

### Support:
- GitHub Issues
- Vercel Documentation
- Supabase Documentation
- Z.ai API Docs