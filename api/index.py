#!/usr/bin/env python3
"""
Vercel Serverless Function for Instagram Automation API
Real Z.ai API integration with Python backend
"""

import os
import json
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import InstagramAutomation
    from config import config
except ImportError:
    # Fallback for Vercel deployment
    class Config:
        DEFAULT_TOPICS = [
            "Artificial Intelligence",
            "Machine Learning",
            "Digital Marketing",
            "Social Media Strategy",
            "Content Creation",
            "Technology Trends",
            "Business Innovation",
            "Startup Life"
        ]
        INDONESIAN_NEWS_DOMAINS = [
            "detik.com", "kompas.com", "tempo.co", "cnnindonesia.com",
            "liputan6.com", "tribunnews.com", "sindonews.com", "viva.co.id",
            "merdeka.com", "okezone.com", "suara.com", "antaranews.com",
            "republika.co.id", "mediaindonesia.com", "jawapos.com"
        ]
        OPTIMAL_POSTING_HOURS = [9, 12, 15, 18, 21]
        MAX_HASHTAGS = 30
        POSTS_PER_TOPIC = 3
        DEFAULT_TIME_RANGE = "oneDay"
        DEBUG = True
        POSTS_OUTPUT_DIR = "generated_posts"

    config = Config()

# In-memory job storage for Vercel serverless
active_jobs = {}
job_results = {}

def handler(request):
    """Main handler for Vercel serverless function"""

    # Get request method and path
    method = request.method
    path = request.path.strip('/')

    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
        'Content-Type': 'application/json'
    }

    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        # Route handling
        if path == '' and method == 'GET':
            return handle_index()

        elif path == 'api/setup' and method == 'POST':
            return handle_setup(request)

        elif path == 'api/test-connection' and method == 'POST':
            return handle_test_connection(request)

        elif path == 'api/start-job' and method == 'POST':
            return handle_start_job(request)

        elif path.startswith('api/job-status/') and method == 'GET':
            job_id = path.split('api/job-status/')[-1]
            return handle_job_status(job_id)

        elif path.startswith('api/job-results/') and method == 'GET':
            job_id = path.split('api/job-results/')[-1]
            return handle_job_results(job_id)

        elif path == 'api/jobs' and method == 'GET':
            return handle_jobs()

        elif path == 'api/topics' and method == 'GET':
            return handle_topics()

        elif path == 'api/config' and method == 'GET':
            return handle_config()

        else:
            # Serve index.html for all other routes
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    'statusCode': 200,
                    'headers': {**headers, 'Content-Type': 'text/html'},
                    'body': content
                }
            except FileNotFoundError:
                return error_response("Page not found", 404)

    except Exception as e:
        print(f"Handler error: {str(e)}")
        return error_response(f"Internal server error: {str(e)}", 500)

def handle_index():
    """Handle root endpoint"""
    return json_response({
        'status': 'success',
        'message': 'Instagram Automation API',
        'description': 'Automated Instagram content creation powered by AI',
        'version': '1.0.0',
        'endpoints': {
            'setup': 'POST /api/setup - Configure API key',
            'test_connection': 'POST /api/test-connection - Test API connections',
            'start_job': 'POST /api/start-job - Start automation job',
            'job_status': 'GET /api/job-status/{jobId} - Get job status',
            'job_results': 'GET /api/job-results/{jobId} - Get job results',
            'jobs': 'GET /api/jobs - Get all jobs',
            'topics': 'GET /api/topics - Get available topics',
            'config': 'GET /api/config - Get configuration'
        }
    })

def handle_setup(request):
    """Handle API key setup and validation"""

    # Get API key from header first, then from body
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        try:
            body = json.loads(request.body)
            api_key = body.get('api_key')
        except (json.JSONDecodeError, AttributeError):
            pass

    if not api_key:
        return error_response('API key is required', 400)

    try:
        # Test with real Z.ai API
        automation = InstagramAutomation(api_key)

        # Test API with a simple request
        test_result = automation.zai_client.chat_completion(
            "Test connection",
            max_tokens=10
        )

        if test_result and test_result.strip():
            return json_response({
                'success': True,
                'message': 'API key validated successfully'
            })
        else:
            return error_response('Invalid API key - no response from Z.ai', 400)

    except Exception as e:
        print(f"API validation error: {str(e)}")
        return error_response(f'API validation failed: {str(e)}', 400)

def handle_test_connection(request):
    """Test API connections"""

    # Get API key from header
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return error_response('API key required', 401)

    results = {}

    # Test Z.ai API
    try:
        automation = InstagramAutomation(api_key)
        test_result = automation.zai_client.chat_completion(
            "Connection test",
            max_tokens=10
        )
        results['zai'] = {'success': True, 'message': 'Connected to Z.ai API'}
    except Exception as e:
        results['zai'] = {'success': False, 'error': str(e)}

    # Instagram API would go here (not implemented in demo)
    results['instagram'] = {'success': False, 'message': 'Not configured'}

    return json_response(results)

def handle_start_job(request):
    """Start automation job"""

    # Get API key from header
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return error_response('API key required', 401)

    try:
        body = json.loads(request.body)
        topics = body.get('topics', [])
        options = body.get('options', {})

        if not topics or not isinstance(topics, list) or len(topics) == 0:
            return error_response('At least one topic is required', 400)

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initialize job
        active_jobs[job_id] = {
            'status': 'running',
            'progress': 0,
            'started_at': datetime.now().isoformat(),
            'current_topic': '',
            'message': 'Initializing automation system...',
            'topics': topics,
            'options': options
        }

        # Start job processing in background (simulate for demo)
        simulate_job_processing(job_id, topics, options, api_key)

        return json_response({
            'job_id': job_id,
            'message': 'Job started successfully',
            'topics': topics,
            'options': options
        })

    except json.JSONDecodeError:
        return error_response('Invalid JSON', 400)
    except Exception as e:
        print(f"Start job error: {str(e)}")
        return error_response(f'Failed to start job: {str(e)}', 500)

