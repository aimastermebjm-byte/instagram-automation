#!/usr/bin/env python3
"""
Simple Indonesian News Scraper
Built-in sources without external dependencies
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

class SimpleIndonesianNewsScraper:
    """Simple news scraper for Indonesian websites"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_news(self, topic: str, max_articles: int = 3) -> List[Dict]:
        """Get news from predefined Indonesian sources"""

        print(f"🔍 Mencari berita tentang: {topic}")

        all_articles = []

        # Berita dari Detik.com
        detik_articles = self._scrape_detik(topic, max_articles)
        all_articles.extend(detik_articles)

        # Berita dari Kompas.com
        kompas_articles = self._scrape_kompas(topic, max_articles)
        all_articles.extend(kompas_articles)

        # Berita dari tempo.co
        tempo_articles = self._scrape_tempo(topic, max_articles)
        all_articles.extend(tempo_articles)

        # Generate sample content for testing
        for i, article in enumerate(all_articles[:max_articles]):
            # Generate hashtag dari topic
            topic_words = topic.lower().split()
            hashtags = []
            for word in topic_words:
                hashtags.append(f"#{word}")

            all_articles[i]['hashtags'] = hashtags[:5]  # Max 5 hashtags

        print(f"✅ Berhasil mendapatkan {len(all_articles)} berita")
        return all_articles

    def _scrape_detik(self, topic: str, max_articles: int) -> List[Dict]:
        """Scrape Detik.com for news about topic"""
        try:
            # Simulasi pencarian (tanpa real scraping)
            sample_articles = [
                {
                    'title': f'Berita Terbaru {topic}: Update Terkini dari Detik',
                    'summary': f'Update terbaru tentang {topic} telah dirilis dengan berbagai perubahan signifikan...',
                    'source': 'detik.com',
                    'url': 'https://www.detik.com',
                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                    'image_url': f'https://via.placeholder.com/300x200/FF5733/000000/FFFFFF?text={topic.replace(" ", "%20")}'
                }
            ]

            return sample_articles[:max_articles]

        except Exception as e:
            print(f"❌ Error scraping Detik: {e}")
            return []

    def _scrape_kompas(self, topic: str, max_articles: int) -> List[Dict]:
        """Scrape Kompas.com for news about topic"""
        try:
            # Simulasi pencarian
            sample_articles = [
                {
                    'title': f'Analisis {topic}: Tren pasar Terkini',
                    'summary': f'Berbagai analis pasar, {topic} menunjukkan adanya perubahan signifikan dalam perilaku konsumen...',
                    'source': 'kompas.com',
                    'url': 'https://www.kompas.com',
                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                    'image_url': f'https://via.placeholder.com/300x200/4CAF50/000000/FFFFFF?text={topic.replace(" ", "%20")}'
                }
            ]

            return sample_articles[:max_articles]

        except Exception as e:
            print(f"❌ Error scraping Kompas: {e}")
            return []

    def _scrape_tempo(self, topic: str, max_articles: int) -> List[Dict]:
        """Scrape Tempo.co for news about topic"""
        try:
            # Simulasi pencarian
            sample_articles = [
                {
                    'title': f'{topic} Hari Ini: Apa yang Baru?',
                    'summary': f'Analisis mendalam menunjukkan bahwa {topic} memiliki potensi pertumbuhan yang signifikan namun perlu perhatian...',
                    'source': 'tempo.co',
                    'url': 'https://www.tempo.co',
                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                    'image_url': f'https://via.placeholder.com/300x200/FF9800/000000/FFFFFF?text={topic.replace(" ", "%20")}'
                }
            ]

            return sample_articles[:max_articles]

        except Exception as e:
            print(f"❌ Error scraping Tempo: {e}")
            return []

def main():
    """Test the simple scraper"""
    scraper = SimpleIndonesianNewsScraper()

    # Test dengan berbagai topik
    topics = ["teknologi", "bisnis", "olahraga", "kesehatan"]

    for topic in topics:
        print(f"\n" + "="*50)
        print(f"📰 Scraping berita: {topic}")
        articles = scraper.get_news(topic, max_articles=2)

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   📰 Sumber: {article['source']}")
            print(f"   🔗 Link: {article['url']}")
            print(f"   📝 Ringkasan: {article['summary'][:100]}...")
            print(f"   🏷️ Image: {article['image_url']}")
            if article['hashtags']:
                print(f"   📝 Hashtags: {', '.join(article['hashtags'][:3])}")
            print(f"   📅 Tanggal: {article['publish_date']}")

if __name__ == "__main__":
    main()