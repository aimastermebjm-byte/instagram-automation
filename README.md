# 🤖 Instagram Automation System

Automated Instagram content creation system powered by Z.ai API that generates news-based posts with engaging captions and custom images.

## ✨ Features

- 🔍 **Automated News Discovery** - Scrape news from Indonesian websites based on topics
- 🤖 **AI-Powered Content Creation** - Generate engaging captions using GLM-4.6
- 🎨 **Custom Image Generation** - Create Instagram-ready images with CogView-4
- 📱 **Instagram Integration** - Auto-post to Instagram using Graph API
- ⏰ **Smart Scheduling** - Optimal posting times for maximum engagement
- 📊 **Content Management** - Track and organize all generated posts

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd instagram_automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# ZAI_API_KEY=your_zai_api_key_here
# INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token (optional)
```

### 3. Run the System

```bash
# Interactive mode
python run_automation.py

# Command line mode
python run_automation.py --topics "teknologi,bisnis" --max-posts 3 --auto-post

# Test configuration
python run_automation.py --config-test
```

## 📋 Requirements

### Required APIs

1. **Z.ai API Key** (Essential)
   - Get from: https://z.ai
   - GLM Coding Plan ($3/month recommended)
   - Provides: Text generation, Image generation, Web search, Web reader

2. **Instagram Business Account** (Optional)
   - Required for auto-posting
   - Get from: https://developers.facebook.com
   - Instagram Graph API permissions needed

### Supported News Sources

- Detik.com
- Kompas.com
- Tempo.co
- CNN Indonesia
- Liputan6.com
- Tribunnews.com
- Sindonews.com
- Viva.co.id
- Merdeka.com
- Okezone.com
- Suara.com
- Antara News
- Republika
- Media Indonesia
- Jawa Pos

## 🎯 Usage Examples

### Basic Usage

```python
from main import InstagramAutomation

# Initialize with Z.ai API key
automation = InstagramAutomation("your_zai_api_key")

# Process a topic
posts = automation.process_topic("teknologi", time_range="oneDay", max_posts=3)

# Generate summary
summary = automation.generate_post_summary(posts)
print(summary)
```

### Command Line Options

```bash
# Process specific topics
python run_automation.py --topics "teknologi,bisnis,kesehatan"

# Set time range and post limits
python run_automation.py --time-range "oneWeek" --max-posts 5

# Auto-post to Instagram
python run_automation.py --auto-post

# Test configuration only
python run_automation.py --config-test
```

## 📁 Project Structure

```
instagram_automation/
├── main.py              # Core automation system
├── run_automation.py    # Main execution script
├── config.py           # Configuration settings
├── instagram_client.py # Instagram API integration
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── README.md          # This file
├── generated_posts/   # Output directory
└── logs/             # Log files directory
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Z.ai API Configuration
ZAI_API_KEY=your_zai_api_key_here

# Instagram API Configuration (Optional)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id
INSTAGRAM_PAGE_ID=your_page_id

# Facebook App Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# System Configuration
DEBUG=false
POSTS_PER_TOPIC=3
DEFAULT_TIME_RANGE=oneDay
ENABLE_SCHEDULING=true

# Rate Limiting
REQUEST_DELAY=2
MAX_RETRIES=3
```

### Configuration Options (config.py)

- `DEFAULT_TOPICS` - Default topics to process
- `INDONESIAN_NEWS_DOMAINS` - Supported news websites
- `OPTIMAL_POSTING_HOURS` - Best times to post on Instagram
- `MAX_HASHTAGS` - Maximum hashtags per post
- `CAPTION_MAX_TOKENS` - Maximum caption length

## 🎨 Content Generation

### Caption Generation

The system uses GLM-4.6 to create engaging captions with:
- **Hook** - Attention-grabbing opening
- **Summary** - News summary in accessible language
- **Call to Action** - Engagement prompts
- **Hashtags** - 3-5 relevant, trending hashtags

### Image Generation

CogView-4 creates Instagram-ready images with:
- **1024x1024 pixels** - Instagram square format
- **Text overlay** - News headlines with readable fonts
- **Modern design** - Professional, social media optimized
- **Topic relevance** - Contextual backgrounds and styling

### Content Workflow

1. **Search News** - Web search for trending topics
2. **Extract Content** - Parse news articles from URLs
3. **Generate Summary** - Create concise news summary
4. **Create Caption** - Generate engaging Instagram caption
5. **Generate Image** - Create custom visual content
6. **Schedule Post** - Optimal posting time calculation
7. **Post to Instagram** - Auto-post or manual scheduling

## 📱 Instagram Integration

### Setup Instagram Business Account

1. **Convert to Business Account** in Instagram settings
2. **Create Facebook App** at developers.facebook.com
3. **Add Instagram Basic Display API**
4. **Get Required Permissions**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`

### Auto-Posting Features

