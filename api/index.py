#!/usr/bin/env python3
"""
Vercel Python Serverless Function
"""
import json
import sys
from wsgiref.headers import Headers

class VercelRequest:
    def __init__(self, event):
        self.event = event
        self.method = event.get('httpMethod', 'GET')
        self.path = event.get('path', '/')
        self.headers = event.get('headers', {})
        self.query = event.get('queryStringParameters', {})
        self.body = event.get('body', '')

class VercelResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = Headers()
        self.headers.add('Content-Type', 'application/json')
        self.headers.add('Access-Control-Allow-Origin', '*')

def handler(event, context):
    """
    Main Vercel handler function
    """
    try:
        request = VercelRequest(event)
        response = VercelResponse()

        # Simple response
        data = {
            "status": "success",
            "message": "Instagram Automation API is working!",
            "method": request.method,
            "path": request.path,
            "query": request.query,
            "debug": "Vercel Python function executed successfully"
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key'
            },
            'body': json.dumps(data, indent=2)
        }

    except Exception as e:
        print(f"Error in handler: {e}", file=sys.stderr)

        error_data = {
            "status": "error",
            "message": "Internal server error",
            "error": str(e),
            "debug": "Error caught in Vercel handler"
        }

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_data, indent=2)
        }

# Export for Vercel
app_handler = handler
lambda_handler = handler