"""
Database Integration with Supabase
Production-ready database for Instagram Automation Web App
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from dotenv import load_dotenv

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not available. Install with: pip install supabase")

load_dotenv()

class DatabaseManager:
    """Production database manager using Supabase"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

        self.client: Optional[Client] = None
        self.connected = False

        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            self.client = create_client(self.supabase_url, self.supabase_key)
            self.connected = True
            print("✅ Supabase connected successfully")

    def create_tables(self):
        """Initialize database tables"""
        if not self.connected:
            print("❌ Database not connected")
            return False

        # SQL untuk membuat tabel (bisa dijalankan di Supabase SQL Editor)
        create_tables_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            api_key TEXT NOT NULL,
            instagram_token TEXT,
            business_account_id TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            subscription_plan TEXT DEFAULT 'free',
            posts_created INTEGER DEFAULT 0,
            jobs_completed INTEGER DEFAULT 0
        );

        -- Jobs table
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
            error TEXT,
            total_posts INTEGER DEFAULT 0,
            auto_posted BOOLEAN DEFAULT FALSE
        );

        -- Posts table
        CREATE TABLE IF NOT EXISTS posts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
            topic TEXT NOT NULL,
            image_url TEXT,
            caption TEXT,
            hashtags JSONB,
            scheduled_time TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            posted_at TIMESTAMP WITH TIME ZONE,
            instagram_media_id TEXT,
            engagement_stats JSONB,
            auto_posted BOOLEAN DEFAULT FALSE
        );

        -- Job Results table
        CREATE TABLE IF NOT EXISTS job_results (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
            filename TEXT,
            posts_count INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Analytics table
        CREATE TABLE IF NOT EXISTS analytics (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            event_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
        CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_posts_job_id ON posts(job_id);
        CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic);
        CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);

        -- RLS (Row Level Security)
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

        -- RLS Policies
        CREATE POLICY "Users can view own data" ON users
            FOR SELECT USING (auth.uid()::text = api_key::text);

        CREATE POLICY "Users can update own data" ON users
            FOR UPDATE USING (auth.uid()::text = api_key::text);

        CREATE POLICY "Users can insert own data" ON users
            FOR INSERT WITH CHECK (auth.uid()::text = api_key::text);

        CREATE POLICY "Users can view own jobs" ON jobs
            FOR SELECT USING (auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id));

        CREATE POLICY "Users can insert own jobs" ON jobs
            FOR INSERT WITH CHECK (auth.uid()::text = (SELECT api_key::text FROM users WHERE id = jobs.user_id));

        -- Function to update updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        -- Trigger for updated_at
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """

        return create_tables_sql

    # User Management
    def create_or_update_user(self, api_key: str, instagram_config: Dict = None) -> Dict:
        """Create or update user"""
        try:
            # Check if user exists
            existing = self.client.table("users").select("*").eq("api_key", api_key).execute()

            user_data = {
                "api_key": api_key,
                "last_active": datetime.now().isoformat(),
            }

            if instagram_config:
                user_data.update({
                    "instagram_token": instagram_config.get("access_token"),
                    "business_account_id": instagram_config.get("business_account_id")
                })

            if existing.data:
                # Update existing user
                result = self.client.table("users").update(user_data).eq("api_key", api_key).execute()
                user = result.data[0]
            else:
                # Create new user
                result = self.client.table("users").insert(user_data).execute()
                user = result.data[0]

            return user

        except Exception as e:
            print(f"❌ Error creating/updating user: {e}")
            return {"error": str(e)}

    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Get user by API key"""
        try:
            result = self.client.table("users").select("*").eq("api_key", api_key).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None

    # Job Management
    def create_job(self, user_id: str, job_id: str, topics: List[str], options: Dict) -> Dict:
        """Create new job"""
        try:
            job_data = {
                "user_id": user_id,
                "job_id": job_id,
                "topics": topics,
                "options": options,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }

            result = self.client.table("jobs").insert(job_data).execute()
            return result.data[0]

        except Exception as e:
            print(f"❌ Error creating job: {e}")
            return {"error": str(e)}

    def update_job_status(self, job_id: str, status: str, **kwargs) -> Dict:
        """Update job status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }

            # Add optional fields
            if "progress" in kwargs:
                update_data["progress"] = kwargs["progress"]
            if "current_topic" in kwargs:
                update_data["current_topic"] = kwargs["current_topic"]
            if "message" in kwargs:
                update_data["message"] = kwargs["message"]
            if "error" in kwargs:
                update_data["error"] = kwargs["error"]
            if "total_posts" in kwargs:
                update_data["total_posts"] = kwargs["total_posts"]

            # Set timestamps
            if status == "running":
                update_data["started_at"] = datetime.now().isoformat()
            elif status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()
            elif status == "failed":
                update_data["failed_at"] = datetime.now().isoformat()

            result = self.client.table("jobs").update(update_data).eq("job_id", job_id).execute()
            return result.data[0] if result.data else {}

        except Exception as e:
            print(f"❌ Error updating job status: {e}")
            return {"error": str(e)}

    def get_user_jobs(self, user_id: str, status: str = None) -> List[Dict]:
        """Get user jobs"""
        try:
            query = self.client.table("jobs").select("*").eq("user_id", user_id)

            if status:
                query = query.eq("status", status)

            query = query.order("created_at", desc=True)
            result = query.execute()
            return result.data

        except Exception as e:
            print(f"❌ Error getting jobs: {e}")
            return []

    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        try:
            result = self.client.table("jobs").select("*").eq("job_id", job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting job: {e}")
            return None

    # Post Management
    def create_posts(self, job_id: str, posts: List) -> List[Dict]:
        """Create multiple posts"""
        try:
            posts_data = []
            for post in posts:
                post_data = {
                    "job_id": job_id,
                    "topic": post.topic,
                    "image_url": post.image_url,
                    "caption": post.caption,
                    "hashtags": post.hashtags,
                    "scheduled_time": post.scheduled_time.isoformat(),
                    "created_at": datetime.now().isoformat()
                }
                posts_data.append(post_data)

            result = self.client.table("posts").insert(posts_data).execute()
            return result.data

        except Exception as e:
            print(f"❌ Error creating posts: {e}")
            return []

    def get_job_posts(self, job_id: str) -> List[Dict]:
        """Get posts for a job"""
        try:
            result = self.client.table("posts").select("*").eq("job_id", job_id).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting posts: {e}")
            return []

    # Analytics
    def track_event(self, user_id: str, event_type: str, event_data: Dict):
        """Track analytics event"""
        try:
            analytics_data = {
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "created_at": datetime.now().isoformat()
            }

            self.client.table("analytics").insert(analytics_data).execute()

        except Exception as e:
            print(f"❌ Error tracking event: {e}")

    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        try:
            # Get basic stats
            posts_count = self.client.table("posts").select("*", count="exact").eq("job_id",
                self.client.table("jobs").select("id").eq("user_id", user_id).execute().data
            ).execute()

            jobs_completed = self.client.table("jobs").select("*", count="exact").eq("user_id", user_id).eq("status", "completed").execute()

            jobs_active = self.client.table("jobs").select("*", count="exact").eq("user_id", user_id).eq("status", "running").execute()

            # Get unique topics
            topics_query = self.client.table("posts").select("topic").eq("job_id",
                self.client.table("jobs").select("id").eq("user_id", user_id).execute().data
            ).execute()

            unique_topics = len(set(post["topic"] for post in topics_query.data)) if topics_query.data else 0

            return {
                "total_posts": posts_count.count if hasattr(posts_count, 'count') else 0,
                "completed_jobs": jobs_completed.count if hasattr(jobs_completed, 'count') else 0,
                "active_jobs": jobs_active.count if hasattr(jobs_active, 'count') else 0,
                "topics_covered": unique_topics
            }

        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return {
                "total_posts": 0,
                "completed_jobs": 0,
                "active_jobs": 0,
                "topics_covered": 0
            }

    # Cleanup
    def cleanup_old_jobs(self, days: int = 30):
        """Clean up old completed jobs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Delete old jobs and related posts
            old_jobs = self.client.table("jobs").select("id").lt("created_at", cutoff_date.isoformat()).eq("status", "completed").execute()

            for job in old_jobs.data:
                # Delete posts
                self.client.table("posts").delete().eq("job_id", job["id"]).execute()
                # Delete job results
                self.client.table("job_results").delete().eq("job_id", job["id"]).execute()
                # Delete job
                self.client.table("jobs").delete().eq("id", job["id"]).execute()

            print(f"🧹 Cleaned up {len(old_jobs.data)} old jobs")

        except Exception as e:
            print(f"❌ Error cleaning up old jobs: {e}")

# Global database instance
db = DatabaseManager()

# Database helper functions for Flask app
def init_database():
    """Initialize database tables"""
    if not db.connected:
        return False

    sql = db.create_tables()
    print("📝 Database SQL created. Run this in Supabase SQL Editor:")
    print("="*60)
    print(sql)
    print("="*60)
    return True

def get_db():
    """Get database instance"""
    return db

if __name__ == "__main__":
    # Test database connection
    print("🔍 Testing database connection...")

    if db.connected:
        print("✅ Database connected successfully!")

        # Print SQL for table creation
        init_database()

    else:
        print("❌ Database connection failed!")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file")