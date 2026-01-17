#!/usr/bin/env python3
"""
19" Rack Mount STL Generator
Generates 3D-printable mounting bracket for square devices in 19" racks
- Half-width faceplate (fits printer bed)
- Rectangular hole through faceplate for device
- Support shelf below opening that extends the device depth
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
    RACK_FULL_WIDTH = 450.0  # Inside width of standard 19" rack (~17.75 inches)
    RACK_HALF_WIDTH = 225.0  # Half width (fits printer bed)
    RACK_UNIT_HEIGHT = 44.45  # 1U in mm
    HOLE_PITCH = 15.875  # Standard hole spacing (5/8")
    HOLE_DIAMETER = 6.35  # M6 clearance hole (0.25")
    HOLE_FROM_EDGE_X = 6.35  # Distance from left/right edge to hole center

    def __init__(self,
                 device_width: float,
                 device_height: float,
                 device_depth: float,
                 tolerance: float = 2.0,
                 wall_thickness: float = 10.0,  # Faceplate thickness (default 10mm)
                 add_support: bool = True,
                 add_rack_holes: bool = True,
                 shelf_thickness: float = 5.0):  # Support shelf thickness
        """Initialize the mount generator"""
        self.device_width = device_width
        self.device_height = device_height
        self.device_depth = device_depth
        self.tolerance = tolerance
        self.wall_thickness = wall_thickness  # Faceplate thickness
        self.add_support = add_support
        self.add_rack_holes = add_rack_holes
        self.shelf_thickness = shelf_thickness

        # Calculate rack units needed (round up)
        # Use 35mm threshold per rack unit to leave room for tolerance
        self.rack_units = math.ceil(device_height / 35.0)
        self.faceplate_height = self.rack_units * self.RACK_UNIT_HEIGHT

        # Use half-width for printability
        self.faceplate_width = self.RACK_HALF_WIDTH

        # Device opening dimensions (with tolerance)
        self.opening_width = device_width + 2 * tolerance
        self.opening_height = device_height + 2 * tolerance

        # Center the opening horizontally, and vertically within the rack units
        self.opening_x = (self.faceplate_width - self.opening_width) / 2
        self.opening_y = (self.faceplate_height - self.opening_height) / 2

        # Support shelf extends back the full depth of the device
        self.shelf_depth = device_depth + 10  # Extends 10mm past device depth for support

    def add_quad(self, triangles: List, v0, v1, v2, v3):
        """Add a quad as two triangles (counter-clockwise winding for outward normals)"""
        triangles.append([v0, v1, v2])
        triangles.append([v0, v2, v3])

    def create_faceplate_with_hole(self) -> List[List[List[float]]]:
        """
        Create faceplate with device cutout hole and support shelf.
        
        Coordinate system:
        - X: width (left to right)
        - Y: height (bottom to top)  
        - Z: depth (front to back, negative goes into rack)
        """
        triangles = []

        # Faceplate dimensions
        fp_w = self.faceplate_width
        fp_h = self.faceplate_height
        fp_t = self.wall_thickness  # Faceplate thickness

        # Opening dimensions and position
        op_x = self.opening_x  # Left edge of opening
        op_y = self.opening_y  # Bottom edge of opening
        op_w = self.opening_width
        op_h = self.opening_height
        op_x2 = op_x + op_w  # Right edge of opening
        op_y2 = op_y + op_h  # Top edge of opening

        # ============================================
        # FRONT FACE of faceplate (Z = 0)
        # We need to draw the front face with a rectangular hole
        # ============================================
        
        # Bottom strip (below opening)
        if op_y > 0:
            self.add_quad(triangles,
                [0, 0, 0], [fp_w, 0, 0], [fp_w, op_y, 0], [0, op_y, 0])
        
        # Top strip (above opening)
        if op_y2 < fp_h:
            self.add_quad(triangles,
                [0, op_y2, 0], [fp_w, op_y2, 0], [fp_w, fp_h, 0], [0, fp_h, 0])
        
        # Left strip (beside opening, between bottom and top strips)
        if op_x > 0:
            self.add_quad(triangles,
                [0, op_y, 0], [op_x, op_y, 0], [op_x, op_y2, 0], [0, op_y2, 0])
        
        # Right strip (beside opening, between bottom and top strips)
        if op_x2 < fp_w:
            self.add_quad(triangles,
                [op_x2, op_y, 0], [fp_w, op_y, 0], [fp_w, op_y2, 0], [op_x2, op_y2, 0])

        # ============================================
        # BACK FACE of faceplate (Z = -fp_t)
        # Same layout but with hole, and reversed winding
        # ============================================
        
        # Bottom strip
        if op_y > 0:
            self.add_quad(triangles,
                [0, 0, -fp_t], [0, op_y, -fp_t], [fp_w, op_y, -fp_t], [fp_w, 0, -fp_t])
        
        # Top strip
        if op_y2 < fp_h:
            self.add_quad(triangles,
                [0, op_y2, -fp_t], [0, fp_h, -fp_t], [fp_w, fp_h, -fp_t], [fp_w, op_y2, -fp_t])
        
        # Left strip
        if op_x > 0:
            self.add_quad(triangles,
                [0, op_y, -fp_t], [0, op_y2, -fp_t], [op_x, op_y2, -fp_t], [op_x, op_y, -fp_t])
        
        # Right strip
        if op_x2 < fp_w:
            self.add_quad(triangles,
                [op_x2, op_y, -fp_t], [op_x2, op_y2, -fp_t], [fp_w, op_y2, -fp_t], [fp_w, op_y, -fp_t])

        # ============================================
        # HOLE INNER WALLS (connecting front to back through the cutout)
        # ============================================
        
        # Top inner wall of hole
        self.add_quad(triangles,
            [op_x, op_y2, 0], [op_x2, op_y2, 0], [op_x2, op_y2, -fp_t], [op_x, op_y2, -fp_t])
        
        # Bottom inner wall of hole
        self.add_quad(triangles,
            [op_x, op_y, 0], [op_x, op_y, -fp_t], [op_x2, op_y, -fp_t], [op_x2, op_y, 0])
        
        # Left inner wall of hole
        self.add_quad(triangles,
            [op_x, op_y, 0], [op_x, op_y2, 0], [op_x, op_y2, -fp_t], [op_x, op_y, -fp_t])
        
        # Right inner wall of hole
        self.add_quad(triangles,
            [op_x2, op_y, 0], [op_x2, op_y, -fp_t], [op_x2, op_y2, -fp_t], [op_x2, op_y2, 0])

        # ============================================
        # OUTER EDGES of faceplate
        # ============================================
        
        # Top edge
        self.add_quad(triangles,
            [0, fp_h, 0], [fp_w, fp_h, 0], [fp_w, fp_h, -fp_t], [0, fp_h, -fp_t])
        
        # Bottom edge
        self.add_quad(triangles,
            [0, 0, 0], [0, 0, -fp_t], [fp_w, 0, -fp_t], [fp_w, 0, 0])
        
        # Left edge
        self.add_quad(triangles,
            [0, 0, 0], [0, fp_h, 0], [0, fp_h, -fp_t], [0, 0, -fp_t])
        
        # Right edge
        self.add_quad(triangles,
            [fp_w, 0, 0], [fp_w, 0, -fp_t], [fp_w, fp_h, -fp_t], [fp_w, fp_h, 0])

        # ============================================
        # SUPPORT SHELF (extends back from bottom of opening)
        # The shelf sits at the bottom of the opening and extends back
        # ============================================
        
        if self.add_support:
            shelf_t = self.shelf_thickness
            shelf_d = self.shelf_depth
            
            # Shelf is positioned at the bottom of the opening
            # It starts at Z = -fp_t (back of faceplate) and extends to Z = -(fp_t + shelf_d)
            shelf_z_front = -fp_t
            shelf_z_back = -fp_t - shelf_d
            
            # Shelf width matches opening width
            shelf_x1 = op_x
            shelf_x2 = op_x2
            
            # Shelf Y position (sits at bottom of opening)
            shelf_y_top = op_y
            shelf_y_bottom = op_y - shelf_t
            
            # Top face of shelf (device rests here)
            self.add_quad(triangles,
                [shelf_x1, shelf_y_top, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_back],
                [shelf_x1, shelf_y_top, shelf_z_back])
            
            # Bottom face of shelf
            self.add_quad(triangles,
                [shelf_x1, shelf_y_bottom, shelf_z_front],
                [shelf_x1, shelf_y_bottom, shelf_z_back],
                [shelf_x2, shelf_y_bottom, shelf_z_back],
                [shelf_x2, shelf_y_bottom, shelf_z_front])
            
            # Left side of shelf
            self.add_quad(triangles,
                [shelf_x1, shelf_y_bottom, shelf_z_front],
                [shelf_x1, shelf_y_top, shelf_z_front],
                [shelf_x1, shelf_y_top, shelf_z_back],
                [shelf_x1, shelf_y_bottom, shelf_z_back])
            
            # Right side of shelf
            self.add_quad(triangles,
                [shelf_x2, shelf_y_bottom, shelf_z_front],
                [shelf_x2, shelf_y_bottom, shelf_z_back],
                [shelf_x2, shelf_y_top, shelf_z_back],
                [shelf_x2, shelf_y_top, shelf_z_front])
            
            # Back face of shelf
            self.add_quad(triangles,
                [shelf_x1, shelf_y_bottom, shelf_z_back],
                [shelf_x1, shelf_y_top, shelf_z_back],
                [shelf_x2, shelf_y_top, shelf_z_back],
                [shelf_x2, shelf_y_bottom, shelf_z_back])
            
            # Front face of shelf (connects to faceplate back)
            # Only needed if shelf_y_bottom < 0 (shelf extends below faceplate)
            # Actually, we need to connect shelf to faceplate
            self.add_quad(triangles,
                [shelf_x1, shelf_y_bottom, shelf_z_front],
                [shelf_x2, shelf_y_bottom, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_front],
                [shelf_x1, shelf_y_top, shelf_z_front])

        # ============================================
        # MOUNTING HOLES (if enabled)
        # ============================================
        if self.add_rack_holes:
            holes = self.calculate_mounting_holes()
            for hx, hy in holes:
                hole_tris = self.create_hole(hx, hy, self.HOLE_DIAMETER / 2, fp_t, segments=16)
                triangles.extend(hole_tris)

        return triangles

    def create_hole(self, cx: float, cy: float, radius: float, depth: float, segments: int = 16) -> List:
        """Create a cylindrical hole through the faceplate"""
        triangles = []
        
        # Generate points around the circle
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            x1 = cx + radius * math.cos(angle1)
            y1 = cy + radius * math.sin(angle1)
            x2 = cx + radius * math.cos(angle2)
            y2 = cy + radius * math.sin(angle2)
            
            # Cylinder wall (connecting front to back)
            triangles.append([[x1, y1, 0], [x2, y2, 0], [x2, y2, -depth]])
            triangles.append([[x1, y1, 0], [x2, y2, -depth], [x1, y1, -depth]])
        
        return triangles

    def calculate_mounting_holes(self) -> List[Tuple[float, float]]:
        """Calculate positions of standard 19" rack mounting holes"""
        holes = []
        
        # Standard rack holes are near the edges
        x_pos = self.HOLE_FROM_EDGE_X
        
        # Vertical spacing: typically 3 holes per U with standard spacing
        # We'll put holes at quarter points of each rack unit
        for u in range(self.rack_units):
            base_y = u * self.RACK_UNIT_HEIGHT
            # Two holes per U, at 1/4 and 3/4 positions
            holes.append((x_pos, base_y + self.RACK_UNIT_HEIGHT * 0.25))
            holes.append((x_pos, base_y + self.RACK_UNIT_HEIGHT * 0.75))
        
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
