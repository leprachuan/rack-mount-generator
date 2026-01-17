# Architecture Guide - 19" Rack Mount Generator

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Computer                           │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Web Browser (Client)                     │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  index.html                                 │    │   │
│  │  │  ├─ HTML Form (Input Controls)             │    │   │
│  │  │  ├─ Three.js Scene (3D Preview)            │    │   │
│  │  │  ├─ CSS Styling (Responsive Design)        │    │   │
│  │  │  └─ JavaScript (Form Handling, API Calls)  │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                      ↓                                │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  HTTPS/HTTP Communication                   │    │   │
│  │  │  ├─ POST /api/generate                      │    │   │
│  │  │  ├─ GET /api/download/<job_id>/<file>     │    │   │
│  │  │  ├─ GET /api/download-zip/<job_id>        │    │   │
│  │  │  └─ GET /api/health                        │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                      ↑                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │ Network
                       │ (localhost:5000 or remote)
                       │
┌──────────────────────┴───────────────────────────────────────┐
│                  Flask Web Server (Backend)                  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  app.py (Flask Application)                          │   │
│  │                                                       │   │
│  │  ├─ Route Handlers:                                 │   │
│  │  │  ├─ @app.route('/')                              │   │
│  │  │  │  └─ Serves index.html                         │   │
│  │  │  │                                                │   │
│  │  │  ├─ @app.route('/api/generate', POST)           │   │
│  │  │  │  ├─ Parse form data                           │   │
│  │  │  │  ├─ Validate input                            │   │
│  │  │  │  ├─ Call STL Generator                        │   │
│  │  │  │  ├─ Write files to disk                       │   │
│  │  │  │  └─ Return job info                           │   │
│  │  │  │                                                │   │
│  │  │  ├─ @app.route('/api/download/...', GET)       │   │
│  │  │  │  └─ Stream file to client                     │   │
│  │  │  │                                                │   │
│  │  │  └─ ... other routes ...                         │   │
│  │  │                                                   │   │
│  │  ├─ Error Handlers:                                 │   │
│  │  │  ├─ 404 Not Found                                │   │
│  │  │  └─ 500 Server Error                             │   │
│  │  │                                                   │   │
│  │  └─ Utilities:                                      │   │
│  │     ├─ cleanup_old_jobs()                           │   │
│  │     └─ CORS Configuration                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  stl_generator.py (STL Generation Engine)            │   │
│  │                                                       │   │
│  │  ├─ RackMountGenerator Class:                        │   │
│  │  │  ├─ __init__(width, height, depth, ...)         │   │
│  │  │  ├─ create_bracket(side='left'|'right')         │   │
│  │  │  │  ├─ Define front/back vertices               │   │
│  │  │  │  ├─ Create inner cavity                       │   │
│  │  │  │  ├─ Generate triangle faces                   │   │
│  │  │  │  ├─ Connect all faces                         │   │
│  │  │  │  └─ Return triangle array                     │   │
│  │  │  │                                                │   │
│  │  │  ├─ create_retention_clip()                      │   │
│  │  │  ├─ create_support_posts()                       │   │
│  │  │  └─ generate_all_parts()                         │   │
│  │  │                                                   │   │
│  │  ├─ STLWriter Class:                                │   │
│  │  │  ├─ write_stl() - ASCII format                   │   │
│  │  │  └─ write_binary_stl() - Binary format           │   │
│  │  │                                                   │   │
│  │  ├─ calculate_print_stats()                         │   │
│  │  │  └─ Returns: volume, weight, print_time         │   │
│  │  │                                                   │   │
│  │  └─ generate_assembly_guide()                       │   │
│  │     └─ Outputs: ASSEMBLY_GUIDE.md                   │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                      ↓                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  File System (Temporary Storage)                     │   │
│  │                                                       │   │
│  │  /tmp/rack_mounts/                                   │   │
│  │  └─ mount_20240115_143025/                           │   │
│  │     ├─ bracket_left.stl                             │   │
│  │     ├─ bracket_right.stl                            │   │
│  │     ├─ retention_clip.stl                           │   │
│  │     ├─ support_posts.stl                            │   │
│  │     ├─ ASSEMBLY_GUIDE.md                            │   │
│  │     └─ config.json                                  │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Generation Workflow
```
User Input (Form)
    ↓
Form Validation (JavaScript)
    ↓
POST /api/generate
    ↓
Backend Validation
    ↓
RackMountGenerator.generate_all_parts()
    ├─ create_bracket('left')
    ├─ create_bracket('right')
    ├─ create_retention_clip()
    └─ create_support_posts()
    ↓
STLWriter.write_binary_stl() ×4
    ↓
generate_assembly_guide()
    ↓
Save config.json
    ↓
Return job_id + file_info
    ↓
Display download buttons
    ↓
User clicks download
    ↓
GET /api/download/<job_id>/<file>
    ↓
Stream file to browser
    ↓
Save STL to computer
```

