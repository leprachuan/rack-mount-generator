# 19" Rack Mount Generator

A web-based tool for generating customized 3D-printable mounting brackets for devices in standard 19-inch server racks.

![Preview](https://img.shields.io/badge/3D-Preview-blue) ![STL Export](https://img.shields.io/badge/Export-STL-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

✨ **Real-Time 3D Preview**
- Interactive Three.js visualization
- Rotate, pan, and zoom to inspect your design
- Device shown as semi-transparent overlay

🔧 **Customizable Parameters**
- Device dimensions (width, height, depth)
- Tolerance for easy insertion/removal
- Wall thickness and structural options
- Left or right rack ear positioning

📐 **Structural Components**
- Half-width faceplate (225mm) - fits standard printer beds
- Rack ear with M6 mounting holes (3 per U)
- Joining flange with M3 holes to connect two brackets
- Support shelf with triangular gussets
- Blank panel mode for solid faceplates

📦 **Instant STL Export**
- What-you-see-is-what-you-get export
- Binary STL format for efficiency
- Direct browser download - no server processing

## Quick Start

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/leprachuan/rack-mount-generator.git
cd rack-mount-generator

# Using uv (recommended)
uv sync
uv run python app.py

# OR using pip
pip install -r requirements.txt
python app.py
```

### Open in Browser

Navigate to: **http://localhost:5001**

> **Note**: The app uses port 5001 because port 5000 is often blocked on macOS by AirPlay/ControlCenter.

## Usage Guide

### Step 1: Enter Device Dimensions

| Field | Description | Example |
|-------|-------------|---------|
| Width | Horizontal width of your device | 150mm |
| Height | Vertical height (44mm = 1U) | 44mm |
| Depth | How far device extends into rack | 200mm |

### Step 2: Configure Mount Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Tolerance | Gap around device for easy insertion | 2mm |
| Wall Thickness | Faceplate material thickness | 10mm |
| Shelf Thickness | Support shelf thickness | 5mm |
| Flange Thickness | Joining flange width | 5mm |
| Gusset Size | Triangular support size | 15mm |

### Step 3: Choose Options

- **Add Support Shelf**: Creates a shelf below the device opening
- **Add Rack Holes**: Adds M6 mounting holes to the rack ear
- **Ear Side**: Position rack ear on left or right
- **Blank Panel**: Creates solid faceplate (no cutout)

### Step 4: Generate & Download

1. Click **"Generate STL Files"**
2. Preview updates in real-time
3. STL file downloads automatically
4. Open in your slicer software (PrusaSlicer, Cura, etc.)

## Printing Recommendations

### Material
| Material | Best For | Notes |
|----------|----------|-------|
| PLA | Prototypes, light loads | Easy to print, may warp in heat |
| PETG | General use | Good strength, slight flexibility |
| ABS | High stress | Strongest, requires enclosure |

### Print Settings
- **Layer Height**: 0.2mm (standard) or 0.15mm (detailed)
- **Infill**: 20-30% for normal use, 50%+ for heavy devices
- **Walls**: 3-4 perimeters recommended
- **Supports**: Not needed - designed to print flat

### Orientation
Print with the faceplate flat on the bed (front face down).

## Assembly

### Mounting a Single Bracket
1. Print the bracket with your chosen settings
2. Insert M6 cage nuts or use clip nuts on rack rails
3. Slide device into the bracket opening
4. Secure bracket to rack with M6 bolts

### Connecting Two Half-Width Brackets
1. Print left bracket (ear on left side)
2. Print right bracket (ear on right side)
3. Align the joining flanges together
4. Insert M3 screws through horizontal holes
5. Secure with M3 nuts
6. Mount assembled full-width bracket to rack

## Technical Specifications

### Rack Standards
- **Standard**: EIA-310-D
- **Rail Spacing**: 450mm (inner width)
- **Unit Height**: 44.45mm (1U)
- **Mounting Holes**: M6 (6.35mm diameter)

### Generated Bracket Dimensions
- **Faceplate Width**: 225mm (half-width design)
- **Rack Ear Width**: 15.875mm (5/8")
- **Joining Flange Depth**: 50.8mm (2")
- **M3 Joining Holes**: 3.2mm diameter

### Hole Patterns
- **Rack Ear**: 3 holes per U at standard positions (6.35mm, 22.225mm, 38.1mm from U bottom)
- **Joining Flange**: 2 rows of holes (near front and back of flange)

### Material Recommendations
| Material | Best For | Notes |
|----------|----------|-------|
| PLA | Prototypes, light loads | Easy to print, 60°C limit |
| PETG | General use | Good strength, slight flexibility |
| ABS | High stress | Strongest, requires enclosure |

## Troubleshooting

### Device Too Tight
- Increase tolerance (try 3-4mm)
- Check for warping during print
- Sand edges if needed

### Bracket Flexes Under Load
- Increase wall thickness
- Use higher infill percentage
- Switch to PETG or ABS material
- Add support shelf option

### Holes Don't Align with Rack
- Verify your rack follows EIA-310-D standard
- Some racks use #10-32 instead of M6 - holes should still work

### Preview Doesn't Update
- Refresh the browser page
- Check browser console for JavaScript errors
- Ensure all input values are valid numbers

## Project Structure

```
rack_mount_generator/
├── index.html          # Web interface with Three.js preview & STL export
├── app.py              # Flask server (serves static files)
├── stl_generator.py    # Legacy Python STL generator (unused)
├── requirements.txt    # Python dependencies
├── pyproject.toml      # uv/pip project configuration
├── README.md           # This file
├── ARCHITECTURE.md     # Technical architecture details
├── DEVELOPMENT.md      # Development guide
├── AGENTS.md           # AI agent instructions
└── CLAUDE.md           # Claude-specific implementation notes
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and contribution guidelines.

See [ARCHITECTURE.md](ARCHITECTURE.md) for technical architecture details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- How to report bugs
- How to suggest features
- Pull request process
- Code style expectations

For branch protection and release information, see [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md).

## Developer Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and code structure
- **[AGENTS.md](AGENTS.md)** - AI agent instructions for code generation
- **[CLAUDE.md](CLAUDE.md)** - Claude AI specific implementation details

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Three.js](https://threejs.org/) for 3D visualization and STL export
- [Flask](https://flask.palletsprojects.com/) for the web server
- The 3D printing community for dimension standards

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready - Client-side STL Export
