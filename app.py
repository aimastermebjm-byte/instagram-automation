#!/usr/bin/env python3
"""
Instagram Automation Web App
PWA-enabled web interface for automated Instagram content creation
"""

import os
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
import threading
import time

from main import InstagramAutomation
from config import config
from instagram_client import InstagramClient

app = Flask(__name__)
CORS(app)

# Configuration
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for job tracking
active_jobs = {}
job_results = {}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(config.POSTS_OUTPUT_DIR, exist_ok=True)
os.makedirs('static/generated_images', exist_ok=True)

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or session.get('api_key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        # Validate API key
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401

        session['api_key'] = api_key
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key):
    """Basic API key validation"""
    # In production, store and validate against database
    return api_key and len(api_key) > 10

def run_automation_job(job_id: str, topics: list, options: dict, api_key: str):
    """Run automation job in background thread"""

    try:
        # Update job status
        active_jobs[job_id] = {
            'status': 'running',
            'progress': 0,
            'started_at': datetime.now().isoformat(),
            'current_topic': '',
            'message': 'Initializing automation system...'
        }

        # Initialize automation
        automation = InstagramAutomation(api_key)

        # Initialize Instagram client if auto-posting
        instagram_client = None
        if options.get('auto_post'):
            instagram_client = InstagramClient()
            if not instagram_client.test_connection():
                options['auto_post'] = False

        all_posts = []
        total_topics = len(topics)

        for i, topic in enumerate(topics):
            # Update progress
            active_jobs[job_id].update({
                'progress': (i / total_topics) * 100,
                'current_topic': topic,
                'message': f'Processing topic {i+1}/{total_topics}: {topic}'
            })

            # Process topic
            posts = automation.process_topic(
                topic=topic,
                time_range=options.get('time_range', 'oneDay'),
                max_posts=options.get('max_posts', 3)
            )

            if posts:
                # Auto-post if enabled
                if options.get('auto_post') and instagram_client:
                    for j, post in enumerate(posts):
                        active_jobs[job_id]['message'] = f'Posting to Instagram ({j+1}/{len(posts)})...'

                        # Schedule with delay
                        scheduled_time = datetime.now() + timedelta(minutes=j*10)
                        result = instagram_client.schedule_post(
                            image_url=post.image_url,
                            caption=post.caption,
                            scheduled_time=scheduled_time
                        )

                        time.sleep(2)  # Rate limiting

                all_posts.extend(posts)

        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config.POSTS_OUTPUT_DIR}/web_posts_{timestamp}.json"

        posts_data = []
        for post in all_posts:
            post_dict = {
                "topic": post.topic,
                "image_url": post.image_url,
                "caption": post.caption,
                "hashtags": post.hashtags,
                "scheduled_time": post.scheduled_time.isoformat(),
                "created_at": datetime.now().isoformat(),
                "auto_posted": options.get('auto_post', False)
            }
            posts_data.append(post_dict)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)

        # Update job completion
        active_jobs[job_id].update({
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.now().isoformat(),
            'message': f'Successfully created {len(all_posts)} posts',
            'total_posts': len(all_posts),
            'filename': filename,
            'topics_processed': topics
        })

        job_results[job_id] = {
            'posts': posts_data,
            'filename': filename,
            'total_posts': len(all_posts)
        }

    except Exception as e:
        active_jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat(),
            'message': f'Error: {str(e)}'
        })

# Web Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/setup')
def setup():
    """Setup page for API key"""
    return render_template('setup.html')

@app.route('/dashboard')
@require_api_key
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/history')
@require_api_key
def history():
    """Job history page"""
    return render_template('history.html')

