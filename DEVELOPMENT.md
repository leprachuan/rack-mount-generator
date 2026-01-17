# Development Guide - 19" Rack Mount Generator

## Architecture Overview (v2.0)

> **Important**: As of v2.0, STL generation is entirely client-side using Three.js and STLExporter. The Python backend only serves static files.

### Frontend (index.html) - THE COMPLETE APPLICATION
- **Framework**: Vanilla JavaScript + Three.js r128
- **STL Export**: THREE.STLExporter (client-side)
- **Features**:
  - Real-time 3D visualization using Three.js
  - OrbitControls for interactive viewing
  - Form validation
  - Direct STL export from Three.js scene
  - No server round-trip for generation

### Backend (app.py) - MINIMAL
- **Framework**: Flask 3.0
- **Features**:
  - Serves index.html
  - Port 5001 (5000 blocked on macOS)
  - Legacy API endpoints (unused)

### STL Engine (stl_generator.py) - LEGACY
- **Status**: NOT USED for production
- **Note**: Kept for reference; had issues with gusset orientation and hole subtraction
- **Replacement**: Client-side Three.js geometry + STLExporter

## Code Structure

### Frontend Components (index.html)

#### Scene Initialization
```javascript
function initScene() {
  // Creates Three.js scene with lighting
  // Sets up OrbitControls for camera manipulation
  // Configures renderer with antialiasing
}
```

#### Preview Update
```javascript
function updatePreview() {
  // Called when any input changes
  // Regenerates all Three.js geometry
  // Updates scene immediately
}
```

#### Geometry Creation Functions
```javascript
function createFaceplate()    // Main bracket body with device cutout
function createRackEar()      // Side ear with M6 holes (uses Shape.holes)
function createShelf()        // Support shelf below device
function createGussets()      // Triangular supports for shelf
function createJoiningFlange() // Flange with M3 holes for connecting brackets
```

#### STL Export
```javascript
function downloadSTLFromPreview() {
  // Uses THREE.STLExporter to convert scene to binary STL
  // Creates Blob and triggers download
  // What-you-see-is-what-you-get export
}
```

### Critical Implementation: Rack Ear Holes

The rack ear uses `THREE.Shape` with `Shape.holes` for proper hole cutouts:

```javascript
function createRackEar() {
  const shape = new THREE.Shape();
  // Draw outer rectangle
  shape.moveTo(...);
  shape.lineTo(...);
  
  // Add holes using THREE.Path with absarc
  const holePath = new THREE.Path();
  holePath.absarc(x, y, radius, 0, Math.PI * 2, false);
  shape.holes.push(holePath);
  
  // Extrude creates actual holes
  const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
}
```

**Why this matters**: Using cylinder meshes would ADD geometry instead of subtracting it. Shape.holes is the correct Three.js approach for creating actual holes.

#### STLWriter Class
Handles STL file output in both ASCII and binary formats.

**Methods**:
- `write_stl()`: ASCII format (larger files)
- `write_binary_stl()`: Binary format (recommended)

#### Statistics Functions
```python
def calculate_print_stats(triangles, infill=20):
    # Returns dictionary with:
    # - volume_cm3
    # - material_volume_cm3
    # - weight_grams
    # - print_time_hours
    # - triangle_count
```

## Geometry Generation

### Bracket Creation Algorithm

1. **Define vertices** for front and back faces
2. **Create inner cavity** for device mounting
3. **Generate triangles** for:
   - Front face (with hole for device)
   - Back face
   - Side walls
   - Edge connections

4. **Apply transformations** for left/right orientation

### Triangle Definition
```python
# Triangles defined as N×3×3 array
# Each row: [v1, v2, v3] where vi = [x, y, z]
triangles = np.array([
    [[0, 0, 0], [1, 0, 0], [1, 1, 0]],  # Triangle 1
    [[0, 0, 0], [1, 1, 0], [0, 1, 0]],  # Triangle 2
])
```

### Normal Calculation
```python
# Normal vectors calculated for each triangle
v1 = triangle[1] - triangle[0]
v2 = triangle[2] - triangle[0]
normal = np.cross(v1, v2)
normal = normal / np.linalg.norm(normal)  # Normalize
```

## API Endpoints

### POST /api/generate
Generates mount files from configuration.

**Request**:
```json
{
  "width": 100,
  "height": 44,
  "depth": 200,
  "tolerance": 2,
  "wallThickness": 3,
  "addSupport": true,
  "addRackHoles": false,
  "infill": 20,
  "bedSize": "prusa"
}
```

**Response** (Success):
```json
{
  "success": true,
  "job_id": "20240115_143025",
  "files": [...],
  "stats": {...}
}
```

**Response** (Error):
```json
{
  "error": "Description of error"
}
```

### GET /api/download/<job_id>/<filename>
Downloads a single STL file.

### GET /api/download-zip/<job_id>
Downloads all files as ZIP archive.

### GET /api/health
Health check endpoint.

## Database/Storage

### File Organization
```
/tmp/rack_mounts/
├── mount_20240115_143025/
│   ├── bracket_left.stl
│   ├── bracket_right.stl
│   ├── retention_clip.stl
│   ├── support_posts.stl
│   ├── ASSEMBLY_GUIDE.md
│   └── config.json
└── mount_20240115_144530/
    └── ...
```

### Config File Format
```json
{
  "width": 100,
  "height": 44,
  "depth": 200,
  "tolerance": 2,
  "wall_thickness": 3,
  "add_support": true,
  "add_rack_holes": false,
  "infill": 20,
  "timestamp": "2024-01-15T14:30:25.123456"
}
```

