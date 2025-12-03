#!/usr/bin/env python3
"""
Minimal Vercel Serverless Function for testing
"""
import json

def handler(request):
    """Basic Vercel serverless function handler"""

    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request path: {request.path}")
    print(f"DEBUG: Request headers: {dict(request.headers)}")

    try:
        # Simple response
        response_data = {
            "status": "success",
            "message": "Instagram Automation API is running!",
            "method": request.method or "GET",
            "path": request.path or "/",
            "debug": "Basic handler working"
        }

        response_body = json.dumps(response_data, indent=2)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key'
            },
            'body': response_body
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        error_response = {
            "status": "error",
            "message": "Internal server error",
            "error": str(e),
            "debug": "Error caught in handler"
        }

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_response, indent=2)
        }

# Export for Vercel
app_handler = handler