const express = require('express');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Static files
app.use(express.static(path.join(__dirname, '../')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Z.ai API Configuration
const ZAI_API_KEY = process.env.ZAI_API_KEY;
const ZAI_BASE_URL = 'https://api.z.ai/api/paas/v4';

if (!ZAI_API_KEY) {
    console.log('⚠️  ZAI_API_KEY not found in environment variables');
}

// Z.ai API Client
class ZAIClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = ZAI_BASE_URL;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async chatCompletion(prompt, model = 'glm-4.6', maxTokens = 500) {
        try {
            const response = await axios.post(`${this.baseURL}/chat/completions`, {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
                max_tokens: maxTokens,
                stream: false
            }, {
                headers: this.headers,
                timeout: 30000
            });

            return response.data.choices[0].message.content;
        } catch (error) {
            console.error('Chat completion error:', error.response?.data || error.message);
            throw error;
        }
    }

    async generateImage(prompt, size = '1024x1024', quality = 'hd') {
        try {
            const response = await axios.post(`${this.baseURL}/images/generations`, {
                model: 'cogview-4',
                prompt: prompt,
                size: size,
                quality: quality,
                n: 1
            }, {
                headers: this.headers,
                timeout: 60000
            });

            return response.data.data[0].url;
        } catch (error) {
            console.error('Image generation error:', error.response?.data || error.message);
            throw error;
        }
    }

    async webSearch(query, timeFilter = 'oneDay', maxResults = 10) {
        try {
            const response = await axios.post(`${this.baseURL}/tools/web-search`, {
                query: query,
                time_filter: timeFilter,
                max_results: maxResults
            }, {
                headers: this.headers,
                timeout: 30000
            });

            return response.data.results || [];
        } catch (error) {
            console.error('Web search error:', error.response?.data || error.message);
            throw error;
        }
    }

    async webReader(url, format = 'markdown') {
        try {
            const response = await axios.post(`${this.baseURL}/tools/web-reader`, {
                url: url,
                format: format
            }, {
                headers: this.headers,
                timeout: 30000
            });

            return response.data.content || '';
        } catch (error) {
            console.error('Web reader error:', error.response?.data || error.message);
            throw error;
        }
    }
}

// Initialize Z.ai client
const zaiClient = new ZAIClient(ZAI_API_KEY);

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../index.html'));
});

// Test API connection
app.post('/api/test', async (req, res) => {
    try {
        if (!ZAI_API_KEY) {
            return res.status(400).json({ success: false, error: 'ZAI_API_KEY not configured' });
        }

        const testResponse = await zaiClient.chatCompletion('Test connection', 'glm-4.6', 10);

        res.json({
            success: true,
            message: 'API connection successful',
            testResponse: testResponse.substring(0, 100)
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.response?.data?.error?.message || error.message
        });
    }
});