## Performance Optimization

### Current Implementation
- **Geometry complexity**: O(1) - fixed triangle count per part
- **File I/O**: Sequential writes with buffering
- **Memory usage**: Typically <100MB per job

### Optimization Opportunities
1. **Async processing**: Use Celery for long-running jobs
2. **Caching**: Cache commonly used configurations
3. **Streaming**: Stream large files instead of loading in memory
4. **Compression**: Use gzip for file transfer

### Memory Management
- Jobs automatically cleaned after 24 hours
- Temporary files stored in system temp directory
- ZIP downloads streamed directly (not buffered)

## Testing

### Unit Tests
```python
# Test bracket generation
def test_bracket_generation():
    gen = RackMountGenerator(100, 44, 200)
    parts = gen.generate_all_parts()
    assert 'bracket_left' in parts
    assert len(parts['bracket_left']) > 0
```

### Integration Tests
```bash
# Test full workflow
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"width": 100, "height": 44, "depth": 200, ...}'
```

### Manual Testing
1. **Input validation**: Try edge cases (0mm, 500mm, negative values)
2. **File generation**: Verify STL files are valid
3. **3D preview**: Check visualization accuracy
4. **Print stats**: Validate calculations

## Extending the Generator

### Adding a New Bracket Type

1. **Add method to RackMountGenerator**:
```python
def create_custom_bracket(self):
    triangles = []
    # Generate geometry
    return np.array(triangles)
```

2. **Update generate_all_parts()**:
```python
def generate_all_parts(self):
    parts = {
        'custom_bracket': self.create_custom_bracket(),
        # ... existing parts
    }
    return parts
```

3. **Update frontend** (optional):
```javascript
// Add checkbox in form
<input type="checkbox" id="addCustom">
```

### Adding Printer Profiles

1. **Update bedSize options in HTML**:
```html
<option value="my_printer">My Printer (300x300mm)</option>
```

2. **Handle in JavaScript**:
```javascript
document.getElementById('bedSize').addEventListener('change', (e) => {
  // Handle custom bed size
});
```

## Debugging

### Python Debugging
```python
# Add breakpoints
import pdb
pdb.set_trace()

# Or use VS Code debugging
# Add .vscode/launch.json for remote debugging
```

### Frontend Debugging
```javascript
// Console logging
console.log('Debug info:', variableName);

// Chrome DevTools
// - F12 to open
// - Inspect element
// - Console for errors
// - Network tab for API calls
```

### STL Validation
```python
# Check if STL is valid
import subprocess
# Validate with external tools
subprocess.run(['cura', 'file.stl'])
```

## Browser Compatibility

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (15.2+)
- **Mobile**: Limited support (small screen)

### WebGL Requirements
- OpenGL 2.0 or higher
- 256MB VRAM minimum
- Modern browser engine

## Dependencies and Versions

### Critical Dependencies
- **Flask** 3.0.0+: Core web framework
- **NumPy** 1.24.3+: Numerical calculations
- **Three.js** r128: 3D rendering

### Why These Versions?
- Compatibility with Python 3.8+
- Support for binary operations
- WebGL 2.0 support in Three.js

## Common Issues & Solutions

### Issue: "Module not found: stl_generator"
**Solution**: Ensure `stl_generator.py` is in same directory as `app.py`

### Issue: "Port 5000 already in use"
**Solution**:
```bash
# Find process on port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
# Or use different port
python app.py --port 5001
```

### Issue: "3D preview not loading"
**Solution**:
1. Check browser console for errors (F12)
2. Verify Three.js CDN is accessible
3. Check WebGL support

### Issue: "STL files invalid/not sliceable"
**Solution**:
1. Verify file is binary STL (not ASCII)
2. Check triangle orientation (normals)
3. Use Cura to repair mesh

## Performance Benchmarks

### Typical Timings
- **Mount generation**: <500ms
- **STL writing**: <1s
- **File download**: <5s (10MB file)
- **Preview rendering**: 60fps (with auto-rotate)

### Resource Usage
- **Memory**: 50-100MB per job
- **Disk**: 10-20MB per complete job
- **CPU**: Peak during STL generation

## Future Roadmap

### Short Term (v1.1)
- [ ] Add multi-part automatic splitting
- [ ] STEP file export
- [ ] Email delivery of files
- [ ] Project history/favorites

### Medium Term (v1.5)
- [ ] Web-based slicer integration
- [ ] Real-time print cost estimation
- [ ] Material database
- [ ] Batch generation

### Long Term (v2.0)
- [ ] AI-powered design recommendations
- [ ] Mobile app
- [ ] Cloud storage integration
- [ ] 3D printer API integration

## Contributing Guidelines

1. **Code Style**: Follow PEP 8 for Python
2. **Commenting**: Add docstrings to all functions
3. **Testing**: Write tests for new features
4. **Documentation**: Update README for user-facing changes
5. **Commits**: Clear, descriptive commit messages

## Security Considerations

### Input Validation
- All numeric inputs validated for range
- File paths checked for directory traversal
- JSON sanitization for API responses

### File Security
- Temporary files cleared after 24 hours
- No sensitive data in logs
- CORS properly configured

### HTTPS Deployment
For production:
```bash
# Use reverse proxy (nginx/Apache)
# Enable SSL/TLS
# Add authentication if needed
```

---

**Last Updated**: January 2024
**Version**: 1.0.0
