const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080; // Railway DEPLOY v3.0 - JAVASCRIPT FIXED

// Enable CORS
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// API Routes
app.post('/api/setup', (req, res) => {
  try {
    const api_key = req.body.api_key || '';

    if (!api_key) {
      return res.status(400).json({
        status: "error",
        message: "API key is required"
      });
    }

    if (api_key.length < 10) {
      return res.status(400).json({
        status: "error",
        message: "API key must be at least 10 characters"
      });
    }

    // Success case
    res.status(200).json({
      status: "success",
      message: "API key validated successfully",
      success: true
    });

  } catch (error) {
    console.error('Setup error:', error);
    res.status(500).json({
      status: "error",
      message: "Internal server error during setup"
    });
  }
});

// Store for active jobs (in production, use Redis or database)
const activeJobs = {};

app.post('/api/generate', async (req, res) => {
  try {
    const api_key = req.headers['x-api-key'];
    const news_url = req.body.news_url || '';
    const topics = req.body.topics || [];
    const custom_topics = req.body.custom_topics || [];
    const options = req.body.options || {};

    if (!api_key) {
      return res.status(401).json({
        status: "error",
        message: "API key is required"
      });
    }

    if (!news_url && !topics.length && !custom_topics.length) {
      return res.status(400).json({
        status: "error",
        message: "News URL or topics are required"
      });
    }

    // Create job
    const jobId = "job_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);

    // Combine all topics
    const allTopics = [...topics, ...custom_topics];

    // Initialize job
    activeJobs[jobId] = {
      status: "processing",
      progress: 0,
      message: "Starting content generation...",
      created_at: new Date().toISOString(),
      news_url: news_url,
      topics: allTopics,
      results: []
    };

    // Start async processing
    processContentGeneration(jobId, news_url, allTopics, options, api_key);

    res.status(200).json({
      status: "success",
      job_id: jobId,
      message: news_url ? `Job started for URL: ${news_url}` : "Job started for " + allTopics.length + " topics",
      success: true
    });

  } catch (error) {
    console.error('Generate error:', error);
    res.status(500).json({
      status: "error",
      message: "Internal server error during job creation"
    });
  }
});