def simulate_job_processing(job_id: str, topics: List[str], options: Dict, api_key: str):
    """Simulate job processing (in production, this would use real Z.ai API)"""

    try:
        automation = InstagramAutomation(api_key)
        total_topics = len(topics)
        all_posts = []

        for i, topic in enumerate(topics):
            # Update progress
            if job_id in active_jobs:
                active_jobs[job_id].update({
                    'progress': (i / total_topics) * 100,
                    'current_topic': topic,
                    'message': f'Processing topic {i+1}/{total_topics}: {topic}'
                })

            # Process topic with real Z.ai API
            try:
                time_range = options.get('time_range', 'oneDay')
                max_posts = options.get('max_posts', 3)

                posts = automation.process_topic(
                    topic=topic,
                    time_range=time_range,
                    max_posts=max_posts
                )

                if posts:
                    all_posts.extend(posts)

            except Exception as e:
                print(f"Error processing topic {topic}: {str(e)}")
                continue

        # Complete job
        if job_id in active_jobs:
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'message': f'Successfully processed {total_topics} topics',
                'total_posts': len(all_posts)
            })

            # Store results with better structure
            job_results[job_id] = {
                'posts': format_posts_for_display(all_posts),
                'total_posts': len(all_posts),
                'completed_at': datetime.now().isoformat(),
                'topics_processed': topics
            }

    except Exception as e:
        if job_id in active_jobs:
            active_jobs[job_id].update({
                'status': 'failed',
                'error': str(e),
                'failed_at': datetime.now().isoformat(),
                'message': f'Error: {str(e)}'
            })

def handle_job_status(job_id: str):
    """Get job status"""

    job = active_jobs.get(job_id)
    if not job:
        return error_response('Job not found', 404)

    return json_response(job)

def handle_job_results(job_id: str):
    """Get job results"""

    results = job_results.get(job_id)
    if not results:
        return error_response('Results not found', 404)

    return json_response(results)

def handle_jobs():
    """Get all jobs"""

    return json_response({
        'active_jobs': active_jobs,
        'completed_jobs': job_results
    })

def handle_topics():
    """Get available topics"""

    return json_response({
        'default_topics': config.DEFAULT_TOPICS,
        'indonesian_news_domains': config.INDONESIAN_NEWS_DOMAINS
    })

def handle_config():
    """Get configuration"""

    return json_response({
        'posts_per_topic': config.POSTS_PER_TOPIC,
        'default_time_range': config.DEFAULT_TIME_RANGE,
        'optimal_posting_hours': config.OPTIMAL_POSTING_HOURS,
        'max_hashtags': config.MAX_HASHTAGS
    })

def json_response(data: Dict, status_code: int = 200):
    """Create JSON response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data, ensure_ascii=False, indent=2)
    }

def error_response(message: str, status_code: int = 400):
    """Create error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'error': message,
            'status': 'error'
        }, ensure_ascii=False, indent=2)
    }

# Vercel serverless function entry point
def lambda_handler(event, context):
    """AWS Lambda compatible handler for Vercel"""

    class Request:
        def __init__(self, event):
            self.method = event.get('httpMethod', 'GET')
            self.path = event.get('path', '/')
            self.headers = event.get('headers', {})
            self.body = event.get('body', '{}')

    request = Request(event)
    response = handler(request)

    return {
        'statusCode': response['statusCode'],
        'headers': response['headers'],
        'body': response['body']
    }

def format_posts_for_display(posts):
    """Format posts for better display in frontend"""
    formatted_posts = []

    for post in posts:
        # Try to extract post data based on post structure
        post_data = {
            'topic': 'AI Generated Content',
            'caption': '🚀 Exciting content created by AI automation system! This post was generated using advanced AI technology to engage your audience.',
            'hashtags': ['#AI', '#Instagram', '#ContentCreation', '#DigitalMarketing'],
            'image_url': 'https://picsum.photos/1080/1080?random=' + str(hash(str(post)) % 1000)
        }

        # Try to extract actual data from post object
        if hasattr(post, 'topic'):
            post_data['topic'] = post.topic
        if hasattr(post, 'caption'):
            post_data['caption'] = post.caption
        if hasattr(post, 'hashtags'):
            post_data['hashtags'] = post.hashtags if post.hashtags else ['#AI', '#Instagram']
        if hasattr(post, 'image_url'):
            post_data['image_url'] = post.image_url
        elif hasattr(post, 'image_path'):
            post_data['image_url'] = post.image_path
        elif hasattr(post, 'image'):
            post_data['image_url'] = post.image

        # Try to extract from dict-like objects
        if isinstance(post, dict):
            post_data.update({
                'topic': post.get('topic', 'AI Generated Content'),
                'caption': post.get('caption', post_data['caption']),
                'hashtags': post.get('hashtags', post_data['hashtags']),
                'image_url': post.get('image_url', post.get('image', post_data['image_url']))
            })

        formatted_posts.append(post_data)

    return formatted_posts

# For Vercel's Python runtime
app = handler