# API Routes
@app.route('/api/setup', methods=['POST'])
def api_setup():
    """Setup API key"""
    data = request.get_json()
    api_key = data.get('api_key')

    if not api_key:
        return jsonify({'error': 'API key is required'}), 400

    # Validate API key with Z.ai
    try:
        automation = InstagramAutomation(api_key)
        # Test with simple request
        test_result = automation.zai_client.chat_completion(
            "Test connection",
            max_tokens=10
        )

        if test_result:
            session['api_key'] = api_key
            return jsonify({
                'success': True,
                'message': 'API key validated successfully'
            })
        else:
            return jsonify({'error': 'Invalid API key'}), 400

    except Exception as e:
        return jsonify({'error': f'API validation failed: {str(e)}'}), 400

@app.route('/api/test-connection', methods=['POST'])
@require_api_key
def api_test_connection():
    """Test API connections"""
    api_key = session.get('api_key')
    results = {}

    # Test Z.ai API
    try:
        automation = InstagramAutomation(api_key)
        test_result = automation.zai_client.chat_completion(
            "Connection test",
            max_tokens=10
        )
        results['zai'] = {'success': True, 'message': 'Connected'}
    except Exception as e:
        results['zai'] = {'success': False, 'error': str(e)}

    # Test Instagram API
    try:
        instagram_client = InstagramClient()
        if instagram_client.is_configured():
            instagram_client.test_connection()
            results['instagram'] = {'success': True, 'message': 'Connected'}
        else:
            results['instagram'] = {'success': False, 'message': 'Not configured'}
    except Exception as e:
        results['instagram'] = {'success': False, 'error': str(e)}

    return jsonify(results)

@app.route('/api/start-job', methods=['POST'])
@require_api_key
def api_start_job():
    """Start automation job"""
    data = request.get_json()
    topics = data.get('topics', [])
    options = data.get('options', {})

    if not topics:
        return jsonify({'error': 'At least one topic is required'}), 400

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Start background job
    thread = threading.Thread(
        target=run_automation_job,
        args=(job_id, topics, options, session.get('api_key'))
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'job_id': job_id,
        'message': 'Job started successfully',
        'topics': topics,
        'options': options
    })

@app.route('/api/job-status/<job_id>')
@require_api_key
def api_job_status(job_id):
    """Get job status"""
    job = active_jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(job)

@app.route('/api/job-results/<job_id>')
@require_api_key
def api_job_results(job_id):
    """Get job results"""
    results = job_results.get(job_id)

    if not results:
        return jsonify({'error': 'Results not found'}), 404

    return jsonify(results)

@app.route('/api/jobs')
@require_api_key
def api_jobs():
    """Get all jobs"""
    return jsonify({
        'active_jobs': active_jobs,
        'completed_jobs': job_results
    })

@app.route('/api/topics')
@require_api_key
def api_topics():
    """Get available topics"""
    return jsonify({
        'default_topics': config.DEFAULT_TOPICS,
        'indonesian_news_domains': config.INDONESIAN_NEWS_DOMAINS
    })

@app.route('/api/download/<filename>')
@require_api_key
def api_download(filename):
    """Download generated posts file"""
    try:
        return send_file(
            os.path.join(config.POSTS_OUTPUT_DIR, filename),
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/config')
@require_api_key
def api_config():
    """Get configuration"""
    return jsonify({
        'posts_per_topic': config.POSTS_PER_TOPIC,
        'default_time_range': config.DEFAULT_TIME_RANGE,
        'optimal_posting_hours': config.OPTIMAL_POSTING_HOURS,
        'max_hashtags': config.MAX_HASHTAGS
    })

# PWA Manifest Route
@app.route('/manifest.json')
def manifest():
    """PWA manifest"""
    return jsonify({
        "name": "Instagram Automation",
        "short_name": "IG Automator",
        "description": "Automated Instagram content creation powered by AI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#E4405F",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

# Service Worker Route
@app.route('/sw.js')
def service_worker():
    """PWA service worker"""
    return app.send_static_file('sw.js')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create static directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    print("🚀 Starting Instagram Automation Web App")
    print("📱 Access at: http://localhost:5000")
    print("🔧 PWA enabled - can be installed as mobile app")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )