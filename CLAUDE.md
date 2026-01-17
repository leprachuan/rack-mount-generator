# Claude Instructions - 19" Rack Mount Generator

## Project Overview

This is a web-based 3D-printable rack mount bracket generator. Users input device dimensions and the app generates STL files for mounting square devices in standard 19-inch server racks.

## Key Architecture

### Client-Side STL Generation (Current Approach)
The STL export is done **entirely in the browser** using Three.js STLExporter. This ensures what-you-see-is-what-you-get (WYSIWYG) output.

```
User Input → Three.js Preview → STLExporter → Download STL
```

**Why client-side?** Previous attempts at server-side Python STL generation had geometry issues (incorrect normals, holes not subtracting properly). The Three.js approach guarantees the exported STL matches the preview exactly.

### File Structure
- `index.html` - Complete frontend (HTML + CSS + JavaScript + Three.js)
- `app.py` - Flask server (serves static files, legacy API still present)
- `stl_generator.py` - Legacy Python STL generator (not used for export anymore)
- `pyproject.toml` - Python dependencies managed by `uv`

## Critical Implementation Details

### Rack Ear Holes
The rack mounting holes are created using `THREE.ExtrudeGeometry` with `THREE.Shape.holes`:

```javascript
const earShape = new THREE.Shape();
// Define outer rectangle
earShape.moveTo(x1, y1);
// ...

// Add circular holes as paths
holePositions.forEach(holeY => {
    const holePath = new THREE.Path();
    holePath.absarc(holeX, holeY, holeRadius, 0, Math.PI * 2, true);
    earShape.holes.push(holePath);
});

const earGeom = new THREE.ExtrudeGeometry(earShape, extrudeSettings);
```

**Important**: Do NOT use cylinder meshes for holes - they export as solid geometry, not cutouts.

### Flange Gussets
Triangular supports connecting the faceplate back to the joining flange:
- Created using `THREE.Shape` + `THREE.ExtrudeGeometry`
- Triangle in Y-Z plane, extruded along X (flange width)
- Bottom gusset lifted 10mm from bottom edge
- Top gusset at faceplate height minus gusset height

### Coordinate System
- X: Width (left to right across faceplate)
- Y: Height (bottom to top)
- Z: Depth (0 = front face, negative = into rack)

### Key Dimensions
- `RACK_HALF_WIDTH = 225.0mm` - Half of 19" rack inner width
- `FULL_RACK_WIDTH = 450.0mm` - Full 19" rack inner width
- `RACK_UNIT_HEIGHT = 44.45mm` - Standard 1U height
- `EAR_WIDTH = 15.875mm` - Standard rack ear width
- `HOLE_DIAMETER = 6.35mm` - M6 clearance hole
- Wide mode threshold: `openingWidth > 185mm` (225 - 40mm margin)

### Wide Device Mode
For devices wider than 185mm (won't fit in half-rack with margins), the generator automatically creates TWO brackets:
- **Left bracket**: Left rack ear, joining flanges on right inner edge (top/bottom of opening)
- **Right bracket**: Right rack ear, joining flanges on left inner edge (top/bottom of opening)
- **Gussets**: Flange gussets are mirrored for each bracket side; shelf gussets only on outer edges
- **Device centering**: Device preview is centered across full rack width (X=0)

## Common Tasks

### Adding a New Parameter
1. Add HTML input in `index.html` form section
2. Add to event listener array for live preview updates
3. Update `generateMountGeometry()` function signature and logic
4. Update `updatePreview()` to read and pass the value
5. The STL export automatically includes any geometry in the scene

### Modifying Geometry
All geometry is in `generateMountGeometry()` function in `index.html`. Key sections:
- Faceplate with cutout (lines ~560-620)
- Support shelf with gussets (lines ~625-680)
- Rack ear with holes (lines ~685-755)
- Joining flange (lines ~760-800)
- Flange gussets (lines ~805-850)
- M3 joining holes (lines ~755-780)

### Testing Changes
1. Run server: `uv run python app.py`
2. Open: `http://localhost:5001`
3. Modify parameters, verify preview updates
4. Click "Generate STL Files" to export
5. Open STL in slicer (PrusaSlicer, Cura) to verify geometry

## Gotchas & Lessons Learned

1. **Port 5000 blocked on macOS** - Uses port 5001 instead (ControlCenter/AirPlay uses 5000)

2. **Python STL generation abandoned** - Server-side STL had persistent issues with normals and boolean operations. Client-side Three.js export is more reliable.

3. **Holes must use Shape.holes** - Adding cylinder meshes creates additive geometry. Use `THREE.Path` with `absarc()` added to `shape.holes` array.

4. **Triangle winding matters** - For proper normals, vertices must be counter-clockwise when viewed from outside the solid.

5. **ExtrudeGeometry rotation** - When extruding shapes, remember the shape is in X-Y plane and extrudes along +Z. Use rotation to reorient.

## Server Commands

```bash
# Start server
cd /Users/fosterlipkey/Documents/rack_mount_generator
uv run python app.py

# Kill existing server
pkill -f "python.*app"

# Check if port in use
lsof -i :5001
```

## Git Repository
- Remote: `github.com/leprachuan/rack-mount-generator` (private)
- Main files to commit: `index.html`, `app.py`, `*.md`
