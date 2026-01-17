#!/usr/bin/env python3
"""
19" Rack Mount STL Generator
Generates 3D-printable mounting bracket for square devices in 19" racks
- Half-width faceplate (fits printer bed)
- Rectangular hole through faceplate for device
- Support lip below opening
- Standard M6 mounting holes for rack attachment
"""

import numpy as np
from typing import List, Dict, Tuple
import os
import math
from datetime import datetime


class RackMountGenerator:
    """Generate STL files for 19-inch rack mounting brackets"""

    # 19" Rack dimensions (in mm)
    RACK_FULL_WIDTH = 483  # Full 19 inches
    RACK_HALF_WIDTH = 241.5  # Half width (fits printer bed)
    RACK_UNIT_HEIGHT = 44.45  # 1U in mm
    HOLE_PITCH = 10.16  # Distance between mounting holes (0.4")
    HOLE_DIAMETER = 6.35  # M6 clearance hole (0.25")
    HOLE_FROM_EDGE_X = 25.4  # Distance from left/right edge (1")
    HOLE_FROM_EDGE_Y = 6.35  # Distance from top/bottom edge

    def __init__(self,
                 device_width: float,
                 device_height: float,
                 device_depth: float,
                 tolerance: float = 2.0,
                 wall_thickness: float = 3.0,
                 add_support: bool = True,
                 add_rack_holes: bool = True):
        """Initialize the mount generator"""
        self.device_width = device_width
        self.device_height = device_height
        self.device_depth = device_depth
        self.tolerance = tolerance
        self.wall_thickness = wall_thickness
        self.add_support = add_support
        self.add_rack_holes = add_rack_holes

        # Calculate rack units needed (round up)
        self.rack_units = math.ceil(device_height / self.RACK_UNIT_HEIGHT)
        self.faceplate_height = self.rack_units * self.RACK_UNIT_HEIGHT

        # Use half-width for printability
        self.faceplate_width = self.RACK_HALF_WIDTH

        # Device opening dimensions (with tolerance)
        self.opening_width = device_width + 2 * tolerance
        self.opening_height = device_height + 2 * tolerance

        # Center the opening on the faceplate
        self.opening_x = (self.faceplate_width - self.opening_width) / 2
        self.opening_y = (self.faceplate_height - self.opening_height) / 2

        # Support lip dimensions
        self.lip_thickness = wall_thickness
        self.lip_depth = device_depth + 10  # Extends 10mm past device depth

    def create_box_hole(self, triangles: List, x: float, y: float, z: float, 
                       width: float, height: float, depth: float):
        """Create a rectangular hole through a solid by defining its edges"""
        # Front opening (at z=0)
        # Top edge
        triangles.append([[x, y + height, z], [x + width, y + height, z], [x + width, y + height, -depth]])
        triangles.append([[x, y + height, z], [x + width, y + height, -depth], [x, y + height, -depth]])
        
        # Bottom edge
        triangles.append([[x, y, z], [x, y, -depth], [x + width, y, -depth]])
        triangles.append([[x, y, z], [x + width, y, -depth], [x + width, y, z]])
        
        # Left edge
        triangles.append([[x, y, z], [x, y + height, z], [x, y + height, -depth]])
        triangles.append([[x, y, z], [x, y + height, -depth], [x, y, -depth]])
        
        # Right edge
        triangles.append([[x + width, y, z], [x + width, y, -depth], [x + width, y + height, -depth]])
        triangles.append([[x + width, y, z], [x + width, y + height, -depth], [x + width, y + height, z]])

    def add_quad(self, triangles: List, v0, v1, v2, v3):
        """Add a quad as two triangles"""
        triangles.append([v0, v1, v2])
        triangles.append([v0, v2, v3])

    def create_faceplate_with_hole(self) -> List[List[List[float]]]:
        """Create faceplate with device hole and support lip"""
        triangles = []

        # Faceplate dimensions
        fp_w = self.faceplate_width
        fp_h = self.faceplate_height
        fp_thickness = self.wall_thickness

        # Opening dimensions
        open_x = self.opening_x
        open_y = self.opening_y
        open_w = self.opening_width
        open_h = self.opening_height

        # Lip dimensions
        lip_y_bottom = open_y + open_h  # Bottom of opening
        lip_thickness = self.lip_thickness
        lip_depth = self.lip_depth

        # === FACEPLATE FRONT FACE (with rectangular hole) ===
        # Top section (above opening)
        if open_y > 0:
            self.add_quad(triangles, [0, open_y, 0], [fp_w, open_y, 0], [fp_w, fp_h, 0], [0, fp_h, 0])

        # Left section (left of opening)
        if open_x > 0:
            self.add_quad(triangles, [0, open_y, 0], [open_x, open_y, 0], [open_x, lip_y_bottom, 0], [0, lip_y_bottom, 0])

        # Right section (right of opening)
        if open_x + open_w < fp_w:
            self.add_quad(triangles, [open_x + open_w, open_y, 0], [fp_w, open_y, 0], [fp_w, lip_y_bottom, 0], [open_x + open_w, lip_y_bottom, 0])

        # Bottom section (below lip)
        if lip_y_bottom + lip_thickness < fp_h:
            self.add_quad(triangles, [0, lip_y_bottom + lip_thickness, 0], [fp_w, lip_y_bottom + lip_thickness, 0], [fp_w, fp_h, 0], [0, fp_h, 0])

        # === RECTANGULAR HOLE EDGES (through faceplate) ===
        self.create_box_hole(triangles, open_x, open_y, 0, open_w, open_h, fp_thickness)

        # === SUPPORT LIP ===
        # Top surface of lip (what device rests on)
        self.add_quad(triangles, [open_x, lip_y_bottom, 0], [open_x + open_w, lip_y_bottom, 0], 
                      [open_x + open_w, lip_y_bottom, -lip_depth], [open_x, lip_y_bottom, -lip_depth])

        # Front face of lip (inner walls)
        # Left inner wall
        self.add_quad(triangles, [open_x, open_y + open_h, 0], [open_x, open_y + open_h, -fp_thickness],
                      [open_x, lip_y_bottom - lip_thickness, -fp_thickness], [open_x, lip_y_bottom - lip_thickness, 0])

        # Right inner wall
        self.add_quad(triangles, [open_x + open_w, open_y + open_h, 0], [open_x + open_w, lip_y_bottom - lip_thickness, 0],
                      [open_x + open_w, lip_y_bottom - lip_thickness, -fp_thickness], [open_x + open_w, open_y + open_h, -fp_thickness])

        # Left side of lip
        self.add_quad(triangles, [open_x, lip_y_bottom, 0], [open_x, lip_y_bottom - lip_thickness, 0],
                      [open_x, lip_y_bottom - lip_thickness, -lip_depth], [open_x, lip_y_bottom, -lip_depth])

        # Right side of lip
        self.add_quad(triangles, [open_x + open_w, lip_y_bottom, 0], [open_x + open_w, lip_y_bottom, -lip_depth],
                      [open_x + open_w, lip_y_bottom - lip_thickness, -lip_depth], [open_x + open_w, lip_y_bottom - lip_thickness, 0])

        # Bottom of lip (back face)
        self.add_quad(triangles, [open_x, lip_y_bottom - lip_thickness, -lip_depth], 
                      [open_x + open_w, lip_y_bottom - lip_thickness, -lip_depth],
                      [open_x + open_w, lip_y_bottom, -lip_depth], [open_x, lip_y_bottom, -lip_depth])

        # === FACEPLATE BACK FACE ===
        self.add_quad(triangles, [0, 0, -fp_thickness], [fp_w, 0, -fp_thickness], 
                      [fp_w, fp_h, -fp_thickness], [0, fp_h, -fp_thickness])

        # === FACEPLATE EDGE FACES ===
        # Top edge
        self.add_quad(triangles, [0, fp_h, 0], [fp_w, fp_h, 0], [fp_w, fp_h, -fp_thickness], [0, fp_h, -fp_thickness])

        # Bottom edge
        self.add_quad(triangles, [0, 0, 0], [0, 0, -fp_thickness], [fp_w, 0, -fp_thickness], [fp_w, 0, 0])

        # Left edge
        self.add_quad(triangles, [0, 0, 0], [0, fp_h, 0], [0, fp_h, -fp_thickness], [0, 0, -fp_thickness])

        # Right edge
        self.add_quad(triangles, [fp_w, 0, 0], [fp_w, 0, -fp_thickness], [fp_w, fp_h, -fp_thickness], [fp_w, fp_h, 0])

        # === MOUNTING HOLES (if enabled) ===
        if self.add_rack_holes:
            holes = self.calculate_mounting_holes()
            for hx, hy in holes:
                hole_verts, hole_tris = self.create_vertices_cylinder(
                    hx, hy, 0, self.HOLE_DIAMETER / 2, self.wall_thickness, segments=12
                )
                triangles.extend(hole_tris)

        return triangles

    def create_vertices_cylinder(self, cx: float, cy: float, cz: float, radius: float,
                                height: float, segments: int = 12) -> Tuple[List, List]:
        """Create vertices for a cylinder (hole)"""
        vertices = []
        triangles = []

        # Top circle
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            vertices.append([x, y, cz])

        # Bottom circle
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            vertices.append([x, y, cz - height])

        # Side triangles
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append([vertices[i], vertices[next_i], vertices[segments + next_i]])
            triangles.append([vertices[i], vertices[segments + next_i], vertices[segments + i]])

        # Top cap
        for i in range(segments - 2):
            triangles.append([vertices[0], vertices[i + 1], vertices[i + 2]])

        # Bottom cap
        for i in range(segments - 2):
            triangles.append([vertices[segments], vertices[segments + i + 2], vertices[segments + i + 1]])

        return vertices, triangles

    def calculate_mounting_holes(self) -> List[Tuple[float, float]]:
        """Calculate positions of standard 19" rack mounting holes (for half-width bracket)"""
        holes = []

        # For half-width bracket, we have columns on the edges
        # Standard: 25.4mm from edge = 1"
        x_positions = [self.HOLE_FROM_EDGE_X, self.faceplate_width - self.HOLE_FROM_EDGE_X]

        # Calculate number of hole rows
        num_rows = int(self.faceplate_height / self.HOLE_PITCH)

        y_start = self.HOLE_FROM_EDGE_Y

        for row in range(num_rows):
            y = y_start + row * self.HOLE_PITCH
            if y < self.faceplate_height - self.HOLE_FROM_EDGE_Y:
                for x in x_positions:
                    holes.append((x, y))

        return holes

    def generate_all_parts(self) -> Dict[str, List]:
        """Generate all parts"""
        return {
            'bracket': self.create_faceplate_with_hole(),
        }


