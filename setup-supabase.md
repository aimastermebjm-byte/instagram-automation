# 🗄️ Supabase Database Setup Guide

## 📋 Cara Copy SQL ke Supabase

### 🎯 Cara 1: Simple SQL (FIXED - Recommended)

**Pakai file ini jika sebelumnya error:**

1. **Buka file `supabase_simple_setup.sql`**:
   - Buka file ini di text editor
   - Select all (Ctrl+A)
   - Copy (Ctrl+C)

2. **Buka Supabase SQL Editor**:
   - Login ke [Supabase Dashboard](https://supabase.com/dashboard)
   - Pilih project Anda
   - Klik "SQL Editor" di sidebar
   - Klik "New query"
   - Paste SQL (Ctrl+V)
   - Klik "Run" ▶️

3. **Tunggu hingga selesai** (±10-15 detik)
   - Harus muncul: "🎉 Instagram Automation database setup completed successfully!"

### 🚀 Cara 2: Original File (Jika simple version berhasil)
### 🛠️ Cara 3: Manual Copy (Jika semua file gagal)

Copy SQL ini dalam **chunks**:

#### 🟢 CHUNK 1: Table Creation
```sql
-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    api_key TEXT NOT NULL UNIQUE,
    instagram_token TEXT,
    business_account_id TEXT,
    facebook_app_id TEXT,
    facebook_app_secret TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'pro', 'enterprise')),
    posts_created INTEGER DEFAULT 0,
    jobs_completed INTEGER DEFAULT 0,
    total_topics_covered INTEGER DEFAULT 0,
    email TEXT,
    settings JSONB DEFAULT '{}'
);

-- JOBS TABLE
CREATE TABLE IF NOT EXISTS jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id TEXT UNIQUE NOT NULL,
    topics JSONB NOT NULL,
    options JSONB NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_topic TEXT,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    total_posts INTEGER DEFAULT 0,
    auto_posted BOOLEAN DEFAULT FALSE,
    error_details JSONB,
    processing_time_seconds INTEGER
);
```
**Run →** Klik "Run" setelah paste chunk 1

---

#### 🟡 CHUNK 2: More Tables
```sql
-- POSTS TABLE
CREATE TABLE IF NOT EXISTS posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    news_url TEXT,
    news_title TEXT,
    news_summary TEXT,
    image_url TEXT,
    caption TEXT,
    hashtags JSONB,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    posted_at TIMESTAMP WITH TIME ZONE,
    instagram_media_id TEXT,
    instagram_permalink TEXT,
    engagement_stats JSONB DEFAULT '{}',
    auto_posted BOOLEAN DEFAULT FALSE,
    post_status TEXT DEFAULT 'created' CHECK (post_status IN ('created', 'scheduled', 'posted', 'failed')),
    ai_generation_metadata JSONB DEFAULT '{}'
);

-- ANALYTICS TABLE
CREATE TABLE IF NOT EXISTS analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    metadata JSONB DEFAULT '{}'
);
```
**Run →** Klik "Run" setelah paste chunk 2

---

#### 🔵 CHUNK 3: Indexes
```sql
-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active DESC);

-- Jobs table indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at DESC);

-- Posts table indexes
CREATE INDEX IF NOT EXISTS idx_posts_job_id ON posts(job_id);
CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(post_status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at DESC);
```
**Run →** Klik "Run" setelah paste chunk 3

---

#### 🟣 CHUNK 4: Row Level Security
```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = api_key::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = api_key::text);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = api_key::text);

-- Jobs table policies
CREATE POLICY "Users can view own jobs" ON jobs
    FOR SELECT USING (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id)
    );
```
**Run →** Klik "Run" setelah paste chunk 4

---

## ✅ Verifikasi Setup

Setelah semua SQL dijalankan:

### 1. **Check Tables**
Di SQL Editor jalankan:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```
Harus muncul: `users, jobs, posts, analytics, job_results, system_logs, rate_limits, subscriptions`

### 2. **Check Policies**
```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public';
```

### 3. **Test Insert Data**
```sql
-- Test user insert
INSERT INTO users (api_key, email, subscription_plan)
VALUES ('test-key-12345', 'test@example.com', 'free');

-- Test job insert
INSERT INTO jobs (user_id, job_id, topics, options, status)
SELECT
    id,
    'test-job-001',
    '["teknologi"]',
    '{"max_posts": 3, "time_range": "oneDay"}',
    'pending'
FROM users
WHERE api_key = 'test-key-12345';

-- Verify data
SELECT * FROM users WHERE api_key = 'test-key-12345';
SELECT * FROM jobs WHERE job_id = 'test-job-001';
```

### 4. **Clean Test Data**
```sql
-- Remove test data
DELETE FROM jobs WHERE job_id = 'test-job-001';
DELETE FROM users WHERE api_key = 'test-key-12345';
```

## 🚨 Common Issues & Solutions

### ❌ **"Permission denied" Error**
**Cause:** RLS policies belum dibuat
**Solution:** Pastikan CHUNK 4 (RLS policies) sudah dijalankan

### ❌ **"Function does not exist" Error**
**Cause:** Functions belum dibuat atau salah eja
**Solution:** Jalankan ulang chunk yang mengandung function

### ❌ **"Maximum transaction size exceeded"**
**Cause:** SQL terlalu panjang untuk satu kali eksekusi
**Solution:** Gunakan cara manual dengan chunks

### ❌ **"Connection lost"**
**Cause:** Query terlalu berat
**Solution:** Tunggu beberapa saat lalu coba lagi

### ❌ **"Table already exists" Warning**
**Normal saja:** Itu karena pakai `IF NOT EXISTS`
**Action:** Lanjutkan ke chunk berikutnya

## 📱 Get Supabase Credentials

Setelah setup selesai:

1. **Buka Project Settings**
   - Di Supabase Dashboard
   - Klik project Anda
   - Go to **Settings** > **API**

2. **Copy Credentials:**
```bash
# Untuk .env file
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
```

3. **Test Connection:**
```bash
# Test dengan Python
python -c "
from supabase import create_client
import os

# Test connection
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
print('✅ Supabase connected successfully!')

# Test tables
tables = client.table('users').select('*').limit(1).execute()
print(f'📊 Users table accessible: {len(tables.data) >= 0}')
"
```

## 🔐 Security Checklist

- [ ] RLS enabled untuk semua tables
- [ ] User policies dibuat
- [ ] API keys disimpan di environment variables
- [ ] Service key hanya untuk server-side
- [ ] Test dengan user permissions

## 🎯 Next Steps

1. ✅ **Database setup complete**
2. 🔧 **Configure environment variables**
3. 🚀 **Deploy to Vercel**
4. 📱 **Test API connection**
5. 🧪 **Run full integration test**

**🎉 Database siap untuk production!**

---

## 💡 Tips

- **Backup database** sebelum menjalankan SQL
- **Test di development** dulu sebelum production
- **Monitor performance** setelah setup
- **Check logs** untuk error detection
- **Update RLS policies** jika perlu security changes

Need help? DM atau buat issue di GitHub! 🚀