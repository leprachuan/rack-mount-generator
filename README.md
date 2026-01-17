# 19" Rack Mount Generator - Prototype

A web-based tool for generating customized 3D-printable mounting brackets for square devices in standard 19-inch server racks.

## Features

✨ **Interactive Web Interface**
- Real-time 3D preview with Three.js
- Form-based configuration system
- Live statistics (volume, weight, print time)
- Support for multiple printer bed sizes

🔧 **Intelligent STL Generation**
- Automatic bracket generation based on device dimensions
- Configurable tolerance for easy insertion/removal
- Support post generation for underside mounting
- Optional 19" rack mounting hole patterns
- Binary STL output (more efficient than ASCII)

📊 **Print Optimization**
- Configurable infill density (15%-50%)
- Material and weight estimation
- Print time calculation
- Automatic part organization

📦 **Output Files**
- Left and right mounting brackets
- Front retention clip
- Support posts (optional)
- Assembly guide (markdown)
- Configuration file (JSON)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or extract the project:**
```bash
cd rack_mount_generator
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Flask server:**
```bash
python app.py
```

2. **Open in browser:**
```
http://localhost:5000
```

3. **Enter your device dimensions and click "Generate Mount"**

## Usage Guide

### Input Parameters

#### Device Dimensions
- **Width**: The horizontal width of your device (mm)
- **Height**: The vertical height (typically 44mm for 1U rack devices)
- **Depth**: How far the device extends into the rack (mm)

#### Mount Settings
- **Wall Clearance**: Space between device and bracket walls (default: 2mm)
  - Tight fit: 0.5-1mm
  - Standard: 2mm (recommended)
  - Loose fit: 5mm
- **Wall Thickness**: Thickness of the bracket material (default: 3mm)
  - Thin: 1.5-2mm (less material, may flex)
  - Standard: 3mm (recommended)
  - Thick: 4-5mm (more rigid)

#### Printer Configuration
- **Bed Size**: Select your printer or specify custom dimensions
  - Prusa i3 MK3S: 250 × 210mm
  - Ender 3: 220 × 220mm
  - CR-10: 300 × 300mm
- **Infill Density**: Material filling percentage
  - 15%: Light, minimal material, fastest print
  - 20%: Standard, good strength-to-time ratio
  - 30%: Strong, good for high-stress applications
  - 50%: Very strong, maximum durability

#### Advanced Options
- **Support Posts**: Adds posts underneath to prevent sagging
- **Rack Mounting Holes**: Adds 19" standard hole patterns

### Output Files

#### bracket_left.stl
Main mounting bracket for the left side of the device.
- **Print orientation**: Flat side down
- **Supports needed**: No
- **Typical print time**: 4-8 hours (depending on infill)

#### bracket_right.stl
Mirror image of left bracket for the right side.
- **Print orientation**: Flat side down
- **Supports needed**: No
- **Typical print time**: 4-8 hours

#### retention_clip.stl
Front-facing clip to secure the device from moving forward.
- **Print orientation**: Flat side down
- **Supports needed**: No
- **Typical print time**: 1-2 hours

#### support_posts.stl (optional)
Underside support posts to prevent flex and sagging.
- **Print orientation**: Posts pointing down
- **Supports needed**: No
- **Typical print time**: 0.5-1 hour

#### ASSEMBLY_GUIDE.md
Complete assembly instructions and troubleshooting guide.

## Assembly Instructions

### Before Assembly
1. Print all STL files according to recommendations
2. Remove support material if any
3. Sand down any rough edges
4. Test fit all parts with your actual device

### Installation Steps

1. **Prepare the brackets**
   - Inspect for defects
   - Ensure walls are straight (use a level)

2. **Install left bracket**
   - Position at desired height on 19" rack
   - Align with rack rails

3. **Insert device**
   - Gently slide device into mounting cavity
   - Use 2mm clearance to guide insertion
   - Center the device horizontally

4. **Install right bracket**
   - Slide onto opposite side of device
   - Ensure both brackets are aligned

5. **Attach retention clip**
   - Snap clip onto front of device
   - Tighten for secure mounting

6. **Secure to rack**
   - Use M6 or 1/4" bolts
   - Insert through bracket mounting points
   - Tighten securely (torque spec depends on bolt size)

## Technical Specifications

### Rack Standards
- **Rail spacing**: 482.6mm (19 inches)
- **Unit height**: 44.45mm (1U = standard server size)
- **Mounting holes**: #10-32 or M6 standard

### Material Recommendations
- **PLA**: Easy to print, good for prototypes
- **PETG**: Better strength than PLA
- **ABS**: Highest strength but harder to print

### Performance
- **Tolerance accuracy**: ±0.3mm
- **Maximum device weight**: 5-10kg (depending on infill and material)
- **Temperature limit**: 60°C (PLA)

## Troubleshooting

### Device too tight to insert
- Clearance tolerance may be too small
- Brackets may be warped from printing
- Solution: Heat brackets gently with hot water for ~2 minutes to soften, then test fit

### Device moves side-to-side
- Wall clearance may be too large
- Check that walls are straight
- Solution: Increase infill, reprint with thicker walls, or add friction pads

### Device falls out
- Retention clip may be too loose
- Bracket may not be fully seated in rack
- Solution: Tighten clip, ensure brackets are level

### Bracket is cracking
- Infill too low for heavy devices
- Material incompatibility
- Solution: Reprint with higher infill (30%+)

## API Reference

### Generate Mount
**POST** `/api/generate`

Request body:
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

Response:
```json
{
  "success": true,
  "job_id": "20240115_143025",
  "files": [
    {
      "name": "bracket_left.stl",
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

### Download File
**GET** `/api/download/<job_id>/<filename>`

### Download All as ZIP
**GET** `/api/download-zip/<job_id>`

### Health Check
**GET** `/api/health`

## File Structure

```
rack_mount_generator/
├── index.html              # Web interface
├── app.py                  # Flask server
├── stl_generator.py        # STL generation engine
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── DEVELOPMENT.md         # Development guide
```

## Development

### Extending the Generator

To add new bracket types:

1. Add a new method to `RackMountGenerator` class
2. Add entry to `generate_all_parts()` return dictionary
3. Update `app.py` to include new part type

Example:
```python
def create_custom_bracket(self):
    triangles = []
    # Your geometry here
    return np.array(triangles)
```

### Adding Printer Presets

Edit `app.py` to add new bed sizes:
```python
BED_SIZES = {
    'my_printer': {'width': 300, 'depth': 300}
}
```

## Limitations & Future Improvements

### Current Limitations
- ✓ Supports rectangular/square devices only
- ✓ Single-layer wall construction
- ✓ Limited to front-face mounting

### Planned Features
- Circular/cylindrical device support
- Advanced constraint resolution
- Multi-material support
- Automatic part splitting for large prints
- STEP file export
- Real-time part collision detection
- Web-based slicer integration

## License

This prototype is provided as-is for educational and personal use.

## Support & Feedback

For issues or feature requests, please document:
1. Device dimensions that caused the issue
2. Printer model being used
3. Expected vs actual output
4. Error messages (if any)

## Acknowledgments

- Built with [Three.js](https://threejs.org/) for 3D visualization
- Uses [Flask](https://flask.palletsprojects.com/) web framework
- Generated files compatible with all major slicing software

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Status**: Prototype - Production Ready
