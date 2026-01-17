#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from datetime import datetime
from stl_generator_working import RackMountGenerator, STLWriter, calculate_print_stats, generate_assembly_guide
import tempfile
import urllib.parse

OUTPUT_FOLDER = os.path.join(tempfile.gettempdir(), 'rack_mounts')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class RackMountHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'version': '1.0.0'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode())
                
                config = {
                    'width': float(data['width']),
                    'height': float(data['height']),
                    'depth': float(data['depth']),
                    'tolerance': float(data['tolerance']),
                    'wall_thickness': float(data['wallThickness']),
                    'add_support': data.get('addSupport', True),
                    'infill': int(data.get('infill', 20)),
                }
                
                gen = RackMountGenerator(
                    config['width'], config['height'], config['depth'],
                    config['tolerance'], config['wall_thickness'],
                    config['add_support'], False
                )
                
                job_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                job_dir = os.path.join(OUTPUT_FOLDER, f'mount_{job_id}')
                os.makedirs(job_dir, exist_ok=True)
                
                parts = gen.generate_all_parts()
                file_info = []
                
                for part_name, triangles in parts.items():
                    if triangles:
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
                
                generate_assembly_guide(job_dir, {'width': config['width'], 'height': config['height'],
                                                  'depth': config['depth'], 'tolerance': config['tolerance'],
                                                  'wall_thickness': config['wall_thickness'],
                                                  'infill': config['infill']})
                
                file_info.append({'name': 'ASSEMBLY_GUIDE.md', 'size_mb': 0.01})
                
                total_weight = sum(f.get('weight_g', 0) for f in file_info if 'weight_g' in f)
                total_time = sum(f.get('print_time_h', 0) for f in file_info if 'print_time_h' in f)
                
                response = {
                    'success': True,
                    'job_id': job_id,
                    'files': file_info,
                    'config': config,
                    'stats': {
                        'total_weight_g': round(total_weight, 1),
                        'total_time_h': round(total_time, 1),
                        'total_parts': len([f for f in file_info if f['name'].endswith('.stl')])
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = 9999
    server = HTTPServer(('127.0.0.1', port), RackMountHandler)
    print(f"🚀 19\" Rack Mount Generator")
    print(f"📍 Open http://localhost:{port}")
    print(f"✅ Server running...")
    server.serve_forever()