// Generate content from URL
app.post('/api/generate', async (req, res) => {
    try {
        const { topic, url } = req.body;

        if (!topic || !url) {
            return res.status(400).json({
                success: false,
                error: 'Both topic and URL are required'
            });
        }

        if (!ZAI_API_KEY) {
            return res.status(400).json({
                success: false,
                error: 'ZAI_API_KEY not configured'
            });
        }

        console.log(`🚀 Processing: ${topic} from ${url}`);

        // Step 1: Extract content from URL
        const content = await zaiClient.webReader(url);
        if (!content || content.length < 100) {
            return res.status(400).json({
                success: false,
                error: 'Failed to extract sufficient content from URL'
            });
        }

        // Step 2: Generate news summary
        const summaryPrompt = `
        Buat ringkasan berita yang informatif dari konten berikut:

        Topik: ${topic}
        Konten: ${content.substring(0, 2000)}...

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
        `;

        const newsSummary = await zaiClient.chatCompletion(summaryPrompt, 'glm-4.6', 300);

        // Step 3: Generate Instagram caption
        const captionPrompt = `
        Buat caption Instagram yang engagement dan menarik untuk berita ini:

        Topik: ${topic}
        Ringkasan Berita: ${newsSummary}

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
        `;

        const generatedCaption = await zaiClient.chatCompletion(captionPrompt, 'glm-4.6', 400);

        // Step 4: Generate Instagram image
        const imagePrompt = `
        Create a professional, modern Instagram post image about:

        Topic: ${topic}
        News Summary: ${newsSummary.substring(0, 200)}...

        Style Requirements:
        - Instagram square format (1024x1024)
        - Modern, clean design
        - Professional typography
        - Eye-catching but readable
        - Social media optimized

        Text Overlay:
        - Include a headline related to: "${topic}"
        - Bold, readable font
        - Good contrast with background

        Visual Elements:
        - Background theme relevant to: ${topic}
        - Professional color scheme
        - Clean, minimalist aesthetic
        - High quality, social media ready

        Style: Modern corporate, digital, technology-focused if applicable
        `;

        const generatedImage = await zaiClient.generateImage(imagePrompt, '1024x1024', 'hd');

        // Step 5: Extract hashtags
        const hashtags = (generatedCaption.match(/#\w+/g) || []);

        // Step 6: Create result object
        const result = {
            topic: topic,
            originalUrl: url,
            newsSummary: newsSummary,
            generatedCaption: generatedCaption,
            generatedImageUrl: generatedImage,
            hashtags: hashtags,
            createdAt: new Date().toISOString()
        };

        // Step 7: Save to file
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `generated_content_${timestamp}.json`;

        await fs.writeFile(
            path.join(__dirname, filename),
            JSON.stringify(result, null, 2)
        );

        console.log(`✅ Content generated successfully!`);

        res.json({
            success: true,
            content: result,
            filename: filename
        });

    } catch (error) {
        console.error('Generate error:', error);
        res.status(500).json({
            success: false,
            error: error.response?.data?.error?.message || error.message
        });
    }
});

// Get available topics
app.get('/api/topics', (req, res) => {
    const defaultTopics = [
        "teknologi",
        "bisnis",
        "kesehatan",
        "olahraga",
        "hiburan",
        "politik",
        "sains",
        "travel",
        "kuliner",
        "fashion"
    ];

    res.json({
        success: true,
        default_topics: defaultTopics,
        indonesian_news_domains: [
            "detik.com",
            "kompas.com",
            "tempo.co",
            "cnnindonesia.com",
            "liputan6.com",
            "tribunnews.com",
            "sindonews.com",
            "viva.co.id",
            "merdeka.com",
            "okezone.com",
            "suara.com",
            "antaranews.com",
            "republika.co.id",
            "mediaindonesia.com",
            "jawapos.com"
        ]
    });
});

// Setup API key
app.post('/api/setup', async (req, res) => {
    try {
        const { api_key } = req.body;

        if (!api_key) {
            return res.status(400).json({
                success: false,
                error: 'API key is required'
            });
        }

        // Test the API key
        const testClient = new ZAIClient(api_key);
        const testResult = await testClient.chatCompletion('Test connection', 'glm-4.6', 10);

        if (testResult && testResult.length > 0) {
            res.json({
                success: true,
                message: 'API key validated successfully'
            });
        } else {
            res.status(400).json({
                success: false,
                error: 'Invalid API key - no response from Z.ai'
            });
        }

    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.response?.data?.error?.message || error.message
        });
    }
});

// Get history
app.get('/api/history', async (req, res) => {
    try {
        const files = await fs.readdir(__dirname);
        const jsonFiles = files.filter(file => file.startsWith('generated_content_') && file.endsWith('.json'));

        const history = [];
        for (const file of jsonFiles.sort().reverse().slice(0, 10)) {
            try {
                const content = await fs.readFile(path.join(__dirname, file), 'utf8');
                const data = JSON.parse(content);
                history.push({
                    filename: file,
                    topic: data.topic,
                    createdAt: data.createdAt,
                    hasImage: !!data.generatedImageUrl
                });
            } catch (err) {
                console.error(`Error reading ${file}:`, err.message);
            }
        }

        res.json({ success: true, history });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Download generated file
app.get('/api/download/:filename', async (req, res) => {
    try {
        const { filename } = req.params;
        const filePath = path.join(__dirname, filename);

        const content = await fs.readFile(filePath, 'utf8');
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.send(content);
    } catch (error) {
        res.status(404).json({ success: false, error: 'File not found' });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Instagram Automation Backend Started`);
    console.log(`🌐 Server running on http://localhost:${PORT}`);
    console.log(`🔑 Z.ai API Key: ${ZAI_API_KEY ? 'Configured' : 'Not configured'}`);
    console.log(`📱 Ready to generate Instagram content!`);
    console.log(`🛑 Press Ctrl+C to stop`);
});

module.exports = app;