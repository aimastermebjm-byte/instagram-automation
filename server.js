const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// API Routes
app.post('/api/setup', (req, res) => {
  try {
    const { api_key } = req.body;

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

app.post('/api/generate', (req, res) => {
  try {
    const { topics } = req.body;

    if (!topics || !topics.length) {
      return res.status(400).json({
        status: "error",
        message: "Topics are required"
      });
    }

    const jobId = "job_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);

    res.status(200).json({
      status: "success",
      job_id: jobId,
      message: "Job started for " + topics.length + " topics",
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
});

// Serve main HTML for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Instagram Automation server running on port ${PORT}`);
  console.log(`🌐 Access: http://localhost:${PORT}`);
});