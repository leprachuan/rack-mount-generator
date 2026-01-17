#!/usr/bin/env python3
"""
Flask server for 19" Rack Mount Generator
Connects the web interface with the STL generation backend
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import tempfile
import shutil
from datetime import datetime
import io
import zipfile

from stl_generator import (
    RackMountGenerator,
    STLWriter,
    calculate_print_stats,
    generate_assembly_guide
)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, 'rack_mounts')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/generate', methods=['POST'])
def generate_mount():
    """
    Generate STL files based on form data

    Expected POST data:
    {
        "width": float,
        "height": float,
        "depth": float,
        "tolerance": float,
        "wallThickness": float,
        "addSupport": bool,
        "addRackHoles": bool,
        "infill": int,
        "bedSize": str,
        "customBedWidth": float (optional),
        "customBedDepth": float (optional)
    }
    """
    try:
        data = request.get_json()

        # Validate input
        required_fields = ['width', 'height', 'depth', 'tolerance', 'wallThickness']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Extract parameters
        config = {
            'width': float(data['width']),
            'height': float(data['height']),
            'depth': float(data['depth']),
            'tolerance': float(data['tolerance']),
            'wall_thickness': float(data['wallThickness']),
            'shelf_thickness': float(data.get('shelfThickness', 5.0)),
            'flange_thickness': float(data.get('flangeThickness', 5.0)),
            'gusset_size': float(data.get('gussetSize', 15.0)),
            'add_support': data.get('addSupport', True),
            'add_rack_holes': data.get('addRackHoles', True),
            'ear_side': data.get('earSide', 'left'),
            'is_blank': data.get('isBlank', False),
            'infill': int(data.get('infill', 20)),
            'bed_size': data.get('bedSize', 'prusa'),
            'timestamp': datetime.now().isoformat()
        }

        # Validate dimensions
        if config['width'] < 10 or config['width'] > 500:
            return jsonify({'error': 'Width must be between 10-500mm'}), 400
        if config['height'] < 10 or config['height'] > 500:
            return jsonify({'error': 'Height must be between 10-500mm'}), 400
        if config['depth'] < 10 or config['depth'] > 500:
            return jsonify({'error': 'Depth must be between 10-500mm'}), 400

        # Generate mount
        generator = RackMountGenerator(
            config['width'],
            config['height'],
            config['depth'],
            config['tolerance'],
            config['wall_thickness'],
            config['add_support'],
            config['add_rack_holes'],
            shelf_thickness=config['shelf_thickness'],
            flange_thickness=config['flange_thickness'],
            gusset_size=config['gusset_size'],
            ear_side=config['ear_side'],
            is_blank=config['is_blank']
        )

        # Create unique output directory
        job_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        job_dir = os.path.join(OUTPUT_FOLDER, f'mount_{job_id}')
        os.makedirs(job_dir, exist_ok=True)

        # Generate parts
        parts = generator.generate_all_parts()
        file_info = []

        # Write STL files
        for part_name, triangles in parts.items():
            if len(triangles) > 0:
                stl_path = os.path.join(job_dir, f'{part_name}.stl')
                STLWriter.write_binary_stl(stl_path, triangles, part_name)

                stats = calculate_print_stats(triangles, config['infill'])

                file_info.append({
                    'name': f'{part_name}.stl',
                    'path': stl_path,
                    'size_bytes': os.path.getsize(stl_path),
                    'size_mb': round(os.path.getsize(stl_path) / (1024 * 1024), 2),
                    'triangles': stats['triangle_count'],
                    'material_cm3': round(stats['material_volume_cm3'], 1),
                    'weight_g': round(stats['weight_grams'], 1),
                    'print_time_h': round(stats['print_time_hours'], 1)
                })

        # Generate assembly guide
        generate_assembly_guide(job_dir, {
            'width': config['width'],
            'height': config['height'],
            'depth': config['depth'],
            'tolerance': config['tolerance'],
            'wall_thickness': config['wall_thickness'],
            'infill': config['infill']
        })

        file_info.append({
            'name': 'ASSEMBLY_GUIDE.md',
            'path': os.path.join(job_dir, 'ASSEMBLY_GUIDE.md'),
            'size_mb': round(os.path.getsize(os.path.join(job_dir, 'ASSEMBLY_GUIDE.md')) / 1024, 2)
        })

        # Save configuration
        config_path = os.path.join(job_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Calculate totals
        total_weight = sum(f.get('weight_g', 0) for f in file_info if 'weight_g' in f)
        total_time = sum(f.get('print_time_h', 0) for f in file_info if 'print_time_h' in f)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'files': file_info,
            'config': config,
            'stats': {
                'total_weight_g': round(total_weight, 1),
                'total_time_h': round(total_time, 1),
                'total_parts': len([f for f in file_info if f['name'].endswith('.stl')])
            }
        }), 200

    except Exception as e:
        print(f"Error in /api/generate: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<job_id>/<filename>', methods=['GET'])
def download_file(job_id, filename):
    """Download a single STL file"""
    try:
        job_dir = os.path.join(OUTPUT_FOLDER, f'mount_{job_id}')
        file_path = os.path.join(job_dir, filename)

        # Security check - ensure file is in the job directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(job_dir)):
            return jsonify({'error': 'Invalid file path'}), 403

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-zip/<job_id>', methods=['GET'])
def download_all_files(job_id):
    """Download all files as a ZIP archive"""
    try:
        job_dir = os.path.join(OUTPUT_FOLDER, f'mount_{job_id}')

        if not os.path.exists(job_dir):
            return jsonify({'error': 'Job not found'}), 404

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in os.listdir(job_dir):
                if filename != 'config.json':  # Skip config in ZIP
                    file_path = os.path.join(job_dir, filename)
                    arcname = f'rack_mount_{job_id}/{filename}'
                    zip_file.write(file_path, arcname)

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'rack_mount_{job_id}.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<job_id>', methods=['GET'])
def get_preview_data(job_id):
    """Get preview data for a job"""
    try:
        job_dir = os.path.join(OUTPUT_FOLDER, f'mount_{job_id}')
        config_path = os.path.join(job_dir, 'config.json')

        if not os.path.exists(config_path):
            return jsonify({'error': 'Job not found'}), 404

        with open(config_path, 'r') as f:
            config = json.load(f)

        return jsonify({
            'success': True,
            'config': config
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


def cleanup_old_jobs(max_age_hours=24):
    """Clean up old job directories to save space"""
    if not os.path.exists(OUTPUT_FOLDER):
        return

    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    for job_folder in os.listdir(OUTPUT_FOLDER):
        job_path = os.path.join(OUTPUT_FOLDER, job_folder)
        if os.path.isdir(job_path):
            folder_age = current_time - os.path.getmtime(job_path)
            if folder_age > max_age_seconds:
                try:
                    shutil.rmtree(job_path)
                    print(f"Cleaned up old job: {job_folder}")
                except Exception as e:
                    print(f"Error cleaning up {job_folder}: {str(e)}")


if __name__ == '__main__':
    import sys
    
    # Clean up old jobs on startup
    cleanup_old_jobs()

    # Run Flask app
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