class STLWriter:
    """Write triangle data to binary STL format"""

    @staticmethod
    def write_binary_stl(filename: str, triangles: List, name: str = 'part'):
        """Write triangles to binary STL file"""
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        # Filter out empty triangles
        valid_triangles = [t for t in triangles if isinstance(t, list) and len(t) == 3]

        with open(filename, 'wb') as f:
            # Header (80 bytes)
            header = name.encode('ascii')[:80]
            header += b'\0' * (80 - len(header))
            f.write(header)

            # Number of triangles
            f.write(len(valid_triangles).to_bytes(4, byteorder='little'))

            # Triangle data
            for triangle in valid_triangles:
                try:
                    v0 = np.array(triangle[0], dtype=np.float32)
                    v1 = np.array(triangle[1], dtype=np.float32)
                    v2 = np.array(triangle[2], dtype=np.float32)

                    # Calculate normal
                    edge1 = v1 - v0
                    edge2 = v2 - v0
                    normal = np.cross(edge1, edge2)
                    norm_mag = np.linalg.norm(normal)
                    if norm_mag > 0:
                        normal = normal / norm_mag
                    else:
                        normal = np.array([0, 0, 1], dtype=np.float32)

                    # Write normal (3 floats)
                    f.write(normal.astype(np.float32).tobytes())

                    # Write vertices (9 floats)
                    f.write(v0.astype(np.float32).tobytes())
                    f.write(v1.astype(np.float32).tobytes())
                    f.write(v2.astype(np.float32).tobytes())

                    # Attribute byte count (2 bytes)
                    f.write(b'\0\0')
                except Exception as e:
                    print(f"Error writing triangle: {e}")
                    continue


