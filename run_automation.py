#!/usr/bin/env python3
"""
Instagram Automation Runner
Main execution script for automated Instagram content creation
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict

from main import InstagramAutomation
from config import config
from instagram_client import InstagramClient

def setup_environment():
    """Setup environment and validate configuration"""
    print("🔧 Setting up environment...")

    # Create necessary directories
    os.makedirs(config.POSTS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)

    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed")
        sys.exit(1)

    print("✅ Environment setup complete")

def get_user_input() -> tuple:
    """Get user input for topics and options"""

    print("\n" + "="*60)
    print("🤖 INSTAGRAM AUTOMATION SYSTEM")
    print("="*60)

    # Topics input
    print("\n📝 Available default topics:")
    for i, topic in enumerate(config.DEFAULT_TOPICS, 1):
        print(f"   {i:2d}. {topic}")

    print(f"\n💡 Enter topics (comma-separated) or choose from default")
    user_input = input("Topics: ").strip()

    if not user_input:
        topics = config.DEFAULT_TOPICS[:3]  # Default to first 3 topics
        print(f"Using default topics: {', '.join(topics)}")
    elif user_input.isdigit():
        # User selected default topics by number
        try:
            index = int(user_input) - 1
            if 0 <= index < len(config.DEFAULT_TOPICS):
                topics = [config.DEFAULT_TOPICS[index]]
                print(f"Selected topic: {topics[0]}")
            else:
                print("Invalid selection, using default topics")
                topics = config.DEFAULT_TOPICS[:3]
        except ValueError:
            topics = config.DEFAULT_TOPICS[:3]
    else:
        # User entered custom topics
        topics = [topic.strip() for topic in user_input.split(',')]

    # Additional options
    print(f"\n⚙️  Configuration options:")
    time_range = input(f"Time range [{config.DEFAULT_TIME_RANGE}]: ").strip() or config.DEFAULT_TIME_RANGE
    max_posts = input(f"Max posts per topic [{config.POSTS_PER_TOPIC}]: ").strip()

    try:
        max_posts = int(max_posts) if max_posts else config.POSTS_PER_TOPIC
    except ValueError:
        max_posts = config.POSTS_PER_TOPIC

    # Post to Instagram directly?
    auto_post = input("Auto-post to Instagram? (y/N): ").strip().lower()
    auto_post = auto_post.startswith('y')

    return topics, time_range, max_posts, auto_post

def process_topics(topics: List[str], time_range: str, max_posts: int, auto_post: bool) -> List[Dict]:
    """Process all topics and create Instagram posts"""

    # Initialize automation system
    print(f"\n🚀 Initializing Instagram automation...")
    automation = InstagramAutomation(config.ZAI_API_KEY)

    # Initialize Instagram client if auto-posting
    instagram_client = None
    if auto_post:
        print("📱 Initializing Instagram client...")
        instagram_client = InstagramClient()

        # Test connection
        if not instagram_client.test_connection():
            print("⚠️  Instagram connection failed, switching to manual mode")
            auto_post = False

    all_posts = []
    total_posts = 0

    try:
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*60}")
            print(f"📰 PROCESSING TOPIC {i}/{len(topics)}: {topic.upper()}")
            print(f"{'='*60}")

            # Process topic
            posts = automation.process_topic(
                topic=topic,
                time_range=time_range,
                max_posts=max_posts
            )

            if not posts:
                print(f"⚠️  No posts created for topic: {topic}")
                continue

            # Auto-post to Instagram if enabled
            if auto_post and instagram_client:
                print(f"\n📱 Auto-posting {len(posts)} posts to Instagram...")
                for j, post in enumerate(posts, 1):
                    print(f"   Posting {j}/{len(posts)}...")

                    # Schedule post for optimal time
                    scheduled_time = datetime.now() + timedelta(hours=j*2)  # Spread posts
                    result = instagram_client.schedule_post(
                        image_url=post.image_url,
                        caption=post.caption,
                        scheduled_time=scheduled_time
                    )

                    if result:
                        total_posts += 1
                        print(f"   ✅ Post {j} scheduled successfully")
                    else:
                        print(f"   ❌ Failed to post {j}")

                    # Add delay between posts
                    if j < len(posts):
                        print(f"   ⏳ Waiting {config.REQUEST_DELAY} seconds...")
                        import time
                        time.sleep(config.REQUEST_DELAY)

            all_posts.extend(posts)

    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

    return all_posts

def generate_summary(posts: List[Dict], auto_post: bool) -> str:
    """Generate summary of created posts"""

    if not posts:
        return "❌ No posts were created"

    topics = list(set([post.topic for post in posts]))

    summary = f"""
{'='*60}
📊 INSTAGRAM AUTOMATION SUMMARY
{'='*60}

