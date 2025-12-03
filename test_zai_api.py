#!/usr/bin/env python3
"""
Z.ai API Testing Script
Test all Z.ai API capabilities for Instagram automation project
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZAITestSuite:
    """Comprehensive Z.ai API test suite"""

    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        self.base_url = "https://api.z.ai/api/paas/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = "", data: dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")

    def test_chat_completion(self):
        """Test chat completion API for caption generation"""
        test_name = "Chat Completion (Caption Generation)"

        prompt = """
        Buat Instagram caption yang menarik untuk berita teknologi:

        Judul: "AI Revolution: Machine Learning Transforms Healthcare Industry"
        Ringkasan: "Latest developments in AI healthcare show breakthrough in disease diagnosis and treatment"

        Format:
        1. Hook menarik (1-2 kalimat)
        2. Summary berita (2-3 kalimat)
        3. Call to action
        4. 3-5 relevant hashtags

        Style: Engagement, friendly, shareable
        """

        payload = {
            "model": "glm-4.6",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                caption = result['choices'][0]['message']['content']

                self.log_test(
                    test_name,
                    True,
                    f"Generated caption ({len(caption)} chars): {caption[:100]}...",
                    {"caption": caption, "tokens": result.get("usage", {}).get("total_tokens", 0)}
                )
                return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_image_generation(self):
        """Test image generation API for Instagram visuals"""
        test_name = "Image Generation (Instagram Visuals)"

        prompt = """
        Buat gambar Instagram yang menarik dan profesional:

        Topic: "Teknologi AI untuk Kesehatan"
        Headline: "AI Revolution in Healthcare"
        Style: Modern, clean design, social media optimized (1024x1024)
        Colors: Blue and white color scheme
        Text: Include headline with readable font
        Background: Abstract technology/medical theme
        Layout: Professional, minimalist, Instagram-ready
        """

        payload = {
            "model": "cogview-4",
            "prompt": prompt,
            "size": "1024x1024",
            "quality": "hd",
            "n": 1
        }

        try:
            response = requests.post(
                f"{self.base_url}/images/generations",
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                image_url = result['data'][0]['url']

                # Test if image URL is accessible
                img_response = requests.head(image_url, timeout=10)
                img_accessible = img_response.status_code == 200

                self.log_test(
                    test_name,
                    img_accessible,
                    f"Generated image: {image_url} (Accessible: {img_accessible})",
                    {"image_url": image_url, "accessible": img_accessible}
                )
                return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_web_search(self):
        """Test web search API for news discovery"""
        test_name = "Web Search (News Discovery)"

        payload = {
            "query": "berita teknologi terbaru Indonesia",
            "time_filter": "oneDay",
            "max_results": 10
        }

        try:
            response = requests.post(
                f"{self.base_url}/tools/web-search",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])

                self.log_test(
                    test_name,
                    len(results) > 0,
                    f"Found {len(results)} news articles",
                    {"result_count": len(results), "sample_results": results[:2]}
                )
                return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_web_reader(self):
        """Test web reader API for content extraction"""
        test_name = "Web Reader (Content Extraction)"

        # Use a known news URL for testing
        test_url = "https://www.detik.com/"

        payload = {
            "url": test_url,
            "format": "markdown"
        }

        try:
            response = requests.post(
                f"{self.base_url}/tools/web-reader",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('content', '')

                self.log_test(
                    test_name,
                    len(content) > 0,
                    f"Extracted {len(content)} characters from {test_url}",
                    {"content_length": len(content), "url": test_url}
                )
                return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_caption_generation_workflow(self):
        """Test complete caption generation workflow"""
        test_name = "Complete Caption Generation Workflow"

        news_content = {
            "title": "Startup Indonesia Raih Pendanaan $10 Juta untuk Pengembangan AI",
            "summary": "Perusahaan teknologi asal Jakarta berhasil mendapatkan investasi dari venture capital Silicon Valley",
            "topic": "startup teknologi",
            "source": "TechNews Indonesia"
        }

        prompt = f"""
        Buat caption Instagram untuk berita ini:

        Judul: {news_content['title']}
        Ringkasan: {news_content['summary']}
        Topik: {news_content['topic']}
        Sumber: {news_content['source']}

        Requirements:
        - Hook yang menarik di awal
        - 3-5 kalimat summary
        - Call to action untuk engagement
        - 3-5 hashtags yang relevan
        - Style: friendly, shareable, engagement-focused
        - Maksimal 200 kata
        """

        payload = {
            "model": "glm-4.6",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 400,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                caption = result['choices'][0]['message']['content']

                # Validate caption quality
                has_hashtag = '#' in caption
                reasonable_length = 50 <= len(caption) <= 1000
                has_call_to_action = any(word in caption.lower() for word in ['komentar', 'bagikan', 'follow', 'like', 'cek'])

                quality_score = sum([has_hashtag, reasonable_length, has_call_to_action])

                self.log_test(
                    test_name,
                    quality_score >= 2,
                    f"Caption generated (Quality: {quality_score}/3, Length: {len(caption)})",
                    {
                        "caption": caption,
                        "has_hashtag": has_hashtag,
                        "reasonable_length": reasonable_length,
                        "has_call_to_action": has_call_to_action,
                        "quality_score": quality_score
                    }
                )
                return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_image_generation_for_instagram(self):
        """Test image generation specifically for Instagram format"""
        test_name = "Instagram-Specific Image Generation"

        test_scenarios = [
            {
                "topic": "teknologi AI",
                "headline": "AI Masa Depan",
                "style": "modern tech, blue gradient, digital aesthetic"
            },
            {
                "topic": "bisnis startup",
                "headline": "Startup Unicorn",
                "style": "corporate, professional, gold and white colors"
            },
            {
                "topic": "kesehatan digital",
                "headline": "Digital Health",
                "style": "medical, clean, green and white colors"
            }
        ]

        successful_images = 0

        for i, scenario in enumerate(test_scenarios, 1):
            prompt = f"""
            Create Instagram post image for:

            Topic: {scenario['topic']}
            Headline: {scenario['headline']}
            Style: {scenario['style']}

            Requirements:
            - Size: 1024x1024 (Instagram square)
            - Quality: HD
            - Text overlay: "{scenario['headline']}"
            - Modern, clean design
            - Social media optimized
            - Readable typography
            - Professional layout
            - Eye-catching colors
            """

            payload = {
                "model": "cogview-4",
                "prompt": prompt,
                "size": "1024x1024",
                "quality": "hd",
                "n": 1
            }

            try:
                response = requests.post(
                    f"{self.base_url}/images/generations",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    image_url = result['data'][0]['url']

                    # Test image accessibility
                    img_response = requests.head(image_url, timeout=10)
                    if img_response.status_code == 200:
                        successful_images += 1

                # Add delay between image generations to avoid rate limiting
                import time
                time.sleep(2)

            except Exception as e:
                print(f"    Error with scenario {i}: {str(e)}")

        success = successful_images >= 2  # At least 2 out of 3 successful
        self.log_test(
            test_name,
            success,
            f"Successfully generated {successful_images}/{len(test_scenarios)} Instagram images",
            {"successful_images": successful_images, "total_scenarios": len(test_scenarios)}
        )
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Z.ai API Test Suite")
        print("=" * 60)

        if not self.api_key:
            print("❌ ZAI_API_KEY not found in environment variables")
            print("Please set up your .env file with your Z.ai API key")
            return False

        print(f"🔑 Using API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
        print()

        # Run all tests
        tests = [
            self.test_chat_completion,
            self.test_image_generation,
            self.test_web_search,
            self.test_web_reader,
            self.test_caption_generation_workflow,
            self.test_image_generation_for_instagram
        ]

        passed = 0
        total = len(tests)

        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")

        # Generate summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("\n🎉 All tests passed! Your Z.ai API is ready for Instagram automation.")
        elif passed >= total * 0.8:
            print("\n✅ Most tests passed. Your Z.ai API is mostly ready.")
        else:
            print("\n⚠️  Several tests failed. Please check your API configuration.")

        # Save test results
        self.save_test_results()

        return passed >= total * 0.8

    def save_test_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zai_api_test_results_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving test results: {str(e)}")

def main():
    """Main function"""
    print("🤖 Z.ai API Testing for Instagram Automation")
    print("This test will verify all Z.ai API capabilities needed for your project")
    print()

    # Initialize test suite
    test_suite = ZAITestSuite()

    try:
        # Run all tests
        success = test_suite.run_all_tests()

        if success:
            print("\n🚀 Your Z.ai API is ready for Instagram automation!")
            print("\nNext steps:")
            print("1. Run: python run_automation.py")
            print("2. Choose your topics")
            print("3. Start creating Instagram content!")
        else:
            print("\n⚠️  Some API features may not work correctly.")
            print("Please check the test results and your API configuration.")

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()