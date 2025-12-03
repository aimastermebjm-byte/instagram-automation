#!/usr/bin/env python3
"""
Simple Vercel Python Function - No external dependencies
"""
import json

def handler(event, context):
    """Main handler function for Vercel"""

    # Extract basic request info
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})

    # Create simple response
    response_data = {
        "status": "success",
        "message": "Instagram Automation API is working!",
        "method": method,
        "path": path,
        "event_type": type(event).__name__,
        "context_type": type(context).__name__,
        "debug": "Simple Python handler executed"
    }

    # Return proper format
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_data, indent=2)
    }

# Export for Vercel
app_handler = handler