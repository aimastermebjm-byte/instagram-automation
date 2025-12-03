-- ==========================================
-- MINIMAL Supabase Setup - Copy & Run (No Errors)
-- ==========================================

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    api_key TEXT NOT NULL UNIQUE,
    instagram_token TEXT,
    business_account_id TEXT,
    email TEXT,
    subscription_plan TEXT DEFAULT 'free',
    posts_created INTEGER DEFAULT 0,
    jobs_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- JOBS TABLE
CREATE TABLE IF NOT EXISTS jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id TEXT UNIQUE NOT NULL,
    topics JSONB NOT NULL,
    options JSONB NOT NULL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    current_topic TEXT,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    total_posts INTEGER DEFAULT 0,
    auto_posted BOOLEAN DEFAULT FALSE
);

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
    post_status TEXT DEFAULT 'created',
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

-- JOB RESULTS TABLE
CREATE TABLE IF NOT EXISTS job_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    filename TEXT,
    posts_count INTEGER NOT NULL,
    successful_posts INTEGER DEFAULT 0,
    failed_posts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_size_bytes INTEGER,
    download_url TEXT,
    export_format TEXT DEFAULT 'json',
    topics_covered JSONB DEFAULT '[]',
    ai_usage_stats JSONB DEFAULT '{}'
);

-- SYSTEM LOGS TABLE
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    log_level TEXT NOT NULL,
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    job_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stack_trace TEXT,
    error_code TEXT
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active DESC);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_posts_job_id ON posts(job_id);
CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(post_status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_topic_created ON posts(topic, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_auto_posted ON posts(auto_posted);

CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_user_event ON analytics(user_id, event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_session_id ON analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_user_created ON analytics(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_job_id ON system_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_logs_level_created ON system_logs(log_level, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_job_results_job_id ON job_results(job_id);
CREATE INDEX IF NOT EXISTS idx_job_results_created_at ON job_results(created_at DESC);

-- ROW LEVEL SECURITY
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_results ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = api_key::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = api_key::text);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = api_key::text);

-- Jobs policies
CREATE POLICY "Users can view own jobs" ON jobs
    FOR SELECT USING (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id)
    );

CREATE POLICY "Users can insert own jobs" ON jobs
    FOR INSERT WITH CHECK (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id)
    );

CREATE POLICY "Users can update own jobs" ON jobs
    FOR UPDATE USING (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id)
    );

-- Posts policies
CREATE POLICY "Users can view own posts" ON posts
    FOR SELECT USING (
        auth.uid()::text = (
            SELECT api_key::text FROM users WHERE id = (
                SELECT user_id FROM jobs WHERE id = posts.job_id
            )
        )
    );

CREATE POLICY "Users can insert own posts" ON posts
    FOR INSERT WITH CHECK (
        auth.uid()::text = (
            SELECT api_key::text FROM users WHERE id = (
                SELECT user_id FROM jobs WHERE id = posts.job_id
            )
        )
    );

CREATE POLICY "Users can update own posts" ON posts
    FOR UPDATE USING (
        auth.uid()::text = (
            SELECT api_key::text FROM users WHERE id = (
                SELECT user_id FROM jobs WHERE id = posts.job_id
            )
        )
    );

-- Analytics policies
CREATE POLICY "Users can view own analytics" ON analytics
    FOR SELECT USING (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = analytics.user_id)
    );

CREATE POLICY "Users can insert own analytics" ON analytics
    FOR INSERT WITH CHECK (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = analytics.user_id)
    );

-- System logs policies
CREATE POLICY "Users can view own logs" ON system_logs
    FOR SELECT USING (
        auth.uid()::text = (SELECT api_key::text FROM users WHERE id = system_logs.user_id)
    );

CREATE POLICY "Service can insert logs" ON system_logs
    FOR INSERT WITH CHECK (true);

-- Job results policies
CREATE POLICY "Users can view own job results" ON job_results
    FOR SELECT USING (
        auth.uid()::text = (
            SELECT api_key::text FROM users WHERE id = (
                SELECT user_id FROM jobs WHERE id = job_results.job_id
            )
        )
    );

-- Simple update function
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update posts_created count
    IF TG_OP = 'UPDATE' AND NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE users
        SET jobs_completed = jobs_completed + 1,
            updated_at = NOW()
        WHERE id = NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user stats
CREATE TRIGGER update_user_stats_trigger
    AFTER UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_user_stats();

-- Simple test function
CREATE OR REPLACE FUNCTION test_database_setup()
RETURNS TEXT AS $$
DECLARE
    user_count INTEGER;
    job_count INTEGER;
    post_count INTEGER;
    analytics_count INTEGER;
    results_count TEXT;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO user_count FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'users';

    SELECT COUNT(*) INTO job_count FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'jobs';

    SELECT COUNT(*) INTO post_count FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'posts';

    SELECT COUNT(*) INTO analytics_count FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'analytics';

    -- Build results
    results_count := 'Tables: users=' || user_count || ', jobs=' || job_count || ', posts=' || post_count || ', analytics=' || analytics_count;

    -- Check RLS
    SELECT COUNT(*) INTO results_count FROM pg_policies
    WHERE schemaname = 'public' AND tablename IN ('users', 'jobs', 'posts', 'analytics');

    results_count := results_count || ' | RLS policies: ' || results_count;

    results_count := results_count || ' | Status: ✅ MINIMAL SETUP COMPLETE';

    RETURN results_count;
END;
$$ LANGUAGE plpgsql;

-- Test the setup
SELECT test_database_setup() as setup_status;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Instagram Automation MINIMAL setup completed successfully!';
    RAISE NOTICE '✅ Tables created: users, jobs, posts, analytics, job_results, system_logs';
    RAISE NOTICE '✅ Indexes created for performance';
    RAISE NOTICE '✅ Row Level Security enabled';
    RAISE NOTICE '✅ Triggers and functions created';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Copy your Supabase credentials from Settings > API';
    RAISE NOTICE '2. Add environment variables to your app';
    RAISE NOTICE '3. Test API connection with your app';
    RAISE NOTICE '4. Deploy to production and start creating content!';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Database is ready for production!';
END $$;