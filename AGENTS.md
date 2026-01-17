# AI Agent Instructions - 19" Rack Mount Generator

## Project Context

This project generates 3D-printable STL files for mounting devices in standard 19-inch server racks. It uses a web interface with real-time 3D preview and client-side STL export.

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | HTML5 + Vanilla JS | User interface |
| 3D Preview | Three.js r128 | Real-time visualization |
| STL Export | THREE.STLExporter | Client-side file generation |
| Server | Flask 3.0 | Static file serving |
| Package Manager | uv | Python dependency management |

## Repository Structure

```
rack_mount_generator/
├── index.html          # Complete frontend (form, preview, export)
├── app.py              # Flask server
├── stl_generator.py    # Legacy Python STL generator (unused)
├── pyproject.toml      # Python dependencies
├── requirements.txt    # Pip requirements (backup)
├── run.sh / run.bat    # Startup scripts
├── README.md           # User documentation
├── CLAUDE.md           # Claude-specific instructions
├── AGENTS.md           # This file
├── ARCHITECTURE.md     # System architecture
├── DEVELOPMENT.md      # Development guide
└── QUICKSTART.md       # Quick start guide
```

## Critical Design Decisions

### 1. Client-Side STL Export
**Decision**: Export STL directly from Three.js preview instead of server-side Python generation.

**Rationale**: Server-side STL generation had persistent issues:
- Triangle normals pointing wrong direction
- Boolean subtraction for holes not working
- Geometry mismatches between preview and export

**Implementation**: Three.js `STLExporter` exports exactly what's rendered in preview.

### 2. Holes via Shape.holes
**Decision**: Create holes using `THREE.Shape.holes` array with `THREE.Path`.

**Wrong approach**:
```javascript
// DON'T DO THIS - creates solid cylinder
const holeGeom = new THREE.CylinderGeometry(r, r, depth, 16);
group.add(new THREE.Mesh(holeGeom, material));
```

**Correct approach**:
```javascript
// DO THIS - creates actual hole
const shape = new THREE.Shape();
shape.moveTo(x1, y1);
// ... define outer boundary

const holePath = new THREE.Path();
holePath.absarc(cx, cy, radius, 0, Math.PI * 2, true);
shape.holes.push(holePath);

const geom = new THREE.ExtrudeGeometry(shape, settings);
```

### 3. Half-Width Faceplate
**Decision**: Generate half-width (225mm) faceplates instead of full 19" width.

**Rationale**: 
- Fits on standard 3D printer beds (typically 200-250mm)
- Two brackets connect via joining flange with M3 screws
- Easier to print, ship, and handle

## Key Geometry Components

### Faceplate
- Width: 225mm (half of 450mm rack inner width)
- Height: Calculated from device height (rounds up to nearest U)
- Thickness: Configurable (default 10mm)
- Contains rectangular cutout for device

### Rack Ear
- Width: 15.875mm (standard)
- Contains M6 mounting holes (3 per rack unit)
- Position: Left or right side (user configurable)

### Joining Flange
- On opposite edge from ear
- 50.8mm depth (2 inches into rack)
- Contains M3 horizontal holes for connecting two brackets

### Support Shelf
- Sits below device cutout
- Depth: Device depth + 10mm
- Has triangular gussets for strength

### Flange Gussets
- Connect faceplate back to joining flange
- Triangular (right-angle) shape
- Top and bottom of faceplate
- Bottom gusset raised 10mm from edge

## Modification Guidelines

### Adding New Features
1. **UI Changes**: Edit HTML form in `index.html` (lines ~300-490)
2. **Preview Logic**: Edit `generateMountGeometry()` function
3. **Event Binding**: Add field ID to event listener array
4. **Export**: Automatic - anything in `mountMesh` group gets exported

### Changing Dimensions
All dimension constants are at top of `generateMountGeometry()`:
```javascript
const RACK_HALF_WIDTH = 225.0;
const RACK_UNIT_HEIGHT = 44.45;
const DEVICE_HEIGHT_PER_U = 35.0;
const EAR_WIDTH = 15.875;
```

### Testing Workflow
1. Start server: `uv run python app.py`
2. Open browser: `http://localhost:5001`
3. Make changes to `index.html`
4. Refresh browser (server hot-reloads)
5. Test preview updates with different parameters
6. Export STL and verify in slicer software

## Known Issues & Workarounds

| Issue | Workaround |
|-------|------------|
| Port 5000 blocked on macOS | Use port 5001 |
| Legacy Python generator broken | Don't use - use client-side export |
| Server auto-reload fails | Manually restart with `pkill` then run again |

## Environment Setup

```bash
# Prerequisites: Python 3.11+, uv package manager

# Clone repository
git clone git@github.com:leprachuan/rack-mount-generator.git
cd rack-mount-generator

# Install dependencies and run
uv sync
uv run python app.py

# Open in browser
open http://localhost:5001
```

## Commit Guidelines

**Always commit these files together**:
- `index.html` - Frontend changes
- `app.py` - Server changes (if modified)
- `*.md` - Documentation updates

**Commit message format**:
```
feat: Add configurable gusset size
fix: Correct rack hole positions
docs: Update CLAUDE.md with new geometry info
```

## Contact & Resources

- **Three.js Docs**: https://threejs.org/docs/
- **STL Format Spec**: https://en.wikipedia.org/wiki/STL_(file_format)
- **19" Rack Standards**: EIA-310-D
