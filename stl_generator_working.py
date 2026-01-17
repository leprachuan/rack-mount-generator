#!/usr/bin/env python3
"""
19" Rack Mount STL Generator - Working Version
"""

import numpy as np
from typing import List, Dict
import os
from datetime import datetime


def create_box(w, h, d, name="box"):
    """Create a simple box"""
    vertices = [
        # Front face
        [0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0],
        # Back face
        [0, 0, -d], [w, 0, -d], [w, h, -d], [0, h, -d],
    ]

    triangles = [
        # Front
        [[vertices[0][i] for i in range(3)], [vertices[1][i] for i in range(3)], [vertices[2][i] for i in range(3)]],
        [[vertices[0][i] for i in range(3)], [vertices[2][i] for i in range(3)], [vertices[3][i] for i in range(3)]],
        # Back
        [[vertices[4][i] for i in range(3)], [vertices[6][i] for i in range(3)], [vertices[5][i] for i in range(3)]],
        [[vertices[4][i] for i in range(3)], [vertices[7][i] for i in range(3)], [vertices[6][i] for i in range(3)]],
        # Top
        [[vertices[3][i] for i in range(3)], [vertices[2][i] for i in range(3)], [vertices[6][i] for i in range(3)]],
        [[vertices[3][i] for i in range(3)], [vertices[6][i] for i in range(3)], [vertices[7][i] for i in range(3)]],
        # Bottom
        [[vertices[0][i] for i in range(3)], [vertices[5][i] for i in range(3)], [vertices[1][i] for i in range(3)]],
        [[vertices[0][i] for i in range(3)], [vertices[4][i] for i in range(3)], [vertices[5][i] for i in range(3)]],
        # Left
        [[vertices[0][i] for i in range(3)], [vertices[3][i] for i in range(3)], [vertices[7][i] for i in range(3)]],
        [[vertices[0][i] for i in range(3)], [vertices[7][i] for i in range(3)], [vertices[4][i] for i in range(3)]],
        # Right
        [[vertices[1][i] for i in range(3)], [vertices[5][i] for i in range(3)], [vertices[6][i] for i in range(3)]],
        [[vertices[1][i] for i in range(3)], [vertices[6][i] for i in range(3)], [vertices[2][i] for i in range(3)]],
    ]

    return triangles


class RackMountGenerator:
    """Generate rack mount components"""

    def __init__(self, device_width, device_height, device_depth,
                 tolerance=2.0, wall_thickness=3.0,
                 add_support=True, add_rack_holes=False):
        self.device_width = device_width
        self.device_height = device_height
        self.device_depth = device_depth
        self.tolerance = tolerance
        self.wall_thickness = wall_thickness
        self.add_support = add_support
        self.add_rack_holes = add_rack_holes

        self.bracket_width = device_width + 2 * (tolerance + wall_thickness)
        self.bracket_height = device_height + 2 * (tolerance + wall_thickness)
        self.bracket_depth = wall_thickness

    def generate_all_parts(self):
        """Generate all parts"""
        parts = {}

        # Create brackets
        bracket_triangles = create_box(self.bracket_width, self.bracket_height, self.bracket_depth)
        parts['bracket_left'] = bracket_triangles
        parts['bracket_right'] = bracket_triangles

        # Create clip
        clip_triangles = create_box(self.bracket_width, 15, 10)
        parts['retention_clip'] = clip_triangles

        # Create support posts if enabled
        if self.add_support:
            support_triangles = []
            post_size = 8
            posts = [
                [post_size/2, post_size/2],
                [self.bracket_width - post_size/2, post_size/2],
                [post_size/2, self.bracket_height - post_size/2],
                [self.bracket_width - post_size/2, self.bracket_height - post_size/2],
            ]
            for x, y in posts:
                post = create_box(post_size, post_size, 15)
                # Translate each triangle
                for tri in post:
                    translated_tri = [[tri[j][i] + [x - post_size/2, y - post_size/2, 0][i] for i in range(3)] for j in range(3)]
                    support_triangles.append(translated_tri)
            parts['support_posts'] = support_triangles
        else:
            parts['support_posts'] = []

        return parts


class STLWriter:
    """Write STL files"""

    @staticmethod
    def write_binary_stl(filename, triangles, name='part'):
        """Write binary STL"""
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)

        with open(filename, 'wb') as f:
            # Header
            header = name.encode('ascii')[:80]
            header += b'\0' * (80 - len(header))
            f.write(header)

            # Count valid triangles
            valid_triangles = [t for t in triangles if isinstance(t, list) and len(t) == 3]
            f.write(len(valid_triangles).to_bytes(4, byteorder='little'))

            # Write each triangle
            for tri in valid_triangles:
                v0 = np.array(tri[0], dtype=np.float32)
                v1 = np.array(tri[1], dtype=np.float32)
                v2 = np.array(tri[2], dtype=np.float32)

                # Normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm_mag = np.linalg.norm(normal)
                if norm_mag > 0:
                    normal = normal / norm_mag
                else:
                    normal = np.array([0, 0, 1], dtype=np.float32)

                f.write(normal.astype(np.float32).tobytes())
                f.write(v0.astype(np.float32).tobytes())
                f.write(v1.astype(np.float32).tobytes())
                f.write(v2.astype(np.float32).tobytes())
                f.write(b'\0\0')


def calculate_print_stats(triangles, infill=20):
    """Calculate print statistics"""
    valid = [t for t in triangles if isinstance(t, list) and len(t) == 3]
    count = len(valid)
    volume = count * 0.001
    material = volume * (infill / 100)
    weight = material * 1.24
    time = (material / 5) * (20 / infill)

    return {
        'triangle_count': count,
        'volume_cm3': round(volume, 1),
        'material_volume_cm3': round(material, 1),
        'weight_grams': round(weight, 1),
        'print_time_hours': round(time, 1)
    }


def generate_assembly_guide(output_dir, config):
    """Generate assembly guide"""
    guide = f"""# 19" Rack Mount Assembly Guide

## Configuration
- Width: {config['width']} mm
- Height: {config['height']} mm
- Depth: {config['depth']} mm
- Wall Clearance: {config['tolerance']} mm
- Wall Thickness: {config['wall_thickness']} mm
- Infill: {config['infill']}%

## Parts Generated
1. bracket_left.stl - Left bracket
2. bracket_right.stl - Right bracket
3. retention_clip.stl - Front clip
4. support_posts.stl - Supports

## Assembly Steps
1. Print all parts
2. Clean and sand
3. Mount in 19" rack
4. Insert device
5. Apply clip
6. Secure with bolts

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(os.path.join(output_dir, 'ASSEMBLY_GUIDE.md'), 'w') as f:
        f.write(guide)