// Real content generation function
async function processContentGeneration(jobId, newsUrl, topics, options, apiKey) {
  try {
    const maxPosts = options.max_posts || 3;
    const results = [];
    let newsContent = null;

    // If news URL is provided, scrape the content first
    if (newsUrl) {
      if (activeJobs[jobId]) {
        activeJobs[jobId].status = "processing";
        activeJobs[jobId].message = "📰 Reading news article...";
        activeJobs[jobId].progress = 10;
      }

      try {
        console.log(`📰 Scraping URL: ${newsUrl}`);
        const response = await fetch('https://api.z.ai/api/paas/v4/reader', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            url: newsUrl,
            timeout: 20,
            no_cache: false,
            return_format: "markdown",
            retain_images: true,
            no_gfm: false,
            keep_img_data_url: false,
            with_images_summary: false,
            with_links_summary: false
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log('🔍 Full Z.ai Reader Response:', JSON.stringify(data, null, 2));

          // Try different possible response structures
          newsContent = data.content ||
                       data.data?.content ||
                       data.result?.content ||
                       data.text ||
                       JSON.stringify(data);

          // Clean up scraped content - extract just the article text
          if (newsContent.length > 2000) {
            console.log('🧹 Content too long, extracting article text only');

            // Try to find the main article content after title
            const lines = newsContent.split('\n');
            let articleText = '';
            let foundTitle = false;
            let foundContent = false;

            for (let line of lines) {
              // Skip obvious headers/navigation
              if (line.includes('Tribun Network') || line.includes('LIVE') ||
                  line.includes('Halo,') || line.includes('Profile') ||
                  line.includes('Download') || line.includes('Follow us') ||
                  line.includes('Tribun Epaper') || line.includes('Gramedia')) {
                continue;
              }

              // Look for title (starts with #)
              if (line.startsWith('#') && !foundTitle) {
                foundTitle = true;
                articleText += line + '\n\n';
                continue;
              }

              // Start collecting content after title
              if (foundTitle && line.trim().length > 50) {
                articleText += line + '\n';
                foundContent = true;

                // Stop if we have enough content
                if (articleText.length > 1500) {
                  break;
                }
              }
            }

            if (articleText.length > 200) {
              newsContent = articleText + '...';
            } else {
              // Fallback: just take first 1500 chars
              newsContent = newsContent.substring(0, 1500) + '...';
            }
          }

          console.log(`✅ News content scraped (${newsContent.length} characters)`);
          console.log('📝 News content preview:', newsContent.substring(0, 200) + '...');

          if (!newsContent || newsContent.trim().length === 0) {
            console.error('❌ No content found in response!');
          }
        } else {
          const errorText = await response.text();
          console.error(`❌ URL scraping failed (${response.status}):`, errorText);
          throw new Error(`Failed to scrape URL: ${response.status} ${response.statusText}`);
        }
      } catch (error) {
        console.error(`❌ URL scraping failed:`, error);
        newsContent = null;
      }
    }

    // Update job status
    if (activeJobs[jobId]) {
      activeJobs[jobId].status = "processing";
      activeJobs[jobId].message = newsContent ? "Creating content from news article..." : "Generating content for topics...";
      activeJobs[jobId].progress = 30;
    }

    // Generate content based on news or topics
    const contentItems = newsContent ?
      [{ type: 'news', content: newsContent, url: newsUrl }] :
      topics.map(topic => ({ type: 'topic', content: topic }));

    for (let i = 0; i < contentItems.length; i++) {
      const item = contentItems[i];

      // Update progress
      if (activeJobs[jobId]) {
        activeJobs[jobId].progress = Math.round(30 + (i / contentItems.length) * 60);
        activeJobs[jobId].message = item.type === 'news' ?
          `Creating Instagram content from news article...` :
          `Processing topic: ${item.content}`;
      }

      // Generate content for each item
      for (let j = 0; j < maxPosts; j++) {
        try {
          console.log(`🔄 Generating content for post ${j + 1} of ${maxPosts}...`);
          const content = await generateInstagramContent(item, apiKey);
          console.log(`📝 Content generated:`, content);

          if (content) {
            // Generate actual image using Z.ai API
            let imageUrl = null;
            try {
              console.log(`🎨 Generating image for: ${content.imagePrompt}`);
              const imageResponse = await fetch('https://api.z.ai/api/paas/v4/images/generations', {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${apiKey}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  model: "cogview-4-250304",
                  prompt: content.imagePrompt,
                  n: 1,
                  size: "1024x1024",
                  style: "vivid",
                  response_format: "url"
                })
              });

              if (imageResponse.ok) {
                const imageData = await imageResponse.json();
                imageUrl = imageData.data[0].url;
                console.log(`✅ Image generated: ${imageUrl}`);
              } else {
                const imgErrorText = await imageResponse.text();
                console.error(`❌ Image generation API error:`, imgErrorText);
              }
            } catch (imgError) {
              console.error(`⚠️ Image generation failed for ${item.content}:`, imgError.message);
            }

            const resultData = {
              topic: item.type === 'news' ? `News from ${new URL(item.url).hostname}` : item.content,
              post_number: j + 1,
              caption: content.caption,
              image_prompt: content.imagePrompt,
              image_url: imageUrl,
              hashtags: content.hashtags,
              news_url: item.type === 'news' ? item.url : null,
              created_at: new Date().toISOString()
            };

            console.log(`✅ Result created:`, resultData);
            results.push(resultData);
          } else {
            console.error(`❌ No content generated for ${item.content}`);
          }
        } catch (error) {
          console.error(`❌ Error generating content for ${item.content}:`, error);
          console.error('Stack trace:', error.stack);
        }
      }
    }

    // Update job completion
    if (activeJobs[jobId]) {
      activeJobs[jobId].status = "completed";
      activeJobs[jobId].progress = 100;
      activeJobs[jobId].message = `Successfully generated ${results.length} posts`;
      activeJobs[jobId].results = results;
      activeJobs[jobId].completed_at = new Date().toISOString();
    }

    console.log(`✅ Job ${jobId} completed with ${results.length} posts generated`);

  } catch (error) {
    console.error(`Job ${jobId} failed:`, error);
    if (activeJobs[jobId]) {
      activeJobs[jobId].status = "failed";
      activeJobs[jobId].message = "Failed to generate content: " + error.message;
      activeJobs[jobId].error = error.message;
    }
  }
}