## Module Dependencies

```
Frontend Dependencies:
├─ Three.js (r128) - 3D rendering
│  └─ WebGL 2.0
└─ Built-in Browser APIs
   ├─ Fetch API
   ├─ FormData
   └─ Canvas/WebGL

Backend Dependencies:
├─ Flask (3.0.0) - Web framework
├─ Flask-CORS (4.0.0) - CORS support
├─ NumPy (1.24.3) - Numerical operations
├─ Werkzeug (3.0.1) - WSGI utilities
└─ Python standard library
   ├─ os (file operations)
   ├─ json (config storage)
   ├─ tempfile (temporary files)
   ├─ shutil (directory operations)
   └─ zipfile (archive creation)
```

## File Structure

```
rack_mount_generator/
│
├── Frontend Files
│   └─ index.html ........................ Main web interface
│      ├─ Form elements
│      ├─ Three.js scene setup
│      ├─ Real-time preview rendering
│      └─ API communication
│
├── Backend Files
│   ├─ app.py ........................... Flask server
│   │  ├─ Route handlers
│   │  ├─ API endpoints
│   │  ├─ File management
│   │  └─ Job cleanup
│   │
│   └─ stl_generator.py ................. STL generation
│      ├─ RackMountGenerator class
│      ├─ Geometry algorithms
│      ├─ STLWriter class
│      └─ Statistics calculation
│
├── Configuration & Setup
│   ├─ requirements.txt ................. Python dependencies
│   ├─ run.sh ........................... Startup script (Unix)
│   └─ run.bat .......................... Startup script (Windows)
│
├── Testing
│   ├─ test_generator.py ............... Test suite
│   └─ verify_setup.py ................. Setup verification
│
└── Documentation
    ├─ README.md ....................... User documentation
    ├─ QUICKSTART.md ................... Quick start guide
    ├─ DEVELOPMENT.md .................. Developer guide
    ├─ ARCHITECTURE.md ................. This file
    └─ PROTOTYPE_SUMMARY.md ............ Project overview
```

## Class Architecture

### RackMountGenerator Class
```python
class RackMountGenerator:
    def __init__(self, device_width, device_height, device_depth,
                 tolerance=2.0, wall_thickness=3.0,
                 add_support=True, add_rack_holes=False)

    def create_bracket(side='left') -> np.ndarray
        # Generates left or right bracket geometry
        # Returns: Triangle array (N×3×3)

    def _add_mounting_rails(vertices, triangles, side)
        # Adds 19" rack mounting hole patterns
        # Optional feature

    def create_retention_clip() -> np.ndarray
        # Generates front-facing retention clip
        # Returns: Triangle array

    def create_support_posts() -> np.ndarray
        # Generates underside support posts
        # Returns: Triangle array (if enabled)

    def generate_all_parts() -> Dict[str, np.ndarray]
        # Orchestrates generation of all parts
        # Returns: Dictionary of all parts
```

### STLWriter Class
```python
class STLWriter:
    @staticmethod
    def write_stl(filename, triangles, name='part')
        # Write ASCII STL format
        # Larger file size, text-based

    @staticmethod
    def write_binary_stl(filename, triangles, name='part')
        # Write binary STL format
        # Smaller file size, binary format (recommended)
```

## Algorithm Overview

### Bracket Generation Algorithm

1. **Define Coordinate System**
   ```
   X-axis: Left-Right (Width)
   Y-axis: Up-Down (Height)
   Z-axis: Front-Back (Depth)
   ```

2. **Calculate Dimensions**
   ```
   Outer width = Device Width + 2×(Tolerance + Wall Thickness)
   Outer height = Device Height + 2×(Tolerance + Wall Thickness)
   Thickness = Wall Thickness
   ```

3. **Create Front Face Vertices**
   ```
   Front face has 8 vertices:
   - 4 outer corners: (0,0), (w,0), (w,h), (0,h)
   - 4 inner corners: forms device cavity
   ```

4. **Create Back Face Vertices**
   ```
   Mirror of front face at Z = -thickness
   ```

5. **Generate Triangle Faces**
   ```
   For each face (top, bottom, left, right, front, back):
   - Create 2 triangles per rectangular face
   - Ensure proper orientation (outward-facing normals)
   ```

6. **Connect Front & Back**
   ```
   Create edge triangles connecting front and back faces
   - Outer perimeter edges
   - Inner cavity edges
   ```

### Geometry Example (Simple 2D cross-section)

