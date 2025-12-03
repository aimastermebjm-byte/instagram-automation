#!/usr/bin/env python3
"""
Vercel Serverless Function Handler for Instagram Automation
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Flask app
from app import app

# Vercel serverless function handler
def handler(request):
    """
    Vercel serverless function handler
    """
    return app(request.environ, lambda status, headers: None)

# Export handler for Vercel
app_handler = handler

# For local testing
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)