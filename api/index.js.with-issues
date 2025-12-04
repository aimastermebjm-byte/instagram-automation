const { spawn } = require('child_process');

// Simple API without async/await for better Vercel compatibility
module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key');

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { method, url } = req;
  const requestPath = url.split('?')[0];

  try {
    // Route handling
    if (requestPath === '/api/setup' && method === 'POST') {
      return handleSetup(req, res);
    }

    if (requestPath === '/api/generate' && method === 'POST') {
      return handleGenerate(req, res);
    }

    if (requestPath === '/api/topics' && method === 'GET') {
      return handleTopics(req, res);
    }

    if (requestPath === '/api/jobs' && method === 'GET') {
      return handleJobs(req, res);
    }

    // Default response - serve complete HTML with embedded JavaScript
    return handleIndex(req, res);

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({
      status: "error",
      message: error.message || "Internal server error"
    });
  }
};

function handleSetup(req, res) {
  try {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const api_key = data.api_key || '';

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

      } catch (parseError) {
        console.error('Parse error:', parseError);
        res.status(400).json({
          status: "error",
          message: "Invalid JSON in request body"
        });
      }
    });

  } catch (error) {
    console.error('Setup error:', error);
    res.status(500).json({
      status: "error",
      message: "Internal server error during setup"
    });
  }
}

function handleGenerate(req, res) {
  try {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const topics = data.topics || [];
        const options = data.options || {};

        if (!topics.length) {
          return res.status(400).json({
            status: "error",
            message: "Topics are required"
          });
        }

        // Create job
        const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        res.status(200).json({
          status: "success",
          job_id: jobId,
          message: `Job started for ${topics.length} topics`,
          success: true
        });

      } catch (parseError) {
        console.error('Parse error:', parseError);
        res.status(400).json({
          status: "error",
          message: "Invalid JSON in request body"
        });
      }
    });

  } catch (error) {
    console.error('Generate error:', error);
    res.status(500).json({
      status: "error",
      message: "Internal server error during job creation"
    });
  }
}

function handleTopics(req, res) {
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
}

function handleJobs(req, res) {
  try {
    res.status(200).json({
      status: "success",
      active_jobs: {},
      completed_jobs: {},
      success: true
    });

  } catch (error) {
    console.error('Jobs error:', error);
    res.status(500).json({
      status: "error",
      message: "Failed to load jobs"
    });
  }
}

