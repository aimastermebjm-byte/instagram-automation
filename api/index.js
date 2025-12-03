const { spawn } = require('child_process');

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

  try {
    // Create simple response without Python
    const response = {
      status: "success",
      message: "Instagram Automation API is running!",
      method: req.method,
      path: req.url,
      headers: req.headers,
      debug: "Node.js handler executed successfully",
      vercel_runtime: "nodejs18.x"
    };

    res.status(200).json(response);

  } catch (error) {
    console.error('Error in handler:', error);

    const errorResponse = {
      status: "error",
      message: "Internal server error",
      error: error.message,
      debug: "Error in Node.js handler"
    };

    res.status(500).json(errorResponse);
  }
};