🎯 Topics Processed: {len(topics)}
📝 Total Posts Created: {len(posts)}
📈 Average Posts per Topic: {len(posts)/len(topics):.1f}

📱 Posting Mode: {'Auto-Post to Instagram' if auto_post else 'Manual (Saved to File)'}

🏷️  Topics: {', '.join(topics)}

📄 Posts Breakdown:
"""
    topic_counts = {}
    for post in posts:
        topic_counts[post.topic] = topic_counts.get(post.topic, 0) + 1

    for topic, count in topic_counts.items():
        summary += f"   • {topic}: {count} posts\n"

    summary += f"\n⏰ Processing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    summary += f"\n💾 All posts saved to JSON file\n"

    return summary

def save_results(posts: List[Dict], auto_post: bool) -> str:
    """Save posts to file and return filename"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{config.POSTS_OUTPUT_DIR}/instagram_posts_{timestamp}.json"

    posts_data = []
    for post in posts:
        post_dict = {
            "topic": post.topic,
            "image_url": post.image_url,
            "caption": post.caption,
            "hashtags": post.hashtags,
            "scheduled_time": post.scheduled_time.isoformat(),
            "created_at": datetime.now().isoformat(),
            "auto_posted": auto_post
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

def show_next_steps():
    """Show next steps and instructions"""

    print(f"""
{'='*60}
🎉 AUTOMATION COMPLETE!
{'='*60}

📋 NEXT STEPS:

1. 📁 Review Generated Posts:
   • Check the JSON file for all created posts
   • Review image URLs and captions
   • Verify hashtag effectiveness

2. 📱 Instagram Posting:
   • If auto-posted: Check your Instagram account
   • If manual: Use the saved content to post manually
   • Optimal posting times: 8AM, 12PM, 6PM, 8PM

3. 📊 Performance Tracking:
   • Monitor engagement rates
   • Track follower growth
   • Identify best performing topics

4. ⚙️  System Optimization:
   • Adjust topics based on performance
   • Fine-tune caption generation prompts
   • Optimize image generation parameters

💡 TIPS FOR SUCCESS:
   • Post consistently (1-3 times per day)
   • Use trending hashtags
   • Engage with comments quickly
   • Mix content types (news, infographics, trends)
   • Monitor Instagram insights regularly

🔧 CONFIGURATION:
   • Edit .env file for API keys
   • Modify config.py for system settings
   • Add custom topics in config.py

📞 SUPPORT:
   • Check logs directory for error details
   • Review Z.ai API documentation
   • Monitor Instagram API limits

{'='*60}
""")

def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description='Instagram Automation System')
    parser.add_argument('--topics', '-t', help='Comma-separated topics to process')
    parser.add_argument('--time-range', '-tr', default='oneDay', help='Time range for news search')
    parser.add_argument('--max-posts', '-mp', type=int, default=3, help='Maximum posts per topic')
    parser.add_argument('--auto-post', '-ap', action='store_true', help='Auto-post to Instagram')
    parser.add_argument('--config-test', '-ct', action='store_true', help='Test configuration only')

    args = parser.parse_args()

    try:
        # Setup environment
        setup_environment()

        # Configuration test mode
        if args.config_test:
            print("🧪 Testing configuration...")
            instagram_client = InstagramClient()
            instagram_client.test_connection()
            return

        # Get user input or use command line args
        if args.topics:
            topics = [topic.strip() for topic in args.topics.split(',')]
            time_range = args.time_range
            max_posts = args.max_posts
            auto_post = args.auto_post
        else:
            topics, time_range, max_posts, auto_post = get_user_input()

        print(f"\n🎯 Processing: {len(topics)} topics, {max_posts} posts each")
        print(f"📅 Time range: {time_range}")
        print(f"📱 Auto-post: {'Enabled' if auto_post else 'Disabled'}")

        # Process topics and create posts
        posts = process_topics(topics, time_range, max_posts, auto_post)

        if posts:
            # Generate and show summary
            summary = generate_summary(posts, auto_post)
            print(summary)

            # Save results
            filename = save_results(posts, auto_post)

            # Show next steps
            show_next_steps()
        else:
            print("❌ No posts were created. Please check your configuration and try again.")

    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()