#!/usr/bin/env python3
"""
Simple Web Interface for URL-based Instagram Content Generation
Using Z.ai API - Real Content Generation Only
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from url_content_generator import URLContentGenerator, GeneratedContent

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize generator
api_key = os.getenv("ZAI_API_KEY")
if not api_key:
    print("❌ ZAI_API_KEY not found in environment variables!")
    exit(1)

generator = URLContentGenerator(api_key)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Content Generator - Z.ai API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }

        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card h2::before {
            content: "🚀";
            font-size: 1.2em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 600;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .result-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .result-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .result-card h3::before {
            content: "✅";
            font-size: 1.2em;
        }

        .result-section {
            margin-bottom: 20px;
        }

        .result-section h4 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .result-content {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e1e5e9;
            line-height: 1.6;
        }

        .image-preview {
            text-align: center;
            margin: 20px 0;
        }

        .image-preview img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            border: 2px solid #e1e5e9;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .hashtags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }

        .hashtag {
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e1e5e9;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Instagram Content Generator</h1>
            <p>Powered by Z.ai API - Real Content Generation</p>
        </div>

        <div class="card">
            <h2>Generate Instagram Content</h2>

            <div class="form-group">
                <label for="topic">🏷️ Topic</label>
                <select id="topic" required>
                    <option value="">Select a topic...</option>
                    <option value="teknologi">Teknologi</option>
                    <option value="bisnis">Bisnis</option>
                    <option value="kesehatan">Kesehatan</option>
                    <option value="olahraga">Olahraga</option>
                    <option value="hiburan">Hiburan</option>
                    <option value="politik">Politik</option>
                    <option value="sains">Sains</option>
                    <option value="travel">Travel</option>
                    <option value="kuliner">Kuliner</option>
                    <option value="fashion">Fashion</option>
                    <option value="startup">Startup</option>
                    <option value="artificial intelligence">Artificial Intelligence</option>
                    <option value="cryptocurrency">Cryptocurrency</option>
                </select>
            </div>

            <div class="form-group">
                <label for="url">🔗 News URL</label>
                <input type="url" id="url" placeholder="https://example.com/news-article" required>
            </div>

            <button class="btn" onclick="generateContent()">
                <span id="btnIcon">🚀</span>
                <span id="btnText">Generate Content</span>
            </button>

            <div id="status"></div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        async function generateContent() {
            const topic = document.getElementById('topic').value;
            const url = document.getElementById('url').value;

            if (!topic || !url) {
                showStatus('Please fill in all fields', 'error');
                return;
            }

            const button = document.querySelector('.btn');
            const btnIcon = document.getElementById('btnIcon');
            const btnText = document.getElementById('btnText');

            // Show loading state
            btnIcon.innerHTML = '<span class="loading"></span>';
            btnText.textContent = 'Generating...';
            button.disabled = true;

            // Clear previous results
            document.getElementById('results').innerHTML = '';
            showStatus('Starting content generation...', 'info');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ topic, url })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.success) {
                    showStatus('Content generated successfully!', 'success');
                    displayResults(data.content);
                } else {
                    showStatus(`Error: ${data.error}`, 'error');
                }

            } catch (error) {
                showStatus(`Generation failed: ${error.message}`, 'error');
            } finally {
                // Reset button state
                btnIcon.textContent = '🚀';
                btnText.textContent = 'Generate Content';
                button.disabled = false;
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;

            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }

        function displayResults(content) {
            const resultsDiv = document.getElementById('results');

            resultsDiv.innerHTML = `
                <div class="result-card">
                    <h3>Generated Instagram Content</h3>

                    <div class="result-section">
                        <h4>📰 Topic</h4>
                        <div class="result-content">
                            <strong>${content.topic}</strong><br>
                            <small>Source: ${content.original_url}</small>
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>📝 News Summary</h4>
                        <div class="result-content">
                            ${content.news_summary.replace(/\\n/g, '<br>')}
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>📱 Instagram Caption</h4>
                        <div class="result-content">
                            ${content.generated_caption.replace(/\\n/g, '<br>')}
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>🏷️ Hashtags</h4>
                        <div class="hashtags">
                            ${content.hashtags.map(tag => `<span class="hashtag">${tag}</span>`).join('')}
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>🎨 Generated Image</h4>
                        <div class="image-preview">
                            <img src="${content.generated_image_url}" alt="Generated Instagram image" />
                        </div>
                        <div class="result-content">
                            <strong>Image URL:</strong><br>
                            <a href="${content.generated_image_url}" target="_blank">${content.generated_image_url}</a>
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>📅 Created At</h4>
                        <div class="result-content">
                            ${new Date(content.created_at).toLocaleString()}
                        </div>
                    </div>
                </div>
            `;
        }

        // Initialize with API connection test
        document.addEventListener('DOMContentLoaded', async () => {
            try {
                const response = await fetch('/api/test', {
                    method: 'GET'
                });

                if (response.ok) {
                    showStatus('✅ Z.ai API connected successfully!', 'success');
                } else {
                    showStatus('⚠️ API connection issue - some features may not work', 'error');
                }
            } catch (error) {
                showStatus('❌ Failed to connect to backend', 'error');
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test')
def test_api():
    """Test Z.ai API connection"""
    try:
        if generator.test_api_connection():
            return jsonify({"success": True, "message": "API connection successful"})
        else:
            return jsonify({"success": False, "error": "API connection failed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Generate Instagram content from URL"""
    try:
        data = request.json
        topic = data.get('topic')
        url = data.get('url')

        if not topic or not url:
            return jsonify({
                "success": False,
                "error": "Both topic and URL are required"
            }), 400

        # Generate content
        generated_content = generator.process_url_content(url, topic)

        if not generated_content:
            return jsonify({
                "success": False,
                "error": "Failed to generate content"
            }), 500

        # Convert to dict for JSON response
        content_dict = {
            "topic": generated_content.topic,
            "original_url": generated_content.original_url,
            "news_summary": generated_content.news_summary,
            "generated_caption": generated_content.generated_caption,
            "generated_image_url": generated_content.generated_image_url,
            "hashtags": generated_content.hashtags,
            "created_at": generated_content.created_at
        }

        # Save to file
        filename = generator.save_results_to_file(generated_content)

        return jsonify({
            "success": True,
            "content": content_dict,
            "filename": filename
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/history')
def get_history():
    """Get generation history (list of saved files)"""
    try:
        import glob
        json_files = glob.glob("generated_content_*.json")

        history = []
        for file in sorted(json_files, reverse=True)[:10]:  # Last 10 files
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history.append({
                        "filename": file,
                        "topic": data.get("topic"),
                        "created_at": data.get("created_at"),
                        "has_image": bool(data.get("generated_image_url"))
                    })
            except:
                continue

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Web Interface for Instagram Content Generation")
    print("🔑 Using Z.ai API Key:", api_key[:10] + "..." + api_key[-6:])
    print("🌐 Open http://localhost:5000 in your browser")
    print("🛑 Press Ctrl+C to stop")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )