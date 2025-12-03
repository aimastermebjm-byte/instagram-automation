#!/usr/bin/env python3
"""
Instagram News Scraper - Real Implementation
Mengambil berita dari website Indonesia untuk Instagram content
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional
from config_scraper import INDONESIAN_NEWS_SOURCES, INSTAGRAM_CATEGORIES, SCRAPING_SETTINGS

class IndonesianNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPING_SETTINGS['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.scraped_articles = []

    def scrape_news_from_source(self, source_key: str, max_articles: int = None) -> List[Dict]:
        """Scrape news from a specific source"""
        source_config = INDONESIAN_NEWS_SOURCES.get(source_key)
        if not source_config:
            print(f"❌ Sumber {source_key} tidak ditemukan")
            return []

        print(f"🔍 Mengambil berita dari {source_config['name']}...")

        try:
            response = self.session.get(
                source_config['url'],
                timeout=SCRAPING_SETTINGS['timeout']
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Find articles based on selector
            article_elements = soup.select(source_config['selector'])

            if not article_elements:
                print(f"⚠️ Tidak ada artikel ditemukan di {source_config['name']}")
                return []

            max_articles = max_articles or SCRAPING_SETTINGS['max_articles_per_source']

            for i, article in enumerate(article_elements[:max_articles]):
                try:
                    # Extract title
                    title_elem = article.select_one(source_config['title_selector'])
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    # Extract link
                    link_elem = article.select_one(source_config['link_selector'])
                    link = link_elem.get('href') if link_elem else ""

                    # Make absolute URL
                    if link:
                        link = urljoin(source_config['url'], link)

                    # Extract summary/description if available
                    summary_elem = article.select_one('p, .summary, .desc')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""

                    # Extract image if available
                    img_elem = article.select_one('img')
                    image_url = img_elem.get('src') if img_elem else ""
                    if image_url:
                        image_url = urljoin(source_config['url'], image_url)

                    # Extract publication date if available
                    date_elem = article.select_one('time, .date, .published')
                    pub_date = date_elem.get('datetime') or date_elem.get('content') if date_elem else ""

                    if title and link:
                        article_data = {
                            'title': title,
                            'link': link,
                            'summary': summary,
                            'image_url': image_url,
                            'source': source_config['name'],
                            'category': source_config['category'],
                            'publish_date': pub_date,
                            'scraped_at': datetime.now().isoformat(),
                            'source_key': source_key
                        }
                        articles.append(article_data)

                except Exception as e:
                    print(f"⚠️ Error parsing article {i+1} from {source_config['name']}: {e}")
                    continue

            print(f"✅ Berhasil mengambil {len(articles)} artikel dari {source_config['name']}")

            # Respect rate limiting
            time.sleep(SCRAPING_SETTINGS['request_delay'])

            return articles

        except Exception as e:
            print(f"❌ Error scraping {source_config['name']}: {e}")
            return []

    def categorize_article(self, article: Dict) -> str:
        """Categorize article based on keywords"""
        title_lower = article['title'].lower()
        summary_lower = article['summary'].lower()
        content = f"{title_lower} {summary_lower}"

        # Score for each category
        category_scores = {}

        for category, config in INSTAGRAM_CATEGORIES.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in content:
                    score += content.count(keyword)
            category_scores[category] = score

        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category

        return 'umum'  # Default category

    def generate_instagram_content(self, article: Dict) -> Dict:
        """Generate Instagram-ready content from article"""
        category = self.categorize_article(article)
        category_config = INSTAGRAM_CATEGORIES.get(category, INSTAGRAM_CATEGORIES['umum'])

        # Create engaging caption
        emoji = category_config.get('emoji', '📰')

        # Extract key information
        title = article['title']
        summary = article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary']

        # Generate caption
        caption_lines = [
            f"{emoji} {title}",
            "",
            f"{summary}",
            "",
            f"📰 Sumber: {article['source']}",
            f"🔗 Baca selengkapnya: {article['link']}"
        ]

        caption = "\n".join(caption_lines)

        # Add hashtags
        hashtags = category_config['hashtags'].copy()
        hashtags.extend([
            f"#{article['source'].lower().replace(' ', '')}",
            "#beritaindonesia",
            "#indonesia",
            "#news"
        ])

        # Limit hashtags
        hashtags = hashtags[:10]  # Max 10 hashtags
        caption += f"\n\n{' '.join(hashtags)}"

        return {
            'caption': caption,
            'image_url': article.get('image_url', ''),
            'category': category,
            'emoji': emoji,
            'hashtags': hashtags,
            'original_article': article
        }

    def scrape_all_sources(self, max_articles_per_source: int = None) -> List[Dict]:
        """Scrape news from all configured sources"""
        all_articles = []

        for source_key in INDONESIAN_NEWS_SOURCES.keys():
            articles = self.scrape_news_from_source(source_key, max_articles_per_source)
            all_articles.extend(articles)

            # Random delay between sources
            time.sleep(random.uniform(1, 3))

        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()

        for article in all_articles:
            title_normalized = re.sub(r'[^\w\s]', '', article['title'].lower())
            if title_normalized not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title_normalized)

        self.scraped_articles = unique_articles
        print(f"✅ Total artikel unik yang di-scrape: {len(unique_articles)}")

        return unique_articles

    def generate_instagram_posts(self, max_posts: int = 10) -> List[Dict]:
        """Generate Instagram-ready posts from scraped articles"""
        if not self.scraped_articles:
            print("❌ Tidak ada artikel yang di-scrape. Jalankan scrape_all_sources() terlebih dahulu.")
            return []

        # Randomly select articles
        selected_articles = random.sample(
            self.scraped_articles,
            min(max_posts, len(self.scraped_articles))
        )

        instagram_posts = []

        for i, article in enumerate(selected_articles):
            print(f"📝 Generate post {i+1}/{len(selected_articles)}: {article['title'][:50]}...")

            post_content = self.generate_instagram_content(article)

            instagram_post = {
                'id': f"post_{i+1}_{int(time.time())}",
                'title': article['title'],
                'caption': post_content['caption'],
                'image_url': post_content['image_url'],
                'category': post_content['category'],
                'emoji': post_content['emoji'],
                'hashtags': post_content['hashtags'],
                'source': article['source'],
                'link': article['link'],
                'created_at': datetime.now().isoformat(),
                'original_article': article
            }

            instagram_posts.append(instagram_post)

        return instagram_posts

    def save_to_json(self, posts: List[Dict], filename: str = 'scraped_posts.json'):
        """Save scraped posts to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            print(f"✅ Berhasil menyimpan {len(posts)} post ke {filename}")
        except Exception as e:
            print(f"❌ Error menyimpan ke {filename}: {e}")

    def load_from_json(self, filename: str = 'scraped_posts.json') -> List[Dict]:
        """Load posts from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                posts = json.load(f)
            print(f"✅ Berhasil memuat {len(posts)} post dari {filename}")
            return posts
        except FileNotFoundError:
            print(f"⚠️ File {filename} tidak ditemukan")
            return []
        except Exception as e:
            print(f"❌ Error memuat dari {filename}: {e}")
            return []

def main():
    """Main function for testing the scraper"""
    scraper = IndonesianNewsScraper()

    print("🚀 Memulai scraping berita Indonesia...")

    # Scrape from all sources (limit for testing)
    articles = scraper.scrape_all_sources(max_articles_per_source=2)

    if articles:
        print(f"📊 Berhasil mengambil {len(articles)} artikel")

        # Generate Instagram posts
        print("📝 Generate konten Instagram...")
        instagram_posts = scraper.generate_instagram_posts(max_posts=5)

        if instagram_posts:
            print(f"✅ Berhasil generate {len(instagram_posts)} post Instagram")

            # Save to JSON
            scraper.save_to_json(instagram_posts)

            # Display sample post
            print("\n📱 Sample Post:")
            sample_post = instagram_posts[0]
            print(f"Judul: {sample_post['title']}")
            print(f"Caption: {sample_post['caption'][:200]}...")
            print(f"Kategori: {sample_post['category']} {sample_post['emoji']}")
        else:
            print("❌ Tidak ada post yang di-generate")
    else:
        print("❌ Tidak ada artikel yang berhasil di-scrape")

if __name__ == "__main__":
    main()