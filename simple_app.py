from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import shutil
from datetime import datetime
from stl_generator_working import RackMountGenerator, STLWriter, calculate_print_stats, generate_assembly_guide

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = os.path.join(tempfile.gettempdir(), 'rack_mounts')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/api/generate', methods=['POST'])
def generate_mount():
    try:
        data = request.get_json()
        
        config = {
            'width': float(data['width']),
            'height': float(data['height']),
            'depth': float(data['depth']),
            'tolerance': float(data['tolerance']),
            'wall_thickness': float(data['wallThickness']),
            'add_support': data.get('addSupport', True),
            'add_rack_holes': data.get('addRackHoles', False),
            'infill': int(data.get('infill', 20)),
        }
        
        # Create generator
        generator = RackMountGenerator(
            config['width'], config['height'], config['depth'],
            config['tolerance'], config['wall_thickness'],
            config['add_support'], config['add_rack_holes']
        )
        
        # Create job directory
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
                    'size_mb': round(os.path.getsize(stl_path) / (1024 * 1024), 2),
                    'triangles': stats['triangle_count'],
                    'material_cm3': stats['material_volume_cm3'],
                    'weight_g': stats['weight_grams'],
                    'print_time_h': stats['print_time_hours']
                })
        
        # Generate assembly guide
        generate_assembly_guide(job_dir, {'width': config['width'], 'height': config['height'],
                                          'depth': config['depth'], 'tolerance': config['tolerance'],
                                          'wall_thickness': config['wall_thickness'],
                                          'infill': config['infill']})
        
        file_info.append({'name': 'ASSEMBLY_GUIDE.md', 'size_mb': 0.01})
        
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0.0'}), 200

if __name__ == '__main__':
    print("🚀 Starting 19\" Rack Mount Generator")
    print("📍 Open http://localhost:5000")
    app.run(debug=False, host='127.0.0.1', port=5001)