```
Front View (Y-Z plane):
┌─────────────────┐
│ Outer bracket   │
│ ┌──────────────┐│  ← Device cavity
│ │  Device here ││
│ └──────────────┘│
└─────────────────┘
 ▲
 Bracket wall thickness (3mm)

3D: Depth extends backward (Z-axis)
```

## STL Format Structure

### Binary STL Format
```
[Header (80 bytes)]
[Number of triangles (4 bytes, uint32)]
[For each triangle:]
  [Normal vector (12 bytes, 3×float32)]
  [Vertex 1 (12 bytes, 3×float32)]
  [Vertex 2 (12 bytes, 3×float32)]
  [Vertex 3 (12 bytes, 3×float32)]
  [Attribute byte count (2 bytes)]
```

### Normal Vector Calculation
```python
v1 = triangle[1] - triangle[0]
v2 = triangle[2] - triangle[0]
normal = cross_product(v1, v2)
normal = normalize(normal)
```

## API Response Schema

### Success Response
```json
{
  "success": true,
  "job_id": "20240115_143025",
  "files": [
    {
      "name": "bracket_left.stl",
      "path": "/tmp/rack_mounts/mount_20240115_143025/bracket_left.stl",
      "size_bytes": 2500000,
      "size_mb": 2.4,
      "triangles": 8524,
      "material_cm3": 15.3,
      "weight_g": 18.9,
      "print_time_h": 4.2
    }
  ],
  "stats": {
    "total_weight_g": 45.2,
    "total_time_h": 12.4,
    "total_parts": 3
  }
}
```

### Error Response
```json
{
  "error": "Descriptive error message"
}
```

## Performance Optimization

### Frontend Optimization
- **Three.js**: Indexed geometry reduces memory
- **Caching**: 3D scenes cached when possible
- **Lazy Loading**: Three.js library loaded async
- **WebGL**: Hardware-accelerated rendering

### Backend Optimization
- **NumPy Arrays**: Fast numerical operations
- **Binary STL**: 50% smaller than ASCII
- **Memory Mapping**: Large files handled efficiently
- **Job Cleanup**: Automatic removal prevents disk bloat

### Network Optimization
- **Compression**: ZIP files reduce download size
- **Streaming**: Large files streamed (not buffered)
- **CORS**: Efficient cross-origin requests
- **Caching**: Browser caches static files

## Scalability Considerations

### Current Capacity
- **Simultaneous users**: 10+ (limited by server hardware)
- **Job queue**: Unlimited (async processing ready)
- **Storage**: 24-hour auto-cleanup
- **Memory**: ~100MB per concurrent job

### Scaling Strategies

1. **Horizontal Scaling**
   ```
   Load Balancer
   ├─ App Server 1
   ├─ App Server 2
   └─ App Server 3
   ```

2. **Async Processing**
   ```
   Flask App → Celery Task Queue → Worker
   ```

3. **File Storage**
   ```
   Local Filesystem → S3/Cloud Storage
   ```

4. **Caching Layer**
   ```
   Redis Cache → Frequently Generated Mounts
   ```

## Security Architecture

### Input Validation
```
User Input → Type Check → Range Check → Sanitize → Process
```

### File Security
```
Generated Files → Isolated Directory → User Download → Auto-Delete
```

### API Security
```
Request → CORS Check → Input Validate → Process → Response
```

## Testing Architecture

### Unit Tests
```
test_basic_generation() → Verify core functionality
test_different_sizes() → Validate range support
test_tolerances() → Check parameter variations
test_infill_settings() → Verify calculation accuracy
test_file_generation() → Ensure file creation
test_edge_cases() → Handle boundary conditions
```

### Integration Tests
```
Form Input → API Call → File Generation → Verification
```

### Manual Testing
```
Browser Access → Form Submission → File Download → Slicer Verification
```

## Deployment Architecture

### Development
```
Python app.py → localhost:5000
```

### Production
```
Nginx (Reverse Proxy) → Gunicorn (App Server) → Flask App
                     ↓
               /tmp/rack_mounts/ (Storage)
```

### Docker
```
Dockerfile → Docker Image → Container → Port 5000
```

### Cloud
```
GitHub → CI/CD Pipeline → Cloud Platform → Running Instance
```

---

## Conclusion

The architecture is designed to be:
- ✅ **Modular**: Components can be updated independently
- ✅ **Scalable**: Ready for horizontal scaling
- ✅ **Maintainable**: Clean separation of concerns
- ✅ **Extensible**: Easy to add new features
- ✅ **Performant**: Optimized for speed
- ✅ **Secure**: Input validation and isolation

This design allows for easy enhancement and deployment in various environments while maintaining code quality and performance.