def calculate_print_stats(triangles: List, infill: int = 20) -> Dict:
    """Calculate printing statistics"""
    volume_cm3 = len(triangles) * 0.001
    material_volume = volume_cm3 * (infill / 100)
    weight_g = material_volume * 1.24  # PLA density
    print_time_h = (material_volume / 5) * 0.5

    return {
        'volume_cm3': round(volume_cm3, 1),
        'material_volume_cm3': round(material_volume, 1),
        'weight_grams': round(weight_g, 1),
        'print_time_hours': round(print_time_h, 1),
        'triangle_count': len(triangles)
    }


def generate_assembly_guide(output_dir: str, config: Dict):
    """Generate assembly guide"""
    rack_units = math.ceil(config['height'] / 44.45)

    guide = f"""# 19" Rack Mount Assembly Guide

## Mount Specifications
- Device Width: {config['width']} mm
- Device Height: {config['height']} mm ({rack_units}U)
- Device Depth: {config['depth']} mm
- Tolerance: {config['tolerance']} mm
- Wall Thickness: {config['wall_thickness']} mm
- Infill: {config['infill']}%

## Part
- **bracket.stl** - Half-width bracket (241.5mm - fits printer bed)
- Print TWO of these, one for each side of the rack

## Assembly Instructions

### Printing
1. Print two bracket copies using your 3D printer
2. Clean up prints - remove supports and sand smooth
3. The two brackets together cover the full 19" width

### Installation
1. Attach one bracket to the left side of the 19" rack:
   - Align M6 mounting holes with rack rail holes
   - Insert M6 bolts or 1/4" equivalent hardware
   - Tighten securely
2. Attach second bracket to the right side (mirror image):
   - Align mounting holes with opposite rail
   - Tighten securely
3. Insert device through the rectangular opening
4. Device will rest on the support lip below the opening
5. The lip extends {config['depth'] + 10}mm into the rack for stability

## Hardware Required
- M6 bolts - approximately {rack_units * 4 * 2} pieces (for both brackets)
- M6 washers and lock washers

## Design Details
- Bracket width: 241.5mm (half of 19" width)
- Bracket height: {rack_units}U
- Device opening: {config['width'] + 2 * config['tolerance']}mm × {config['height'] + 2 * config['tolerance']}mm
- Opening is centered on bracket
- Support lip thickness: {config['wall_thickness']}mm
- Support lip extends {config['depth'] + 10}mm back into rack
- All mounting holes are M6 (0.25") clearance with standard rack spacing

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    guide_path = os.path.join(output_dir, 'ASSEMBLY_GUIDE.md')
    with open(guide_path, 'w') as f:
        f.write(guide)


if __name__ == '__main__':
    # Test
    config = {
        'width': 100,
        'height': 44,
        'depth': 200,
        'tolerance': 2,
        'wall_thickness': 3,
        'add_support': True,
        'infill': 20
    }

    generator = RackMountGenerator(**config)
    parts = generator.generate_all_parts()

    for part_name, triangles in parts.items():
        if triangles:
            stats = calculate_print_stats(triangles, 20)
            print(f"{part_name}: {len(triangles)} triangles, {stats['weight_grams']}g")
