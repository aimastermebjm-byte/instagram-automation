"""
Instagram Graph API Client for automated posting
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional, List
import time
from config import config

class InstagramClient:
    """Instagram Graph API Client"""

    def __init__(self):
        self.access_token = config.INSTAGRAM_ACCESS_TOKEN
        self.business_account_id = config.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.page_id = config.INSTAGRAM_PAGE_ID
        self.base_url = config.FACEBOOK_GRAPH_URL

    def is_configured(self) -> bool:
        """Check if Instagram API is properly configured"""
        return all([
            self.access_token,
            self.business_account_id,
            self.page_id
        ])

    def create_media_container(self, image_url: str, caption: str) -> Optional[str]:
        """
        Create media container for Instagram post
        Returns media creation ID
        """
        if not self.is_configured():
            print("⚠️  Instagram API not configured - skipping post creation")
            return None

        url = f"{self.base_url}/{self.page_id}/media"

        params = {
            'access_token': self.access_token,
            'image_url': image_url,
            'caption': caption,
            'media_type': 'IMAGE'
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            creation_id = result.get('id')

            if creation_id:
                print(f"✅ Media container created: {creation_id}")
                return creation_id
            else:
                print(f"❌ Failed to create media container: {result}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating media container: {e}")
            return None

    def publish_media(self, creation_id: str) -> Optional[str]:
        """
        Publish media container to Instagram
        Returns published media ID
        """
        if not self.is_configured():
            print("⚠️  Instagram API not configured - skipping publish")
            return None

        url = f"{self.base_url}/{self.page_id}/media_publish"

        params = {
            'access_token': self.access_token,
            'creation_id': creation_id
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            media_id = result.get('id')

            if media_id:
                print(f"✅ Media published to Instagram: {media_id}")
                return media_id
            else:
                print(f"❌ Failed to publish media: {result}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error publishing media: {e}")
            return None

    def get_media_info(self, media_id: str) -> Optional[Dict]:
        """Get information about published media"""

        if not self.is_configured():
            return None

        url = f"{self.base_url}/{media_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            print(f"📊 Media info retrieved: {result.get('permalink', 'N/A')}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting media info: {e}")
            return None

    def get_business_account_info(self) -> Optional[Dict]:
        """Get Instagram business account information"""

        if not self.is_configured():
            return None

        url = f"{self.base_url}/{self.business_account_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'id,username,account_type,followers_count,follows_count,media_count'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            print(f"📈 Account info: @{result.get('username')} ({result.get('followers_count', 0)} followers)")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting account info: {e}")
            return None

    def schedule_post(self, image_url: str, caption: str,
                     scheduled_time: datetime = None) -> Optional[Dict]:
        """
        Schedule Instagram post (note: Instagram doesn't have native scheduling
        through Graph API, so this creates a reminder for manual posting)
        """

        if not self.is_configured():
            print("⚠️  Instagram API not configured - creating scheduling reminder")
            return self._create_scheduling_reminder(image_url, caption, scheduled_time)

        # Create media container first
        creation_id = self.create_media_container(image_url, caption)
        if not creation_id:
            return None

        # Note: Instagram doesn't support direct scheduling through Graph API
        # This would require a scheduling system that publishes at the specified time
        if scheduled_time and scheduled_time > datetime.now():
            print(f"⏰ Post scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            print("💡 Note: Manual implementation of scheduler needed for automatic posting")

            # Create scheduling record
            scheduled_post = {
                'creation_id': creation_id,
                'scheduled_time': scheduled_time.isoformat(),
                'image_url': image_url,
                'caption': caption,
                'status': 'scheduled'
            }

            self._save_scheduled_post(scheduled_post)
            return scheduled_post

        # Publish immediately if no scheduling
        media_id = self.publish_media(creation_id)
        if media_id:
            media_info = self.get_media_info(media_id)
            return {
                'media_id': media_id,
                'media_info': media_info,
                'status': 'published',
                'posted_at': datetime.now().isoformat()
            }

        return None

    def _create_scheduling_reminder(self, image_url: str, caption: str,
                                  scheduled_time: datetime = None) -> Dict:
        """Create reminder for manual posting when API not configured"""

        reminder = {
            'image_url': image_url,
            'caption': caption,
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else datetime.now().isoformat(),
            'status': 'manual_posting_required',
            'instructions': 'Post manually to Instagram or configure Instagram API'
        }

        # Save to scheduled posts file
        self._save_scheduled_post(reminder)

        print("💾 Post saved for manual posting")
        print(f"📱 Post caption: {caption[:100]}...")
        print(f"🖼️  Image: {image_url}")
        if scheduled_time:
            print(f"⏰ Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")

        return reminder

    def _save_scheduled_post(self, post_data: Dict):
        """Save scheduled post to file"""

        os.makedirs(config.POSTS_OUTPUT_DIR, exist_ok=True)
        filename = f"{config.POSTS_OUTPUT_DIR}/scheduled_posts.json"

        try:
            # Load existing posts
            existing_posts = []
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_posts = json.load(f)

            # Add new post
            post_data['created_at'] = datetime.now().isoformat()
            existing_posts.append(post_data)

            # Save updated list
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_posts, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Error saving scheduled post: {e}")

    def get_scheduled_posts(self) -> List[Dict]:
        """Get all scheduled posts"""

        filename = f"{config.POSTS_OUTPUT_DIR}/scheduled_posts.json"

        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []

        except Exception as e:
            print(f"❌ Error loading scheduled posts: {e}")
            return []

    def test_connection(self) -> bool:
        """Test Instagram API connection"""

        if not self.is_configured():
            print("⚠️  Instagram API not configured")
            return False

        try:
            print("🔍 Testing Instagram API connection...")
            account_info = self.get_business_account_info()

            if account_info:
                print(f"✅ Instagram API connection successful")
                print(f"📊 Account: @{account_info.get('username')}")
                print(f"👥 Followers: {account_info.get('followers_count', 0):,}")
                print(f"📱 Media count: {account_info.get('media_count', 0):,}")
                return True
            else:
                print("❌ Instagram API connection failed")
                return False

        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False