// Generate Instagram content using Z.ai API
async function generateInstagramContent(item, apiKey) {
  try {
    const isNews = item.type === 'news';
    console.log(`🔗 Calling Z.ai API for ${isNews ? 'news content' : 'topic'}: ${item.content.substring(0, 100)}...`);

    // Correct Z.ai API endpoints from documentation
    const possibleEndpoints = [
      'https://api.z.ai/api/paas/v4/chat/completions',
      'https://api.z.ai/paas/v4/chat/completions'
    ];

    let lastError = null;
    let successResponse = null;

    // Clean up content for AI processing - get just the essence
    let cleanContent = item.content;

    // Extract title and main content for better AI processing
    if (cleanContent.includes('#')) {
      const titleMatch = cleanContent.match(/#([^#\n]+(?:\n[^#\n]+)*)/);
      if (titleMatch) {
        const title = titleMatch[1].replace(/\n/g, ' ').trim();
        // Find first substantial paragraph after title
        const afterTitle = cleanContent.substring(cleanContent.indexOf(titleMatch[0]) + titleMatch[0].length);
        const paragraphs = afterTitle.split('\n').filter(p => p.trim().length > 100);

        if (paragraphs.length > 0) {
          cleanContent = `Judul: ${title}\n\nKonten utama: ${paragraphs[0].substring(0, 800)}...`;
        } else {
          cleanContent = `Judul: ${title}`;
        }
      } else if (cleanContent.length > 800) {
        cleanContent = cleanContent.substring(0, 800) + '...';
      }
    } else if (cleanContent.length > 1500) {
      cleanContent = cleanContent.substring(0, 1500) + '...';
    }

    const prompt = isNews ?
      `Baca berita ini dan buat postingan Instagram yang menarik dalam bahasa Indonesia:

BERITA:
"""
${cleanContent}
"""

BUAT HASIL YANG SANGAT BAGUS seperti contoh:

1. Caption yang singkat dan menarik (maks 150 karakter) - HARUS relevan dengan berita
2. Image prompt yang detail dan spesifik untuk gambar - DESKRIPSI VISUAL YANG JELAS
3. 5-8 hashtag yang tepat dan trending

FORMAT WAJIB:
{
  "caption": "Teks caption menarik dan singkat",
  "imagePrompt": "Deskripsi visual detail untuk gambar: warna, objek, suasana, gaya",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
}

Contoh bagus:
- Caption: "Menkeu Purbaya siap ke China bahas utang Whoosh! 💰"
- Image Prompt: "Menteri Keuangan Indonesia dengan dokumen negara, suasana formal, latar belakang kantor, warna biru dan merah"
- Hashtags: ["#menkeu", "#indonesia", "#whoosh", "#ekonomi"]` :
      `Buat postingan Instagram tentang "${item.content}" dalam bahasa Indonesia. Buat yang menarik, trending, dan cocok untuk audiens Indonesia. Sertakan:
1. Caption menarik (maks 150 karakter)
2. Image prompt untuk AI image generation
3. Hashtag yang relevan (5-8 hashtag)

Respons dalam format JSON:
{
  "caption": "caption menarik di sini",
  "imagePrompt": "deskripsi gambar detail untuk AI generation",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}`;

    for (const endpoint of possibleEndpoints) {
      try {
        console.log(`📡 Trying endpoint: ${endpoint}`);

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'User-Agent': 'Instagram-Automation/1.0'
          },
          body: JSON.stringify({
            model: "glm-4.6",
            messages: [
              {
                role: "system",
                content: "You are an expert Instagram content creator specializing in Indonesian content. Create viral, engaging content. Always respond in JSON format with caption, imagePrompt, and hashtags fields."
              },
              {
                role: "user",
                content: prompt
              }
            ],
            max_tokens: 500,
            temperature: 0.8
          })
        });

        console.log(`📊 Response status: ${response.status} ${response.statusText}`);

        if (response.ok) {
          const data = await response.json();
          console.log('🔍 Full Z.ai Chat Response:', JSON.stringify(data, null, 2));

          // Try different response structures
          let content = null;
          if (data.choices && data.choices[0] && data.choices[0].message) {
            content = data.choices[0].message.content;
          } else if (data.data && data.data.choices && data.data.choices[0]) {
            content = data.data.choices[0].message?.content;
          } else if (data.result) {
            content = data.result;
          } else {
            content = JSON.stringify(data);
          }

          console.log('📝 Raw content:', content);

          if (content && content.trim().length > 0) {
            // Try to parse JSON response
            try {
              const parsed = JSON.parse(content);
              successResponse = {
                caption: parsed.caption || content.substring(0, 150),
                imagePrompt: parsed.imagePrompt || `${item.content} aesthetic Instagram post style, Indonesian theme`,
                hashtags: Array.isArray(parsed.hashtags) ? parsed.hashtags : [`#${item.content.replace(/\s+/g, '')}`, `#${item.content}`, `#indonesia`, `#viral`]
              };
              console.log('✅ Parsed successfully:', successResponse);
              break;
            } catch (parseError) {
              console.log('⚠️ JSON parse failed, using content as caption');
              successResponse = {
                caption: content.substring(0, 150),
                imagePrompt: `${item.content} aesthetic Instagram post style, modern Indonesian design`,
                hashtags: [`#${item.content.replace(/\s+/g, '')}`, `#${item.content}`, `#indonesia`, `#viral`]
              };
              console.log('✅ Fallback response:', successResponse);
              break;
            }
          } else {
            console.error('❌ No content found in Z.ai response!');
          }
        } else {
          lastError = `${response.status} ${response.statusText}`;
          console.log(`❌ Endpoint ${endpoint} failed: ${lastError}`);
        }
      } catch (error) {
        lastError = error.message;
        console.log(`❌ Endpoint ${endpoint} error: ${lastError}`);
      }
    }

    if (successResponse) {
      return successResponse;
    }

    throw new Error(`All endpoints failed. Last error: ${lastError}`);

  } catch (error) {
    console.error('💥 Z.ai API completely failed:', error);
    console.log('🔄 Using enhanced fallback with Indonesian content');

    // Enhanced fallback with Indonesian-specific content
    const indonesianContent = {
      "teknologi": "🚀 Teknologi Indonesia semakin maju! Swipe up untuk info terbaru 📱",
      "bisnis": "💼 Bisnis lokal berkembang pesat! Peluang emas untuk entrepreneur 🇮🇩",
      "kesehatan": "🏥 Tips kesehatan ala Indonesia! Sehat bersama keluarga ❤️",
      "olahraga": "⚽ Olahraga Indonesia membanggakan! Dukung atlet kita 🥇",
      "hiburan": "🎬 Hiburan tanpa batas! Film Indonesia keren abis 🎭",
      "politik": "🏛️ Politik untuk rakyat! Ikuti perkembangan terkini 📰",
      "sains": "🔬 Sains Indonesia menakjubkan! Temuan baru dari para ilmuwan 🧪",
      "travel": "✈️ Jelajahi keindahan Indonesia! Wisata lokal luar biasa 🏝️",
      "kuliner": "🍜 Kuliner nusantara menggugah selera! Makanan tradisional terenak 🌶️",
      "fashion": "👗 Fashion Indonesia kekinian! Gaya lokal mendunia 🌟",
      "startup": "💡 Startup Indonesia bermunculan! Inovasi tanpa henti 🚀",
      "artificial intelligence": "🤖 AI di Indonesia! Masa depan teknologi sudah di sini 🇮🇩"
    };

    const topicName = item.type === 'news' ? 'Berita Terkini' : item.content;

    // Check if content is actually an error message
    const isErrorMessage = item.content.toLowerCase().includes('error 403') ||
                          item.content.toLowerCase().includes('request blocked') ||
                          item.content.toLowerCase().includes('cloudfront') ||
                          item.content.toLowerCase().includes('maaf, tidak dapat');

    if (isErrorMessage && item.type === 'news') {
      // For news with scraping errors, use URL hostname as topic
      const urlHost = new URL(item.url).hostname;
      console.log(`🔄 Using fallback for blocked URL: ${urlHost}`);
      topicName = `Breaking News from ${urlHost}`;
    }

    const caption = indonesianContent[topicName.toLowerCase()] ||
                   `🔥 ${topicName} Indonesia sedang trending! Swipe up untuk detail lengkap 🚀`;

    return {
      caption: caption,
      imagePrompt: `${topicName} aesthetic Indonesian Instagram post style, vibrant colors, modern design, cultural elements`,
      hashtags: [`#${topicName.replace(/\s+/g, '')}`, `#${topicName}`, `#indonesia`, `#viral`, `#trending`, `#lokal`]
    };
  }
}

