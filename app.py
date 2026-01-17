#!/usr/bin/env python3
"""
Flask server for 19" Rack Mount Generator
Serves static files only - STL generation happens client-side via Three.js
"""

from flask import Flask, send_from_directory, jsonify
import sys

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'mode': 'client-side STL export'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting 19\" Rack Mount Generator Server")
    print("📍 Open http://localhost:5001 in your browser")
    print("\nServer running on http://127.0.0.1:5001")

    # Parse host and port from arguments
    host = '127.0.0.1'
    port = 5001  # Use 5001 since macOS ControlCenter uses 5000
    
    if '--host' in sys.argv:
        host_idx = sys.argv.index('--host')
        if host_idx + 1 < len(sys.argv):
            host = sys.argv[host_idx + 1]
    
    if '--port' in sys.argv:
        port_idx = sys.argv.index('--port')
        if port_idx + 1 < len(sys.argv):
            port = int(sys.argv[port_idx + 1])

    app.run(debug=True, host=host, port=port)
