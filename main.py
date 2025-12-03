#!/usr/bin/env python3
"""
Instagram Automation System using Z.ai API
Automated news content creation and posting system
"""

import os
import asyncio
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class NewsContent:
    """Data structure for news content"""
    title: str
    url: str
    summary: str
    content: str
    image_url: Optional[str] = None
    publish_date: Optional[str] = None
    source: Optional[str] = None

@dataclass
class InstagramPost:
    """Data structure for Instagram post"""
    image_url: str
    caption: str
    hashtags: List[str]
    scheduled_time: datetime
    topic: str

class ZAIClient:
    """Z.ai API Client wrapper"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.z.ai/api/paas/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, prompt: str, model: str = "glm-4.6",
                       temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate text using Z.ai chat completion API"""

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            print(f"Chat completion error: {e}")
            return ""

    def generate_image(self, prompt: str, size: str = "1024x1024",
                      quality: str = "hd") -> Optional[str]:
        """Generate image using Z.ai image generation API"""

        payload = {
            "model": "cogview-4",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1
        }

        try:
            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return result['data'][0]['url']

        except requests.exceptions.RequestException as e:
            print(f"Image generation error: {e}")
            return None

    def web_search(self, query: str, time_filter: str = "oneDay",
                   max_results: int = 10) -> List[Dict]:
        """Search web for news using Z.ai web search API"""

        payload = {
            "query": query,
            "time_filter": time_filter,
            "max_results": max_results
        }

        try:
            response = requests.post(
                f"{self.base_url}/tools/web-search",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result.get('results', [])

        except requests.exceptions.RequestException as e:
            print(f"Web search error: {e}")
            return []

    def web_reader(self, url: str, format: str = "markdown") -> Optional[str]:
        """Extract content from URL using Z.ai web reader API"""

        payload = {
            "url": url,
            "format": format
        }

        try:
            response = requests.post(
                f"{self.base_url}/tools/web-reader",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result.get('content')

        except requests.exceptions.RequestException as e:
            print(f"Web reader error: {e}")
            return None

class InstagramAutomation:
    """Main Instagram Automation System"""

    def __init__(self, zai_api_key: str):
        self.zai_client = ZAIClient(zai_api_key)
        self.posts_queue = []

    def search_news(self, topic: str, time_range: str = "oneDay") -> List[NewsContent]:
        """Search for news based on topic"""

        print(f"🔍 Searching news for topic: {topic}")

        # Search query in Indonesian for better local results
        search_query = f"berita terbaru {topic} Indonesia"
        search_results = self.zai_client.web_search(
            query=search_query,
            time_filter=time_range,
            max_results=10
        )

        news_contents = []

        for result in search_results:
            # Extract content from each URL
            content = self.zai_client.web_reader(result['url'])

            if content:
                news_content = NewsContent(
                    title=result['title'],
                    url=result['url'],
                    summary=result.get('summary', ''),
                    content=content,
                    source=self._extract_domain(result['url']),
                    publish_date=result.get('publish_date')
                )
                news_contents.append(news_content)

        print(f"📰 Found {len(news_contents)} news articles")
        return news_contents

    def generate_caption(self, news_content: NewsContent, topic: str) -> str:
        """Generate Instagram caption from news content"""

        prompt = f"""
        Buat caption Instagram yang menarik untuk berita ini:

        Judul: {news_content.title}
        Ringkasan: {news_content.summary}
        Topik: {topic}
        Sumber: {news_content.source}

        Format:
        1. Hook menarik di awal (1-2 kalimat)
        2. Summary berita dalam bahasa yang mudah dipahami (2-3 kalimat)
        3. Call to action untuk engagement
        4. 3-5 hashtags yang relevan dan trending

        Style:
        - Engagement, friendly, shareable
        - Menggunakan bahasa yang relatable
        - Tidak terlalu formal
        - Mendorong interaksi

        Caption harus singkat (maksimal 200 kata) dan menarik untuk dibaca.
        """

        caption = self.zai_client.chat_completion(
            prompt=prompt,
            temperature=0.7,
            max_tokens=300
        )

        return caption

    def generate_instagram_image(self, news_content: NewsContent, topic: str) -> Optional[str]:
        """Generate Instagram image from news content"""

        prompt = f"""
        Buat gambar Instagram yang menarik dan profesional untuk berita:

        Judul Berita: {news_content.title}
        Topik: {topic}
        Sumber: {news_content.source}

        Style Requirements:
        - Modern, clean design
        - Eye-catching colors yang sesuai dengan topik
        - Social media optimized (1024x1024)
        - Space untuk text overlay yang readable
        - Professional layout
        - Minimalis tapi informatif

        Text Overlay:
        Tambahkan judul berita dengan font yang mudah dibaca:
        "{news_content.title[:60]}..."

        Additional Elements:
- Background yang relevan dengan topik
- Visual hierarchy yang jelas
- Instagram-friendly aesthetic
        """

        print(f"🎨 Generating image for: {news_content.title[:50]}...")
        image_url = self.zai_client.generate_image(
            prompt=prompt,
            size="1024x1024",
            quality="hd"
        )

        if image_url:
            print(f"✅ Image generated: {image_url}")
        else:
            print(f"❌ Failed to generate image")

        return image_url

    def create_instagram_post(self, news_content: NewsContent, topic: str) -> Optional[InstagramPost]:
        """Create complete Instagram post from news content"""

        print(f"📱 Creating Instagram post for: {news_content.title[:50]}...")

        # Generate caption
        caption = self.generate_caption(news_content, topic)

        # Generate image
        image_url = self.generate_instagram_image(news_content, topic)

        if not image_url:
            print(f"❌ Failed to create post - no image generated")
            return None

        # Extract hashtags from caption
        hashtags = self._extract_hashtags(caption)

        # Schedule optimal posting time (tomorrow at optimal hours)
        scheduled_time = self._get_optimal_posting_time()

        post = InstagramPost(
            image_url=image_url,
            caption=caption,
            hashtags=hashtags,
            scheduled_time=scheduled_time,
            topic=topic
        )

        print(f"✅ Instagram post created successfully")
        return post

    def process_topic(self, topic: str, time_range: str = "oneDay", max_posts: int = 3) -> List[InstagramPost]:
        """Process a topic and create Instagram posts"""

        print(f"\n🚀 Processing topic: {topic}")
        print("=" * 50)

        # Search for news
        news_contents = self.search_news(topic, time_range)

        if not news_contents:
            print(f"❌ No news found for topic: {topic}")
            return []

        # Create Instagram posts
        posts = []
        for i, news_content in enumerate(news_contents[:max_posts]):
            print(f"\n📝 Processing article {i+1}/{min(max_posts, len(news_contents))}")

            post = self.create_instagram_post(news_content, topic)
            if post:
                posts.append(post)
                self.posts_queue.append(post)

        print(f"\n✅ Successfully created {len(posts)} Instagram posts for topic: {topic}")
        return posts

    def generate_post_summary(self, posts: List[InstagramPost]) -> str:
        """Generate summary of created posts"""

        if not posts:
            return "No posts created"

        summary = f"""
📊 INSTAGRAM POST SUMMARY
========================
Total Posts: {len(posts)}
Topics: {list(set([post.topic for post in posts]))}
Scheduled Times: {[post.scheduled_time.strftime('%Y-%m-%d %H:%M') for post in posts]}

POST PREVIEWS:
--------------
"""

        for i, post in enumerate(posts, 1):
            summary += f"""
{i}. {post.topic}
   Caption: {post.caption[:100]}...
   Hashtags: {', '.join(post.hashtags[:3])}...
   Scheduled: {post.scheduled_time.strftime('%Y-%m-%d %H:%M')}
"""

        return summary

    def save_posts_to_file(self, posts: List[InstagramPost], filename: str = None) -> str:
        """Save posts to JSON file"""

        if not filename:
            filename = f"instagram_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        posts_data = []
        for post in posts:
            post_dict = {
                "topic": post.topic,
                "image_url": post.image_url,
                "caption": post.caption,
                "hashtags": post.hashtags,
                "scheduled_time": post.scheduled_time.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            posts_data.append(post_dict)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Posts saved to: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Error saving posts: {e}")
            return ""

    # Helper methods
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "Unknown"

    def _extract_hashtags(self, caption: str) -> List[str]:
        """Extract hashtags from caption"""
        import re
        hashtags = re.findall(r'#\w+', caption)
        return hashtags

    def _get_optimal_posting_time(self) -> datetime:
        """Get optimal posting time for Instagram"""
        # Best times: 8AM, 12PM, 6PM, 8PM
        optimal_hours = [8, 12, 18, 20]

        # Schedule for tomorrow at random optimal hour
        tomorrow = datetime.now() + timedelta(days=1)
        import random
        hour = random.choice(optimal_hours)

        return tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)

def main():
    """Main function to test the system"""

    # Get API key from environment or user input
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        api_key = input("Enter your Z.ai API key: ").strip()

    if not api_key:
        print("❌ Z.ai API key is required!")
        return

    # Initialize system
    print("🤖 Initializing Instagram Automation System...")
    automation = InstagramAutomation(api_key)

    # Test with sample topics
    test_topics = [
        "teknologi",
        "bisnis",
        "kesehatan",
        "olahraga"
    ]

    print(f"\n🎯 Testing system with topics: {', '.join(test_topics)}")

    all_posts = []

    try:
        for topic in test_topics:
            posts = automation.process_topic(topic, time_range="oneDay", max_posts=2)
            all_posts.extend(posts)

            # Small delay between topics to avoid rate limiting
            time.sleep(2)

        # Generate summary
        print("\n" + "="*60)
        summary = automation.generate_post_summary(all_posts)
        print(summary)

        # Save to file
        if all_posts:
            filename = automation.save_posts_to_file(all_posts)
            print(f"\n🎉 System test completed!")
            print(f"📁 Posts saved to: {filename}")
            print(f"📈 Total posts created: {len(all_posts)}")

    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()