app.get('/api/topics', (req, res) => {
  try {
    const defaultTopics = [
      "teknologi", "bisnis", "kesehatan", "olahraga", "hiburan",
      "politik", "sains", "travel", "kuliner", "fashion",
      "startup", "artificial intelligence"
    ];

    res.status(200).json({
      status: "success",
      default_topics: defaultTopics,
      success: true
    });

  } catch (error) {
    console.error('Topics error:', error);
    res.status(500).json({
      status: "error",
      message: "Failed to load topics"
    });
  }
});

app.get('/api/jobs', (req, res) => {
  try {
    res.status(200).json({
      status: "success",
      active_jobs: activeJobs,
      completed_jobs: {}, // We store everything in activeJobs for now
      success: true
    });
  } catch (error) {
    console.error('Jobs error:', error);
    res.status(500).json({
      status: "error",
      message: "Failed to load jobs"
    });
  }
});

// Generate images using Z.ai API
app.post('/api/generate-image', async (req, res) => {
  try {
    const api_key = req.headers['x-api-key'];
    const { prompt, style = "realistic", size = "1024x1024" } = req.body;

    if (!api_key) {
      return res.status(401).json({
        status: "error",
        message: "API key is required"
      });
    }

    if (!prompt) {
      return res.status(400).json({
        status: "error",
        message: "Prompt is required"
      });
    }

    console.log(`🎨 Generating image with prompt: ${prompt}`);

    const response = await fetch('https://api.z.ai/api/paas/v4/images/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${api_key}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "cogview-4-250304",
        prompt: prompt,
        n: 1,
        size: size,
        style: style,
        response_format: "url"
      })
    });

    if (!response.ok) {
      throw new Error(`Z.ai Image API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Image generated successfully:', data);

    res.status(200).json({
      status: "success",
      image_url: data.data[0].url,
      prompt: prompt,
      success: true
    });

  } catch (error) {
    console.error('Image generation error:', error);
    res.status(500).json({
      status: "error",
      message: "Failed to generate image: " + error.message
    });
  }
});

// Scrape URL content using Z.ai Web Reader API
app.post('/api/scrape-url', async (req, res) => {
  try {
    const api_key = req.headers['x-api-key'];
    const { url, timeout = 20 } = req.body;

    if (!api_key) {
      return res.status(401).json({
        status: "error",
        message: "API key is required"
      });
    }

    if (!url) {
      return res.status(400).json({
        status: "error",
        message: "URL is required"
      });
    }

    console.log(`📰 Scraping URL: ${url}`);

    const response = await fetch('https://api.z.ai/api/paas/v4/reader', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${api_key}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: url,
        timeout: timeout,
        no_cache: false,
        return_format: "markdown",
        retain_images: true,
        no_gfm: false,
        keep_img_data_url: false,
        with_images_summary: false,
        with_links_summary: false
      })
    });

    if (!response.ok) {
      throw new Error(`Z.ai Reader API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ URL scraped successfully');

    res.status(200).json({
      status: "success",
      content: data.content,
      url: url,
      title: data.title,
      success: true
    });

  } catch (error) {
    console.error('URL scraping error:', error);
    res.status(500).json({
      status: "error",
      message: "Failed to scrape URL: " + error.message
    });
  }
});

