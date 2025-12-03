#!/usr/bin/env python3
"""
URL-Specific Instagram Content Generator
Using Z.ai API for real content generation
Focus: URL-based news processing (no mock data)
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class NewsContent:
    """Data structure for processed news content"""
    title: str
    url: str
    summary: str
    content: str
    topic: str
    source: str
    processed_at: str

@dataclass
class GeneratedContent:
    """Data structure for generated Instagram content"""
    topic: str
    original_url: str
    news_summary: str
    generated_caption: str
    generated_image_url: str
    hashtags: List[str]
    created_at: str

class URLContentGenerator:
    """URL-based content generator using Z.ai API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.z.ai/api/paas/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"🔑 Initialized with API Key: {api_key[:10]}...{api_key[-6:]}")

    def test_api_connection(self) -> bool:
        """Test connection to Z.ai API"""
        try:
            print("🧪 Testing API connection...")

            payload = {
                "model": "glm-4.6",
                "messages": [{"role": "user", "content": "Hello, test connection"}],
                "max_tokens": 10,
                "temperature": 0.1
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print("✅ API connection successful!")
                return True
            else:
                print(f"❌ API connection failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ API connection error: {e}")
            return False

    def extract_content_from_url(self, url: str) -> Optional[str]:
        """Extract content from URL using Z.ai Web Reader"""
        try:
            print(f"📖 Extracting content from: {url}")

            payload = {
                "url": url,
                "format": "markdown"
            }

            response = requests.post(
                f"{self.base_url}/tools/web-reader",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('content', '')

                if content and len(content) > 100:
                    print(f"✅ Content extracted successfully ({len(content)} characters)")
                    return content
                else:
                    print(f"❌ Content too short or empty: {len(content) if content else 0} characters")
                    return None
            else:
                print(f"❌ Failed to extract content: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            return None

    def generate_news_summary(self, content: str, topic: str) -> Optional[str]:
        """Generate news summary using Z.ai"""
        try:
            print("📝 Generating news summary...")

            prompt = f"""
            Buat ringkasan berita yang informatif dari konten berikut:

            Topik: {topic}
            Konten: {content[:2000]}...

            Format ringkasan:
            1. Judul yang menarik (1 baris)
            2. Ringkasan inti berita (2-3 kalimat)
            3. Poin-poin penting (maksimal 3 poin)
            4. Konteks atau dampak berita (1 kalimat)

            Style:
            - Ringkas dan padat
            - Mudah dipahami
            - Factual dan objektif
            - Bahasa Indonesia yang baik

            Maksimal 150 kata.
            """

            payload = {
                "model": "glm-4.6",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.5
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content']
                print(f"✅ Summary generated ({len(summary)} characters)")
                return summary
            else:
                print(f"❌ Failed to generate summary: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return None

    def generate_instagram_caption(self, news_summary: str, topic: str) -> Optional[str]:
        """Generate Instagram caption from news summary"""
        try:
            print("📱 Generating Instagram caption...")

            prompt = f"""
            Buat caption Instagram yang engagement dan menarik untuk berita ini:

            Topik: {topic}
            Ringkasan Berita: {news_summary}

            Format Caption Instagram:
            1. Hook yang menarik perhatian (1-2 kalimat dengan emoji)
            2. Summary berita dalam bahasa yang relatable (2-3 kalimat)
            3. Question atau call to action untuk engagement (1 kalimat)
            4. 3-5 hashtags yang relevan dan trending

            Style:
            - Friendly dan conversational
            - Menggunakan bahasa yang relatable
            - Engagement-focused
            - Instagram native feel
            - Tidak terlalu formal

            Maksimal 200 kata.
            """

            payload = {
                "model": "glm-4.6",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.7
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                caption = result['choices'][0]['message']['content']
                print(f"✅ Caption generated ({len(caption)} characters)")
                return caption
            else:
                print(f"❌ Failed to generate caption: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error generating caption: {e}")
            return None

    def generate_instagram_image(self, news_summary: str, topic: str) -> Optional[str]:
        """Generate Instagram image using Z.ai CogView-4"""
        try:
            print("🎨 Generating Instagram image...")

            # Extract key points from summary for better image prompt
            prompt = f"""
            Create a professional, modern Instagram post image about:

            Topic: {topic}
            News Summary: {news_summary[:200]}...

            Style Requirements:
            - Instagram square format (1024x1024)
            - Modern, clean design
            - Professional typography
            - Eye-catching but readable
            - Social media optimized

            Text Overlay:
            - Include a headline related to: "{topic}"
            - Bold, readable font
            - Good contrast with background

            Visual Elements:
            - Background theme relevant to: {topic}
            - Professional color scheme
            - Clean, minimalist aesthetic
            - High quality, social media ready

            Style: Modern corporate, digital, technology-focused if applicable
            """

            payload = {
                "model": "cogview-4",
                "prompt": prompt,
                "size": "1024x1024",
                "quality": "hd",
                "n": 1
            }

            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                image_url = result['data'][0]['url']
                print(f"✅ Image generated: {image_url}")
                return image_url
            else:
                print(f"❌ Failed to generate image: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None

    def extract_hashtags(self, caption: str) -> List[str]:
        """Extract hashtags from caption"""
        import re
        hashtags = re.findall(r'#\w+', caption)
        return hashtags

    def process_url_content(self, url: str, topic: str) -> Optional[GeneratedContent]:
        """Main workflow: Process URL content and generate Instagram content"""

        print(f"\n🚀 Processing URL content...")
        print(f"📰 URL: {url}")
        print(f"🏷️  Topic: {topic}")
        print("=" * 60)

        # Step 1: Extract content from URL
        content = self.extract_content_from_url(url)
        if not content:
            print("❌ Failed to extract content from URL")
            return None

        # Step 2: Generate news summary
        news_summary = self.generate_news_summary(content, topic)
        if not news_summary:
            print("❌ Failed to generate news summary")
            return None

        # Step 3: Generate Instagram caption
        caption = self.generate_instagram_caption(news_summary, topic)
        if not caption:
            print("❌ Failed to generate Instagram caption")
            return None

        # Step 4: Generate Instagram image
        image_url = self.generate_instagram_image(news_summary, topic)
        if not image_url:
            print("❌ Failed to generate Instagram image")
            return None

        # Step 5: Extract hashtags
        hashtags = self.extract_hashtags(caption)

        # Step 6: Create result object
        result = GeneratedContent(
            topic=topic,
            original_url=url,
            news_summary=news_summary,
            generated_caption=caption,
            generated_image_url=image_url,
            hashtags=hashtags,
            created_at=datetime.now().isoformat()
        )

        print(f"\n✅ Content generation completed successfully!")
        return result

    def display_results(self, content: GeneratedContent):
        """Display generated content results"""
        print(f"\n🎉 GENERATED CONTENT RESULTS")
        print("=" * 60)

        print(f"\n📰 Topic: {content.topic}")
        print(f"🔗 Source URL: {content.original_url}")
        print(f"⏰ Created: {content.created_at}")

        print(f"\n📝 News Summary:")
        print("-" * 30)
        print(f"{content.news_summary}")

        print(f"\n📱 Instagram Caption:")
        print("-" * 30)
        print(f"{content.generated_caption}")

        print(f"\n🏷️  Hashtags:")
        print("-" * 30)
        if content.hashtags:
            print(f"{' '.join(content.hashtags)}")
        else:
            print("No hashtags found in caption")

        print(f"\n🎨 Generated Image:")
        print("-" * 30)
        print(f"URL: {content.generated_image_url}")

        print(f"\n💾 Content saved and ready to use!")

    def save_results_to_file(self, content: GeneratedContent, filename: str = None) -> str:
        """Save generated content to JSON file"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_content_{timestamp}.json"

        content_dict = {
            "topic": content.topic,
            "original_url": content.original_url,
            "news_summary": content.news_summary,
            "generated_caption": content.generated_caption,
            "generated_image_url": content.generated_image_url,
            "hashtags": content.hashtags,
            "created_at": content.created_at
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, ensure_ascii=False, indent=2)

            print(f"💾 Results saved to: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return ""

def main():
    """Main function for URL-based content generation"""

    print("🤖 URL-Specific Instagram Content Generator")
    print("Using Z.ai API - Real Content Generation")
    print("=" * 60)

    # Get API key from environment
    api_key = os.getenv("ZAI_API_KEY")

    if not api_key:
        print("❌ ZAI_API_KEY not found in environment variables!")
        print("Please set up your .env file with your Z.ai API key")
        return

    # Initialize generator
    generator = URLContentGenerator(api_key)

    # Test API connection
    if not generator.test_api_connection():
        print("❌ Failed to connect to Z.ai API")
        print("Please check your API key and internet connection")
        return

    # Get user input
    print(f"\n📝 Enter content details:")
    print("-" * 30)

    topic = input("🏷️  Topic (e.g., teknologi, bisnis, kesehatan): ").strip()
    url = input("🔗 News URL: ").strip()

    if not topic or not url:
        print("❌ Both topic and URL are required!")
        return

    print(f"\n🚀 Starting content generation...")

    try:
        # Process URL content
        generated_content = generator.process_url_content(url, topic)

        if generated_content:
            # Display results
            generator.display_results(generated_content)

            # Save to file
            filename = generator.save_results_to_file(generated_content)

            print(f"\n🎉 Content generation completed successfully!")
            print(f"📁 Results saved to: {filename}")
            print(f"\n📱 Your Instagram content is ready to use!")

        else:
            print(f"\n❌ Content generation failed!")
            print(f"Please check the error messages above and try again.")

    except KeyboardInterrupt:
        print(f"\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()