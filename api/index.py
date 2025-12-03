#!/usr/bin/env python3
"""
Simple Vercel Serverless Function Handler
"""
import json

def handler(request):
    """Simple handler for Vercel serverless function"""

    try:
        # Get request data
        method = request.method
        path = request.path

        # Simple response for testing
        response_data = {
            "message": "Instagram Automation API is running!",
            "method": method,
            "path": path,
            "status": "success"
        }

        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps(response_data, indent=2)
        }

    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "status": "error"
            })
        }

# Export handler for Vercel
app_handler = handler