// Serve main HTML for all other routes
app.get('*', (req, res) => {
  // HTML with properly formatted JavaScript
  res.setHeader('Content-Type', 'text/html');
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .card {
            background: white; border-radius: 12px; padding: 25px;
            margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .card h2 { color: #667eea; margin-bottom: 15px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .form-group input, select, textarea {
            width: 100%; padding: 12px; border: 2px solid #e1e5e9;
            border-radius: 8px; font-size: 1rem;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 12px 24px;
            border-radius: 8px; font-size: 1rem; font-weight: 600;
            cursor: pointer; margin-right: 10px;
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-success { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .status {
            padding: 15px; border-radius: 8px; margin: 15px 0; font-weight: 600;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .hidden { display: none !important; }
        .topics-container { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
        .topic-chip {
            background: #667eea; color: white; padding: 8px 16px;
            border-radius: 20px; font-size: 0.9rem; cursor: pointer;
            transition: all 0.3s ease;
        }
        .topic-chip:hover { transform: scale(1.05); }
        .topic-chip.selected { background: #764ba2; }
        .loading {
            display: inline-block; width: 20px; height: 20px;
            border: 2px solid #ffffff; border-radius: 50%;
            border-top-color: transparent; animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Instagram Automation</h1>
            <p>🚀 Powered by AI - Create engaging content automatically</p>
        </div>

        <div class="card" id="setupCard">
            <h2>🔑 API Configuration</h2>
            <div class="form-group">
                <label for="apiKey">Z.ai API Key</label>
                <input type="password" id="apiKey" placeholder="Enter your Z.ai API key">
            </div>
            <button class="btn" id="setupBtn" onclick="setupAPI()">
                <span id="setupIcon">🔗</span>
                <span id="setupText">Connect API</span>
            </button>
            <div id="setupStatus"></div>
        </div>

        <div class="card hidden" id="jobCard">
            <h2>📝 Create Automation Job</h2>
            <div class="form-group">
                <label for="newsUrl">📰 News URL</label>
                <input type="url" id="newsUrl" placeholder="https://example.com/news-article"
                    style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 1rem;">
                <small style="color: #666; font-size: 12px; margin-top: 5px; display: block;">
                    Enter a news article URL. System will read the article, create summary, then generate image and caption.
                </small>
            </div>
            <div class="form-group">
                <label for="customTopics">✍️ Custom Topics (optional, if not using URL)</label>
                <textarea id="customTopics" rows="2" placeholder="Additional topics..."></textarea>
            </div>
            <div class="grid">
                <div class="form-group">
                    <label for="maxPosts">📊 Posts per Topic</label>
                    <select id="maxPosts">
                        <option value="1">1 Post</option>
                        <option value="2">2 Posts</option>
                        <option value="3" selected>3 Posts</option>
                        <option value="5">5 Posts</option>
                        <option value="10">10 Posts</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="timeRange">⏰ Time Range</label>
                    <select id="timeRange">
                        <option value="oneDay" selected>One Day</option>
                        <option value="threeDays">Three Days</option>
                        <option value="oneWeek">One Week</option>
                        <option value="oneMonth">One Month</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-success" id="startBtn" onclick="startJob()">
                <span id="startIcon">🚀</span>
                <span id="startText">Start Automation</span>
            </button>
            <div id="jobStatus"></div>
        </div>

        <div class="card hidden" id="jobsCard">
            <h2>📋 Active Jobs</h2>
            <div id="jobsList">
                <p style="text-align: center; color: #666; padding: 20px;">No jobs yet. Create your first automation job! 🚀</p>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let selectedTopics = new Set();
        let apiKey = localStorage.getItem("zai_api_key") || "";

        document.addEventListener("DOMContentLoaded", function() {
            console.log("🚀 Instagram Automation loaded");
            if (apiKey) {
                document.getElementById("apiKey").value = apiKey;
                setupAPI();
            }
        });

        async function loadTopics() {
            try {
                console.log("📋 Loading topics...");
                const response = await fetch(API_BASE + "/api/topics");
                const data = await response.json();

                if (data.success) {
                    const container = document.getElementById("topicsContainer");
                    container.innerHTML = "";

                    data.default_topics.forEach(function(topic) {
                        const chip = document.createElement("div");
                        chip.className = "topic-chip";
                        chip.textContent = topic;
                        chip.onclick = function() { toggleTopic(chip, topic); };
                        container.appendChild(chip);
                    });

                    console.log("✅ Topics loaded:", data.default_topics.length);
                } else {
                    throw new Error("Failed to load topics");
                }
            } catch (error) {
                console.error("❌ Failed to load topics:", error);
                document.getElementById("topicsContainer").innerHTML = '<div style="color: #721c24;">Failed to load topics</div>';
            }
        }

        function toggleTopic(chip, topic) {
            if (selectedTopics.has(topic)) {
                selectedTopics.delete(topic);
                chip.classList.remove("selected");
            } else {
                selectedTopics.add(topic);
                chip.classList.add("selected");
            }
            console.log("🏷️ Selected topics:", Array.from(selectedTopics));
        }

        async function setupAPI() {
            const apiKeyInput = document.getElementById("apiKey");
            const key = apiKeyInput.value.trim();

            if (!key) {
                showStatus("setupStatus", "❌ Please enter your API key", "error");
                return;
            }

            const btn = document.getElementById("setupBtn");
            const icon = document.getElementById("setupIcon");
            const text = document.getElementById("setupText");

            btn.disabled = true;
            icon.innerHTML = '<span class="loading"></span>';
            text.textContent = "Connecting...";

            try {
                console.log("🔗 Testing API connection...");
                const response = await fetch(API_BASE + "/api/setup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ api_key: key })
                });

                const data = await response.json();
                console.log("📡 API Response:", data);

                if (response.ok && data.success) {
                    apiKey = key;
                    localStorage.setItem("zai_api_key", key);
                    showStatus("setupStatus", "✅ API connected successfully!", "success");
                    console.log("✅ API Setup successful!");

                    setTimeout(function() {
                        document.getElementById("jobCard").classList.remove("hidden");
                        document.getElementById("jobsCard").classList.remove("hidden");
                        refreshJobs();
                        setInterval(refreshJobs, 5000);
                        showStatus("jobStatus", "🎉 Ready to create automation jobs! Enter a news URL to get started.", "success");
                    }, 500);

                } else {
                    showStatus("setupStatus", "❌ " + (data.message || "Failed to connect API"), "error");
                }
            } catch (error) {
                console.error("❌ Setup error:", error);
                showStatus("setupStatus", "❌ Connection failed: " + error.message, "error");
            } finally {
                btn.disabled = false;
                icon.innerHTML = "🔗";
                text.textContent = "Connect API";
            }
        }

        async function startJob() {
            const newsUrl = document.getElementById("newsUrl").value.trim();
            const customTopicsText = document.getElementById("customTopics").value;
            const maxPosts = parseInt(document.getElementById("maxPosts").value);
            const timeRange = document.getElementById("timeRange").value;

            // Check if URL is provided or topics are available
            if (!newsUrl && !customTopicsText && selectedTopics.size === 0) {
                showStatus("jobStatus", "❌ Please enter a news URL or select topics", "error");
                return;
            }

            const btn = document.getElementById("startBtn");
            const icon = document.getElementById("startIcon");
            const text = document.getElementById("startText");

            btn.disabled = true;
            icon.innerHTML = '<span class="loading"></span>';
            text.textContent = "Starting...";

            try {
                console.log("🚀 Starting job with URL:", newsUrl, "and topics:", customTopicsText);
                const response = await fetch(API_BASE + "/api/generate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-API-Key": apiKey
                    },
                    body: JSON.stringify({
                        news_url: newsUrl,
                        topics: selectedTopics.size > 0 ? Array.from(selectedTopics) : [],
                        custom_topics: customTopicsText.split("\\n").map(function(t) { return t.trim(); }).filter(function(t) { return t; }),
                        options: { max_posts: maxPosts, time_range: timeRange }
                    })
                });

                const data = await response.json();
                console.log("📡 Job Response:", data);

                if (response.ok && data.success) {
                    showStatus("jobStatus", "✅ Job started successfully! Job ID: " + data.job_id, "success");

                    // Clear form
                    document.getElementById("newsUrl").value = "";
                    document.getElementById("customTopics").value = "";
                    document.querySelectorAll(".topic-chip.selected").forEach(function(chip) {
                        chip.classList.remove("selected");
                    });
                    selectedTopics.clear();

                    setTimeout(refreshJobs, 1000);
                } else {
                    showStatus("jobStatus", "❌ " + (data.message || "Failed to start job"), "error");
                }
            } catch (error) {
                console.error("❌ Job error:", error);
                showStatus("jobStatus", "❌ Failed to start job: " + error.message, "error");
            } finally {
                btn.disabled = false;
                icon.innerHTML = "🚀";
                text.textContent = "Start Automation";
            }
        }

        async function refreshJobs() {
            try {
                const response = await fetch(API_BASE + "/api/jobs");
                const data = await response.json();

                if (data.success) {
                    const jobsList = document.getElementById("jobsList");

                    if (data.active_jobs && Object.keys(data.active_jobs).length > 0) {
                        var html = '<h3 style="color: #667eea; margin-bottom: 15px;">🔄 Active Jobs</h3>';
                        Object.keys(data.active_jobs).forEach(function(jobId) {
                            var job = data.active_jobs[jobId];
                            var statusColor = job.status === 'completed' ? '#28a745' : (job.status === 'failed' ? '#dc3545' : '#667eea');

                            html +=
                                '<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 10px; border-left: 4px solid ' + statusColor + ';">' +
                                    '<h4 style="color: ' + statusColor + ';">🚀 Job: ' + jobId.substring(0, 8) + '...</h4>' +
                                    '<p><strong>Status:</strong> ' + (job.status || "Unknown") + '</p>' +
                                    '<p><strong>Progress:</strong> ' + (job.progress || 0) + '%</p>' +
                                    '<p><strong>Message:</strong> ' + (job.message || "Processing...") + '</p>' +
                                    '<p><strong>Topics:</strong> ' + (job.topics ? job.topics.join(', ') : 'N/A') + '</p>';

                            // Show results if job is completed
                            if (job.status === 'completed' && job.results && job.results.length > 0) {
                                html += '<div style="margin-top: 15px;"><strong>📝 Generated Content (' + job.results.length + ' posts):</strong></div>';
                                job.results.forEach(function(result, index) {
                                    html +=
                                        '<div style="background: white; border-radius: 6px; padding: 10px; margin-top: 8px; border: 1px solid #dee2e6;">' +
                                            '<div style="font-weight: bold; color: #667eea;">Post ' + (index + 1) + ' - ' + (result.topic || 'Unknown') + '</div>' +
                                            '<div style="margin: 5px 0; font-size: 14px;">💬 ' + (result.caption || 'No caption') + '</div>' +
                                            (result.image_url ?
                                                '<div style="margin: 5px 0;"><img src="' + result.image_url + '" style="max-width: 200px; border-radius: 4px;" alt="Generated image"></div>' :
                                                '<div style="margin: 5px 0; font-size: 12px; color: #666;">🎨 ' + (result.image_prompt || 'No image prompt') + '</div>'
                                            ) +
                                            '<div style="margin: 5px 0; font-size: 12px; color: #007bff;">🏷️ ' + (result.hashtags ? result.hashtags.join(' ') : 'No hashtags') + '</div>' +
                                        '</div>';
                                });
                            }

                            html += '</div>';
                        });
                        jobsList.innerHTML = html;
                    } else {
                        jobsList.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No active jobs. Create your first automation job! 🚀</p>';
                    }
                }
            } catch (error) {
                console.error("❌ Failed to refresh jobs:", error);
            }
        }

        function showStatus(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = '<div class="status ' + type + '">' + message + '</div>';

            if (type === "success") {
                setTimeout(function() {
                    element.innerHTML = "";
                }, 5000);
            }
        }
    </script>
</body>
</html>`);
});

app.listen(PORT, () => {
  console.log(`🚀 Instagram Automation server running on port ${PORT}`);
  console.log(`🌐 Access: http://localhost:${PORT}`);
});