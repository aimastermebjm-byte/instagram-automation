#!/usr/bin/env python3
"""
Simple Test Script untuk Instagram Automation
Test API key dan basic functionality
"""

import os
import sys
import json
import requests
from datetime import datetime

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup...")

    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded successfully")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

    # Check API key
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment")
        return False

    print(f"✅ ZAI_API_KEY found: {api_key[:10]}...{api_key[-6:]}")
    return True

def test_zai_connection(api_key):
    """Test Z.ai API connection"""
    print("\n🧪 Testing Z.ai API Connection...")

    base_url = "https://api.z.ai/api/paas/v4"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4.6",
        "messages": [{"role": "user", "content": "Hello, test connection"}],
        "max_tokens": 10,
        "temperature": 0.1
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            print(f"✅ API Connection Successful!")
            print(f"📝 Response: {response_text}")
            return True
        else:
            print(f"❌ API Connection Failed: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False

def test_url_extraction():
    """Test URL content extraction"""
    print("\n📖 Testing URL Content Extraction...")

    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("❌ No API key for testing")
        return False

    base_url = "https://api.z.ai/api/paas/v4"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test with a simple URL
    test_url = "https://www.detik.com/"

    payload = {
        "url": test_url,
        "format": "markdown"
    }

    try:
        response = requests.post(
            f"{base_url}/tools/web-reader",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get('content', '')
            if content and len(content) > 100:
                print(f"✅ Content Extraction Successful!")
                print(f"📄 Extracted {len(content)} characters")
                print(f"📝 Content Preview: {content[:200]}...")
                return True
            else:
                print(f"❌ Content too short: {len(content)} characters")
                return False
        else:
            print(f"❌ Content Extraction Failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Content Extraction Error: {e}")
        return False

def test_image_generation():
    """Test image generation"""
    print("\n🎨 Testing Image Generation...")

    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("❌ No API key for testing")
        return False

    base_url = "https://api.z.ai/api/paas/v4"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = """
    Create a simple Instagram post image about "Technology News".
    Style: Modern, clean, professional.
    Size: 1024x1024
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
            f"{base_url}/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            print(f"✅ Image Generation Successful!")
            print(f"🖼️ Image URL: {image_url}")

            # Test if image is accessible
            img_response = requests.head(image_url, timeout=10)
            if img_response.status_code == 200:
                print(f"✅ Image is accessible!")
                return True
            else:
                print(f"❌ Image not accessible: HTTP {img_response.status_code}")
                return False
        else:
            print(f"❌ Image Generation Failed: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Image Generation Error: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 Instagram Automation - Local Test")
    print("=" * 50)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed!")
        return False

    # Get API key
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        print("\n❌ No API key found!")
        return False

    # Run tests
    tests = [
        ("API Connection", lambda: test_zai_connection(api_key)),
        ("URL Content Extraction", test_url_extraction),
        ("Image Generation", test_image_generation)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Your system is ready!")
        print("\n🚀 Next steps:")
        print("1. Run: python simple_web_interface.py")
        print("2. Open: http://localhost:5000")
        print("3. Enter your Z.ai API key")
        print("4. Start creating Instagram content!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return passed == total

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()