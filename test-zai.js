const fetch = require('node-fetch');

async function testZaiAPI() {
    const apiKey = 'YOUR_ZAI_API_KEY'; // You'll need to replace this with your actual API key

    console.log('🧪 Testing Z.ai API...\n');

    // Test 1: URL Scraping
    console.log('1️⃣ Testing URL scraping...');
    try {
        const scrapeResponse = await fetch('https://api.z.ai/api/paas/v4/reader', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: 'https://www.detik.com/berita/d-7424008/tes',
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

        if (scrapeResponse.ok) {
            const scrapeData = await scrapeResponse.json();
            console.log('✅ URL scraping successful');
            console.log('📄 Content preview:', scrapeData.data?.content?.substring(0, 200) + '...');
            console.log('📊 Full response keys:', Object.keys(scrapeData));
        } else {
            const errorText = await scrapeResponse.text();
            console.log('❌ URL scraping failed:', scrapeResponse.status, errorText);
        }
    } catch (error) {
        console.log('❌ URL scraping error:', error.message);
    }

    // Test 2: Content Generation
    console.log('\n2️⃣ Testing content generation...');
    try {
        const contentResponse = await fetch('https://api.z.ai/api/paas/v4/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'Instagram-Automation/1.0'
            },
            body: JSON.stringify({
                model: "glm-4.6",
                messages: [{
                    role: "system",
                    content: `You are an expert Instagram content creator specializing in viral news content.

Create a comprehensive Instagram post about this news. Return a JSON object with:
- caption: Engaging caption (150-200 words)
- hashtags: 15-20 relevant hashtags
- image_prompt: Detailed image description for AI image generation

Format: {"caption": "...", "hashtags": "...", "image_prompt": "..."}`
                }, {
                    role: "user",
                    content: "Test news content about technology"
                }]
            })
        });

        if (contentResponse.ok) {
            const contentData = await contentResponse.json();
            console.log('✅ Content generation successful');
            console.log('📝 Generated content preview:', JSON.stringify(contentData.choices?.[0]?.message?.content).substring(0, 200) + '...');
        } else {
            const errorText = await contentResponse.text();
            console.log('❌ Content generation failed:', contentResponse.status, errorText);
        }
    } catch (error) {
        console.log('❌ Content generation error:', error.message);
    }

    // Test 3: Image Generation
    console.log('\n3️⃣ Testing image generation...');
    try {
        const imageResponse = await fetch('https://api.z.ai/api/paas/v4/images/generations', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: "cogview-4-250304",
                prompt: "Test image of modern technology, digital style, blue and purple colors",
                n: 1
            })
        });

        if (imageResponse.ok) {
            const imageData = await imageResponse.json();
            console.log('✅ Image generation successful');
            console.log('🖼️ Image response keys:', Object.keys(imageData));
            if (imageData.data && imageData.data.length > 0) {
                console.log('📸 Generated image URL:', imageData.data[0].url ? 'Available' : 'Not available');
            }
        } else {
            const errorText = await imageResponse.text();
            console.log('❌ Image generation failed:', imageResponse.status, errorText);
        }
    } catch (error) {
        console.log('❌ Image generation error:', error.message);
    }
}

if (require.main === module) {
    testZaiAPI();
}

module.exports = testZaiAPI;