- **Media Container Creation** - Upload images and captions
- **Scheduled Publishing** - Post at optimal times
- **Performance Tracking** - Monitor engagement metrics
- **Error Handling** - Retry failed posts automatically

## 📊 Scheduling & Optimization

### Optimal Posting Times

The system schedules posts at peak engagement times:
- **8:00 AM** - Morning commute
- **12:00 PM** - Lunch break
- **6:00 PM** - After work
- **8:00 PM** - Prime time

### Content Strategy

- **70% News** - Timely, relevant content
- **20% Infographics** - Visual educational content
- **10% Trending Topics** - Viral content and memes

### Performance Optimization

- **Rate Limiting** - Respect API limits
- **Batch Processing** - Efficient API usage
- **Error Recovery** - Automatic retry logic
- **Content Caching** - Reduce redundant API calls

## 🔧 Advanced Usage

### Custom Topics

```python
# Add custom topics
custom_topics = [
    "artificial intelligence",
    "startup Indonesia",
    "cryptocurrency",
    "health technology",
    "digital marketing"
]

posts = automation.process_topic("artificial intelligence", max_posts=5)
```

### Custom Image Prompts

```python
# Modify image generation prompts
def generate_instagram_image(news_content, topic):
    prompt = f"""
    Create a modern, minimalist Instagram post about:
    Title: {news_content.title}
    Topic: {topic}

    Style: Corporate, professional, clean
    Colors: Blue and white color scheme
    Text: Include headline in bold, readable font
    Layout: Social media optimized with clear hierarchy
    """

    return zai_client.generate_image(prompt)
```

### Custom Caption Style

```python
def generate_custom_caption(news_content, topic):
    prompt = f"""
    Create a professional but engaging Instagram caption:

    News: {news_content.title}
    Topic: {topic}

    Format:
    - Strong opening hook
    - 2-3 sentence summary
    - Question for engagement
    - 3-5 industry-specific hashtags
    - Professional but conversational tone
    """

    return zai_client.chat_completion(prompt)
```

## 📈 Analytics & Performance

### Tracking Metrics

- **Engagement Rate** - Likes, comments, shares
- **Reach** - Number of unique viewers
- **Growth Rate** - Follower increase over time
- **Best Performing Topics** - Content analysis
- **Optimal Posting Times** - Time-based performance

### Content Analysis

The system tracks:
- **Topic Performance** - Which topics get most engagement
- **Caption Effectiveness** - Best-performing caption styles
- **Image Engagement** - Most successful visual formats
- **Hashtag Performance** - Most effective hashtags

## 🛠️ Troubleshooting

### Common Issues

1. **Z.ai API Key Error**
   ```
   Solution: Check your API key in .env file
   Get new key from https://z.ai
   ```

2. **Instagram API Not Configured**
   ```
   Solution: Set up Instagram Business Account
   Configure Facebook App with proper permissions
   ```

3. **No News Found**
   ```
   Solution: Try different topics
   Check time range settings
   Verify internet connection
   ```

4. **Image Generation Failed**
   ```
   Solution: Check Z.ai API limits
   Verify prompt content
   Try alternative prompts
   ```

### Debug Mode

```bash
# Enable debug mode in .env
DEBUG=true

# Check logs
tail -f logs/automation.log

# Test individual components
python -c "from main import InstagramAutomation; print('API test passed')"
```

## 🔒 Security & Best Practices

### API Security

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Implement rate limiting** to avoid API blocks
- **Monitor API usage** to prevent overages

### Instagram Guidelines

- **Follow Instagram's API usage policies**
- **Don't spam** - Respect posting limits
- **Create quality content** - Avoid low-quality automation
- **Engage authentically** - Respond to comments

### Content Quality

- **Fact-check** all news content before posting
- **Give credit** to original news sources
- **Add value** - Don't just copy headlines
- **Stay relevant** - Focus on timely, important news

## 🤝 Contributing

### Development Setup

```bash
# Clone the project
git clone <repository-url>
cd instagram_automation

# Install development dependencies
pip install -r requirements.txt

# Create development environment
cp .env.example .env.dev
# Edit .env.dev with your keys

# Run tests
python -m pytest tests/
```

### Adding Features

1. **New Topics** - Add to `config.py`
2. **Custom Prompts** - Modify generation functions
3. **Additional APIs** - Extend client classes
4. **Analytics** - Add performance tracking

## 📞 Support

### Documentation

- **Z.ai API Docs**: https://docs.z.ai
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **Facebook Developers**: https://developers.facebook.com

### Help Resources

- **Check logs** for error details
- **Review configuration** settings
- **Test API connections** with test mode
- **Monitor API limits** and usage

---

**🎉 Happy Instagramming!**

For questions, issues, or suggestions, please check the documentation or create an issue in the project repository.

**Note**: This system is for educational and authorized use only. Please ensure you have proper permissions for any automated Instagram activity and comply with Instagram's terms of service.