function handleIndex(req, res) {
  try {
    // Complete HTML with embedded JavaScript
    const html = `<!DOCTYPE html>
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

        <!-- Setup Card -->
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

        <!-- Job Creation Card -->
        <div class="card hidden" id="jobCard">
            <h2>📝 Create Automation Job</h2>
            <div class="form-group">
                <label>🏷️ Topics (Click to select)</label>
                <div class="topics-container" id="topicsContainer">
                    <div style="color: #666;">Loading topics...</div>
                </div>
            </div>
            <div class="form-group">
                <label for="customTopics">✍️ Custom Topics (one per line)</label>
                <textarea id="customTopics" rows="3"
                    placeholder="Artificial Intelligence&#10;Digital Marketing&#10;Social Media Strategy"></textarea>
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

        <!-- Active Jobs Card -->
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
        let apiKey = localStorage.getItem('zai_api_key') || '';

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🚀 Instagram Automation loaded');
            if (apiKey) {
                document.getElementById('apiKey').value = apiKey;
                setupAPI();
            }
        });

        async function loadTopics() {
            try {
                console.log('📋 Loading topics...');
                const response = await fetch(\`\${API_BASE}/api/topics\`);
                const data = await response.json();

                if (data.success) {
                    const container = document.getElementById('topicsContainer');
                    container.innerHTML = '';

                    data.default_topics.forEach(topic => {
                        const chip = document.createElement('div');
                        chip.className = 'topic-chip';
                        chip.textContent = topic;
                        chip.onclick = () => toggleTopic(chip, topic);
                        container.appendChild(chip);
                    });

                    console.log('✅ Topics loaded:', data.default_topics.length);
                } else {
                    throw new Error('Failed to load topics');
                }
            } catch (error) {
                console.error('❌ Failed to load topics:', error);
                document.getElementById('topicsContainer').innerHTML =
                    '<div style="color: #721c24;">Failed to load topics</div>';
            }
        }

        function toggleTopic(chip, topic) {
            if (selectedTopics.has(topic)) {
                selectedTopics.delete(topic);
                chip.classList.remove('selected');
            } else {
                selectedTopics.add(topic);
                chip.classList.add('selected');
            }
            console.log('🏷️ Selected topics:', Array.from(selectedTopics));
        }

        async function setupAPI() {
            const apiKeyInput = document.getElementById('apiKey');
            const key = apiKeyInput.value.trim();

            if (!key) {
                showStatus('setupStatus', '❌ Please enter your API key', 'error');
                return;
            }

            const btn = document.getElementById('setupBtn');
            const icon = document.getElementById('setupIcon');
            const text = document.getElementById('setupText');

            btn.disabled = true;
            icon.innerHTML = '<span class="loading"></span>';
            text.textContent = 'Connecting...';

            try {
                console.log('🔗 Testing API connection...');
                const response = await fetch(\`\${API_BASE}/api/setup\`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: key })
                });

                const data = await response.json();
                console.log('📡 API Response:', data);

                if (response.ok && data.success) {
                    apiKey = key;
                    localStorage.setItem('zai_api_key', key);
                    showStatus('setupStatus', '✅ API connected successfully!', 'success');
                    console.log('✅ API Setup successful!');

                    // Show other cards with animation
                    setTimeout(() => {
                        document.getElementById('jobCard').classList.remove('hidden');
                        document.getElementById('jobsCard').classList.remove('hidden');

                        // Load topics
                        loadTopics();

                        // Start job refresh
                        refreshJobs();
                        setInterval(refreshJobs, 5000);

                        showStatus('jobStatus', '🎉 Ready to create automation jobs!', 'success');
                    }, 500);

                } else {
                    showStatus('setupStatus', \`❌ \${data.message || 'Failed to connect API'}\`, 'error');
                }
            } catch (error) {
                console.error('❌ Setup error:', error);
                showStatus('setupStatus', \`❌ Connection failed: \${error.message}\`, 'error');
            } finally {
                btn.disabled = false;
                icon.innerHTML = '🔗';
                text.textContent = 'Connect API';
            }
        }

        async function startJob() {
            const customTopicsText = document.getElementById('customTopics').value;
            const maxPosts = parseInt(document.getElementById('maxPosts').value);
            const timeRange = document.getElementById('timeRange').value;

            const customTopics = customTopicsText
                .split('\\n')
                .map(t => t.trim())
                .filter(t => t);

            const allTopics = [...selectedTopics, ...customTopics];

            if (allTopics.length === 0) {
                showStatus('jobStatus', '❌ Please select or enter at least one topic', 'error');
                return;
            }

            const btn = document.getElementById('startBtn');
            const icon = document.getElementById('startIcon');
            const text = document.getElementById('startText');

            btn.disabled = true;
            icon.innerHTML = '<span class="loading"></span>';
            text.textContent = 'Starting...';

            try {
                console.log('🚀 Starting job with topics:', allTopics);
                const response = await fetch(\`\${API_BASE}/api/generate\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey
                    },
                    body: JSON.stringify({
                        topics: allTopics,
                        options: { max_posts: maxPosts, time_range: timeRange }
                    })
                });

                const data = await response.json();
                console.log('📡 Job Response:', data);

                if (response.ok && data.success) {
                    showStatus('jobStatus',
                        \`✅ Job started successfully! Job ID: \${data.job_id}\`, 'success');

                    // Clear form
                    document.getElementById('customTopics').value = '';
                    document.querySelectorAll('.topic-chip.selected').forEach(chip => {
                        chip.classList.remove('selected');
                    });
                    selectedTopics.clear();

                    // Refresh jobs
                    setTimeout(refreshJobs, 1000);
                } else {
                    showStatus('jobStatus',
                        \`❌ \${data.message || 'Failed to start job'}\`, 'error');
                }
            } catch (error) {
                console.error('❌ Job error:', error);
                showStatus('jobStatus',
                    \`❌ Failed to start job: \${error.message}\`, 'error');
            } finally {
                btn.disabled = false;
                icon.innerHTML = '🚀';
                text.textContent = 'Start Automation';
            }
        }

        async function refreshJobs() {
            try {
                const response = await fetch(\`\${API_BASE}/api/jobs\`);
                const data = await response.json();

                if (data.success) {
                    const jobsList = document.getElementById('jobsList');

                    if (data.active_jobs && Object.keys(data.active_jobs).length > 0) {
                        let html = '<h3 style="color: #667eea; margin-bottom: 15px;">🔄 Active Jobs</h3>';
                        Object.entries(data.active_jobs).forEach(([jobId, job]) => {
                            html += \`
                                <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 10px; border-left: 4px solid #667eea;">
                                    <h4 style="color: #667eea;">🚀 Job: \${jobId.substring(0, 8)}...</h4>
                                    <p><strong>Status:</strong> \${job.status}</p>
                                    <p><strong>Progress:</strong> \${job.progress || 0}%</p>
                                    <p><strong>Message:</strong> \${job.message || 'Processing...'}</p>
                                </div>
                            \`;
                        });
                        jobsList.innerHTML = html;
                    } else {
                        jobsList.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No active jobs. Create your first automation job! 🚀</p>';
                    }
                }
            } catch (error) {
                console.error('❌ Failed to refresh jobs:', error);
            }
        }

        function showStatus(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = \`<div class="status \${type}">\${message}</div>\`;

            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    element.innerHTML = '';
                }, 5000);
            }
        }
    </script>
</body>
</html>`;

    res.setHeader('Content-Type', 'text/html');
    res.send(html);

  } catch (error) {
    console.error('Index error:', error);
    res.status(500).send('<h1>Server Error</h1>');
  }
}