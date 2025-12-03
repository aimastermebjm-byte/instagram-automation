"""
Configuration settings for Instagram Automation System
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class"""

    # Z.ai API Configuration
    ZAI_API_KEY = os.getenv("ZAI_API_KEY")

    # Instagram API Configuration
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

    # Facebook App Configuration
    FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")

    # System Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    POSTS_PER_TOPIC = int(os.getenv("POSTS_PER_TOPIC", "3"))
    DEFAULT_TIME_RANGE = os.getenv("DEFAULT_TIME_RANGE", "oneDay")
    ENABLE_SCHEDULING = os.getenv("ENABLE_SCHEDULING", "true").lower() == "true"

    # Rate Limiting
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "2"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    # API URLs
    ZAI_BASE_URL = "https://api.z.ai/api/paas/v4"
    FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v18.0"

    # Topics Configuration
    DEFAULT_TOPICS = [
        "teknologi",
        "bisnis",
        "kesehatan",
        "olahraga",
        "hiburan",
        "politik",
        "sains",
        "travel",
        "kuliner",
        "fashion"
    ]

    # Indonesian News Sources
    INDONESIAN_NEWS_DOMAINS = [
        "detik.com",
        "kompas.com",
        "tempo.co",
        "cnnindonesia.com",
        "liputan6.com",
        "tribunnews.com",
        "sindonews.com",
        "viva.co.id",
        "merdeka.com",
        "okezone.com",
        "suara.com",
        "antaranews.com",
        "republika.co.id",
        "mediaindonesia.com",
        "jawapos.com"
    ]

    # Image Generation Settings
    DEFAULT_IMAGE_SIZE = "1024x1024"
    DEFAULT_IMAGE_QUALITY = "hd"
    MAX_IMAGE_GENERATION_RETRIES = 3

    # Content Generation Settings
    CAPTION_MAX_TOKENS = 300
    CAPTION_TEMPERATURE = 0.7
    SUMMARY_MAX_TOKENS = 150
    SUMMARY_TEMPERATURE = 0.5

    # Instagram Settings
    MAX_HASHTAGS = 5
    MAX_CAPTION_LENGTH = 2200
    OPTIMAL_POSTING_HOURS = [8, 12, 15, 18, 20]

    # File Paths
    POSTS_OUTPUT_DIR = "generated_posts"
    LOGS_DIR = "logs"

    # Validation
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.ZAI_API_KEY:
            print("❌ ZAI_API_KEY is required")
            return False

        if self.POSTS_PER_TOPIC < 1 or self.POSTS_PER_TOPIC > 10:
            print("⚠️  POSTS_PER_TOPIC should be between 1 and 10")

        return True

# Global configuration instance
config = Config()