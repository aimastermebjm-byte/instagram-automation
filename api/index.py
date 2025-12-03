#!/usr/bin/env python3
"""
Vercel Serverless Function for Instagram Automation API
Simplified stable version
"""

import json
import os
import uuid
from datetime import datetime
import urllib.parse

# In-memory job storage for Vercel serverless
active_jobs = {}
job_results = {}

# Simplified config for Vercel
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

def handler(request):
    """Main handler for Vercel serverless function"""

    try:
        # Get request method and path
        method = request.method
        path = request.path.strip('/') if request.path else ''

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

        # Default response - serve index.html for all other routes
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
            if request.body and isinstance(request.body, str):
                body = json.loads(request.body)
                api_key = body.get('api_key')
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            print(f"JSON parsing error: {str(e)}")
            pass

    if not api_key:
        return error_response('API key is required', 400)

    try:
        # Simulate API key validation for demo
        # In production, this would call real Z.ai API
        return json_response({
            'success': True,
            'message': 'API key validated successfully'
        })

    except Exception as e:
        print(f"API validation error: {str(e)}")
        return error_response(f'API validation failed: {str(e)}', 400)

def handle_test_connection(request):
    """Test API connections"""

    results = {}

    # Test Z.ai API (simulated for demo)
    results['zai'] = {'success': True, 'message': 'Connected to Z.ai API'}

    # Instagram API (not configured in demo)
    results['instagram'] = {'success': False, 'message': 'Not configured'}

    return json_response(results)

def handle_start_job(request):
    """Start automation job"""

    # Get API key from header
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return error_response('API key required', 401)

    try:
        if request.body and isinstance(request.body, str):
            body = json.loads(request.body)
            topics = body.get('topics', [])
            options = body.get('options', {})
        else:
            return error_response('Invalid request body', 400)

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
            'options': options,
            'total_posts': 0
        }

        # Start job simulation
        simulate_job_processing(job_id, topics, options)

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

def simulate_job_processing(job_id: str, topics: list, options: dict):
    """Simulate job processing with sample results"""

    try:
        total_topics = len(topics)

        # Simulate progress updates
        for i, topic in enumerate(topics):
            if job_id in active_jobs:
                progress = int(((i + 1) / total_topics) * 100)
                active_jobs[job_id].update({
                    'progress': progress,
                    'current_topic': topic,
                    'message': f'Processing topic {i+1}/{total_topics}: {topic}'
                })

        # Complete job
        if job_id in active_jobs:
            total_posts = len(topics) * options.get('max_posts', 3)
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'message': f'Successfully processed {total_topics} topics',
                'total_posts': total_posts
            })

            # Generate sample posts for results
            sample_posts = []
            for topic in topics:
                max_posts = options.get('max_posts', 3)
                for i in range(max_posts):
                    sample_posts.append({
                        'topic': topic,
                        'caption': f'🚀 Exciting AI-generated content about {topic}! This post showcases the latest trends in {topic} with engaging captions and relevant hashtags.',
                        'hashtags': [f'#{topic.replace(" ", "")}', '#AI', '#Instagram', '#ContentCreation'],
                        'image_url': f'https://picsum.photos/1080/1080?random={uuid.uuid4().hex[:8]}'
                    })

            # Store results
            job_results[job_id] = {
                'posts': sample_posts,
                'total_posts': len(sample_posts),
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
        'default_topics': DEFAULT_TOPICS,
        'indonesian_news_domains': [
            "detik.com", "kompas.com", "tempo.co", "cnnindonesia.com",
            "liputan6.com", "tribunnews.com", "sindonews.com", "viva.co.id",
            "merdeka.com", "okezone.com", "suara.com", "antaranews.com",
            "republika.co.id", "mediaindonesia.com", "jawapos.com"
        ]
    })

def handle_config():
    """Get configuration"""
    return json_response({
        'posts_per_topic': 3,
        'default_time_range': 'oneDay',
        'optimal_posting_hours': [9, 12, 15, 18, 21],
        'max_hashtags': 30
    })

def json_response(data: dict, status_code: int = 200):
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
app = handler