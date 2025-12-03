#!/usr/bin/env python3
"""
Web App Runner for Instagram Automation PWA
Production-ready web application runner
"""

import os
import sys
from app import app

def main():
    """Run the Instagram Automation Web App"""

    print("""
    🚀 INSTAGRAM AUTOMATION WEB APP
    ==================================

    📱 PWA Features Enabled:
       • Install as mobile app
       • Offline support
       • Background sync
       • Push notifications

    🌐 Web Interface:
       • Responsive design
       • Real-time updates
       • Job management
       • Progress tracking

    🔧 API Integration:
       • Z.ai AI-powered content
       • Instagram Graph API
       • Multi-source news scraping
       • Smart scheduling

    ⚡ Performance:
       • Caching enabled
       • Optimized API calls
       • Background processing
       • Error recovery

    📱 Access Instructions:
       1. Open browser: http://localhost:5000
       2. Setup your Z.ai API key
       3. Select topics and create content
       4. Monitor progress in real-time
       5. Download results or auto-post

    📲 Mobile App:
       • On mobile, tap "Share" > "Add to Home Screen"
       • Works offline with cached content
       • Background sync when online

    🔐 Security:
       • API key validation
       • Session management
       • Rate limiting
       • Error handling
    """)

    print("🎯 Starting Web App...")
    print("📱 Mobile-optimized • PWA-ready • Real-time updates")
    print("🌐 Open: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop\n")

    # Production settings
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=debug_mode,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Web App stopped by user")
    except Exception as e:
        print(f"\n❌ Error running Web App: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()