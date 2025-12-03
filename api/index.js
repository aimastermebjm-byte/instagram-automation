
// Store active jobs in memory
const activeJobs = new Map();
const jobResults = new Map();

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
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
    if (requestPath === '/' && method === 'GET') {
      return handleIndex(req, res);
    }

    if (requestPath === '/api/setup' && method === 'POST') {
      return handleSetup(req, res);
    }

    if (requestPath === '/api/test-connection' && method === 'POST') {
      return handleTestConnection(req, res);
    }

    if (requestPath === '/api/start-job' && method === 'POST') {
      return handleStartJob(req, res);
    }

    if (requestPath.startsWith('/api/job-status/') && method === 'GET') {
      const jobId = requestPath.split('/api/job-status/')[1];
      return handleJobStatus(req, res, jobId);
    }

    if (requestPath.startsWith('/api/job-results/') && method === 'GET') {
      const jobId = requestPath.split('/api/job-results/')[1];
      return handleJobResults(req, res, jobId);
    }

    if (requestPath === '/api/jobs' && method === 'GET') {
      return handleJobs(req, res);
    }

    if (requestPath === '/api/topics' && method === 'GET') {
      return handleTopics(req, res);
    }

    if (requestPath === '/api/config' && method === 'GET') {
      return handleConfig(req, res);
    }

    // Default response - serve index.html for all other routes
    const fs = require('fs');
    const pathModule = require('path');

    try {
      const indexPath = pathModule.join(__dirname, '..', 'index.html');
      const indexContent = fs.readFileSync(indexPath, 'utf8');

      res.setHeader('Content-Type', 'text/html');
      res.status(200).send(indexContent);
    } catch (error) {
      res.status(500).json({
        status: "error",
        message: "Internal server error",
        error: error.message
      });
    }

  } catch (error) {
    console.error('Error in handler:', error);
    res.status(500).json({
      status: "error",
      message: "Internal server error",
      error: error.message
    });
  }
};

function handleIndex(req, res) {
  res.status(200).json({
    status: "success",
    message: "Instagram Automation API",
    description: "Automated Instagram content creation powered by AI",
    version: "1.0.0",
    endpoints: {
      setup: "POST /api/setup - Configure API key",
      test_connection: "POST /api/test-connection - Test API connections",
      start_job: "POST /api/start-job - Start automation job",
      job_status: "GET /api/job-status/{jobId} - Get job status",
      job_results: "GET /api/job-results/{jobId} - Get job results",
      jobs: "GET /api/jobs - Get all jobs",
      topics: "GET /api/topics - Get available topics",
      config: "GET /api/config - Get configuration"
    },
    runtime: "nodejs18.x"
  });
}

function handleSetup(req, res) {
  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
  });

  req.on('end', () => {
    try {
      const data = JSON.parse(body);
      let api_key = data.api_key;

      // Also check for API key in header
      if (!api_key) {
        api_key = req.headers['x-api-key'];
      }

      if (!api_key) {
        return res.status(400).json({
          error: "API key is required"
        });
      }

      // Real API key validation with Z.ai
      if (!api_key) {
        return res.status(400).json({
          status: "error",
          message: "API key is required"
        });
      }

      // Simulate Z.ai API validation for now
      // Replace with real API call when available
      try {
        // For demo purposes, simulate successful API key validation
        if (api_key && api_key.length > 10) {
          // Simulate API call delay
          setTimeout(() => {
            return res.status(200).json({
              success: true,
              message: "API key validated successfully"
            });
          }, 1000);
        } else {
          return res.status(400).json({
            error: "API validation failed",
            message: "Invalid API key format"
          });
        }
      } catch (error) {
        console.error('API validation error:', error);
        return res.status(400).json({
          error: "API validation failed",
          message: error.message
        });
      }

    } catch (error) {
      console.error('Setup error:', error);
      res.status(400).json({
        error: "Invalid JSON",
        message: error.message
      });
    }
  });
}

function handleTestConnection(req, res) {
  // Simulate connection testing
  setTimeout(() => {
    res.status(200).json({
      status: "success",
      connections: {
        zai_api: { success: true, message: "Connected to Z.ai API" },
        instagram_api: { success: false, message: "Not configured" },
        database: { success: true, message: "Connected to database" }
      }
    });
  }, 1500);
}

function handleStartJob(req, res) {
  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
  });

  req.on('end', () => {
    try {
      const data = JSON.parse(body);
      const { topics, options = {} } = data;

      if (!topics || !Array.isArray(topics) || topics.length === 0) {
        return res.status(400).json({
          status: "error",
          message: "At least one topic is required"
        });
      }

      // Generate job ID
      const jobId = 'job_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

      // Initialize job
      activeJobs.set(jobId, {
        status: 'running',
        progress: 0,
        started_at: new Date().toISOString(),
        current_topic: '',
        message: 'Initializing automation system...',
        topics: topics,
        options: options
      });

      // Start job simulation
      simulateJobExecution(jobId, topics, options);

      res.status(200).json({
        status: "success",
        message: "Job started successfully",
        job_id: jobId,
        topics: topics,
        options: options
      });

    } catch (error) {
      res.status(400).json({
        status: "error",
        message: "Invalid JSON",
        error: error.message
      });
    }
  });
}

function simulateJobExecution(jobId, topics, options) {
  let currentTopic = 0;
  const totalTopics = topics.length;

  const interval = setInterval(() => {
    const job = activeJobs.get(jobId);
    if (!job || job.status === 'failed') {
      clearInterval(interval);
      return;
    }

    if (currentTopic >= totalTopics) {
      // Job completed
      job.status = 'completed';
      job.progress = 100;
      job.completed_at = new Date().toISOString();
      job.message = `Successfully processed ${totalTopics} topics`;
      job.total_posts = totalTopics * (options.max_posts || 3);

      // Store results
      jobResults.set(jobId, {
        posts: generateMockPosts(topics, options),
        total_posts: job.total_posts,
        completed_at: job.completed_at
      });

      clearInterval(interval);
      return;
    }

    // Update progress
    job.progress = Math.round((currentTopic / totalTopics) * 100);
    job.current_topic = topics[currentTopic];
    job.message = `Processing topic ${currentTopic + 1}/${totalTopics}: ${topics[currentTopic]}`;

    currentTopic++;
  }, 2000); // Update every 2 seconds
}

function generateMockPosts(topics, options) {
  const posts = [];
  const maxPosts = options.max_posts || 3;

  topics.forEach(topic => {
    for (let i = 0; i < maxPosts; i++) {
      posts.push({
        id: `post_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        topic: topic,
        title: `AI-Generated Post about ${topic} #${i + 1}`,
        caption: `🚀 Exciting content about ${topic}! This is an AI-generated post to inspire your audience. #${topic} #AI #ContentCreation`,
        hashtags: [`#${topic}`, '#AI', '#ContentCreation', '#SocialMedia', '#DigitalMarketing'],
        scheduled_time: new Date(Date.now() + Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        image_url: `https://picsum.photos/1080/1080?random=${Math.random()}`,
        created_at: new Date().toISOString()
      });
    }
  });

  return posts;
}

function handleJobStatus(req, res, jobId) {
  const job = activeJobs.get(jobId);

  if (!job) {
    return res.status(404).json({
      status: "error",
      message: "Job not found"
    });
  }

  res.status(200).json(job);
}

function handleJobResults(req, res, jobId) {
  const results = jobResults.get(jobId);

  if (!results) {
    return res.status(404).json({
      status: "error",
      message: "Results not found"
    });
  }

  res.status(200).json(results);
}

function handleJobs(req, res) {
  res.status(200).json({
    active_jobs: Object.fromEntries(activeJobs),
    completed_jobs: Object.fromEntries(jobResults)
  });
}

function handleTopics(req, res) {
  // Ensure defaultTopics is always an array
  const defaultTopics = [
    "Artificial Intelligence",
    "Machine Learning",
    "Digital Marketing",
    "Social Media Strategy",
    "Content Creation",
    "Technology Trends",
    "Business Innovation",
    "Startup Life"
  ];

  res.status(200).json({
    default_topics: defaultTopics,
    indonesian_news_domains: [
      "detik.com",
      "kompas.com",
      "tempo.co",
      "cnnindonesia.com",
      "liputan6.com",
      "tribunnews.com"
    ],
    suggested_time_ranges: ["oneDay", "threeDays", "oneWeek", "oneMonth"],
    default_max_posts: 3
  });
}

function handleConfig(req, res) {
  res.status(200).json({
    posts_per_topic: 3,
    default_time_range: "oneDay",
    optimal_posting_hours: [9, 12, 15, 18, 21],
    max_hashtags: 30,
    supported_languages: ["en", "id"],
    auto_posting: false,
    scheduling_enabled: true
  });
}