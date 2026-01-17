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
                 shelf_thickness: float = 5.0,  # Support shelf thickness
                 flange_thickness: float = 5.0,  # Joining flange thickness
                 gusset_size: float = 15.0,  # Size of triangular gussets
                 ear_side: str = 'left',  # Which side the rack ear goes on: 'left' or 'right'
                 is_blank: bool = False):  # If True, no cutout or shelf - just a blank panel
        """Initialize the mount generator"""
        self.device_width = device_width
        self.device_height = device_height
        self.device_depth = device_depth
        self.tolerance = tolerance
        self.wall_thickness = wall_thickness  # Faceplate thickness
        self.add_support = add_support if not is_blank else False  # No support for blanks
        self.add_rack_holes = add_rack_holes
        self.shelf_thickness = shelf_thickness
        self.flange_thickness = flange_thickness
        self.gusset_size = gusset_size
        self.ear_side = ear_side
        self.is_blank = is_blank
        
        # Rack ear dimensions
        self.ear_width = 15.875  # Standard rack ear width (~5/8")
        self.ear_thickness = wall_thickness  # Same as faceplate

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
        If is_blank is True, creates a solid faceplate with no cutout.
        
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
        # BLANK PANEL - solid faceplate with no cutout
        # ============================================
        if self.is_blank:
            # Front face - solid rectangle
            self.add_quad(triangles,
                [0, 0, 0], [fp_w, 0, 0], [fp_w, fp_h, 0], [0, fp_h, 0])
            
            # Back face - solid rectangle
            self.add_quad(triangles,
                [0, 0, -fp_t], [0, fp_h, -fp_t], [fp_w, fp_h, -fp_t], [fp_w, 0, -fp_t])
            
            # Skip to outer edges (no hole inner walls needed)
        else:
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
        # Shelf is wider than the opening with triangular gussets for strength
        # ============================================
        
        if self.add_support:
            shelf_t = self.shelf_thickness
            shelf_d = self.shelf_depth
            gusset_width = self.gusset_size  # Extra width on each side for gussets
            
            # Shelf is positioned at the bottom of the opening
            # It starts at Z = -fp_t (back of faceplate) and extends to Z = -(fp_t + shelf_d)
            shelf_z_front = -fp_t
            shelf_z_back = -fp_t - shelf_d
            
            # Shelf width is wider than opening (adds gusset_width on each side)
            shelf_x1 = op_x - gusset_width
            shelf_x2 = op_x2 + gusset_width
            
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
            self.add_quad(triangles,
                [shelf_x1, shelf_y_bottom, shelf_z_front],
                [shelf_x2, shelf_y_bottom, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_front],
                [shelf_x1, shelf_y_top, shelf_z_front])
            
            # ============================================
            # TRIANGULAR GUSSETS (right triangles for structural support)
            # These connect the shelf to the faceplate on each side
            # Gusset height matches the device height
            # ============================================
            
            # Left gusset - right triangle
            # Vertices: 
            #   A: top-front of gusset area (at faceplate back)
            #   B: top-back of shelf (where shelf meets gusset)  
            #   C: bottom-front (at faceplate back, bottom of shelf)
            gusset_height = self.device_height  # Gusset height matches device height
            
            # Left gusset
            left_gusset_x = shelf_x1 + gusset_width / 2  # Center of left gusset
            
            # Left gusset - outer face (facing left)
            triangles.append([
                [shelf_x1, shelf_y_top, shelf_z_front],  # Front top
                [shelf_x1, shelf_y_top, shelf_z_back],   # Back top
                [shelf_x1, shelf_y_top + gusset_height, shelf_z_front]  # Front high point
            ])
            
            # Left gusset - inner face (facing right)
            triangles.append([
                [shelf_x1 + gusset_width, shelf_y_top, shelf_z_front],  # Front top
                [shelf_x1 + gusset_width, shelf_y_top + gusset_height, shelf_z_front],  # Front high point
                [shelf_x1 + gusset_width, shelf_y_top, shelf_z_back]   # Back top
            ])
            
            # Left gusset - top face (hypotenuse)
            self.add_quad(triangles,
                [shelf_x1, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x1 + gusset_width, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x1 + gusset_width, shelf_y_top, shelf_z_back],
                [shelf_x1, shelf_y_top, shelf_z_back])
            
            # Left gusset - front face (attaches to faceplate)
            self.add_quad(triangles,
                [shelf_x1, shelf_y_top, shelf_z_front],
                [shelf_x1, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x1 + gusset_width, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x1 + gusset_width, shelf_y_top, shelf_z_front])
            
            # Right gusset
            # Right gusset - outer face (facing right)
            triangles.append([
                [shelf_x2, shelf_y_top, shelf_z_front],  # Front top
                [shelf_x2, shelf_y_top + gusset_height, shelf_z_front],  # Front high point
                [shelf_x2, shelf_y_top, shelf_z_back]   # Back top
            ])
            
            # Right gusset - inner face (facing left)
            triangles.append([
                [shelf_x2 - gusset_width, shelf_y_top, shelf_z_front],  # Front top
                [shelf_x2 - gusset_width, shelf_y_top, shelf_z_back],   # Back top
                [shelf_x2 - gusset_width, shelf_y_top + gusset_height, shelf_z_front]  # Front high point
            ])
            
            # Right gusset - top face (hypotenuse)
            self.add_quad(triangles,
                [shelf_x2 - gusset_width, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x2, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_back],
                [shelf_x2 - gusset_width, shelf_y_top, shelf_z_back])
            
            # Right gusset - front face (attaches to faceplate)
            self.add_quad(triangles,
                [shelf_x2 - gusset_width, shelf_y_top, shelf_z_front],
                [shelf_x2 - gusset_width, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x2, shelf_y_top + gusset_height, shelf_z_front],
                [shelf_x2, shelf_y_top, shelf_z_front])

        # ============================================
        # RACK EAR (mounting flange on left or right side)
        # This is the part that attaches to the rack rails
        # ============================================
        ear_w = self.ear_width
        ear_t = self.ear_thickness
        
        if self.ear_side == 'left':
            # Left ear - extends to the left of the faceplate
            ear_x_outer = -ear_w
            ear_x_inner = 0
        else:
            # Right ear - extends to the right of the faceplate
            ear_x_outer = fp_w + ear_w
            ear_x_inner = fp_w
        
        # Front face of ear
        self.add_quad(triangles,
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, 0, 0],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, 0, 0],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, fp_h, 0],
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, fp_h, 0])
        
        # Back face of ear
        self.add_quad(triangles,
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, 0, -ear_t],
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, fp_h, -ear_t],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, fp_h, -ear_t],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, 0, -ear_t])
        
        # Top edge of ear
        self.add_quad(triangles,
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, fp_h, 0],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, fp_h, 0],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, fp_h, -ear_t],
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, fp_h, -ear_t])
        
        # Bottom edge of ear
        self.add_quad(triangles,
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, 0, 0],
            [ear_x_outer if self.ear_side == 'left' else ear_x_inner, 0, -ear_t],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, 0, -ear_t],
            [ear_x_inner if self.ear_side == 'left' else ear_x_outer, 0, 0])
        
        # Outer edge of ear (the side away from faceplate)
        if self.ear_side == 'left':
            self.add_quad(triangles,
                [ear_x_outer, 0, 0], [ear_x_outer, fp_h, 0],
                [ear_x_outer, fp_h, -ear_t], [ear_x_outer, 0, -ear_t])
        else:
            self.add_quad(triangles,
                [ear_x_outer, 0, 0], [ear_x_outer, 0, -ear_t],
                [ear_x_outer, fp_h, -ear_t], [ear_x_outer, fp_h, 0])

        # ============================================
        # RACK MOUNTING HOLES (on the ear)
        # ============================================
        if self.add_rack_holes:
            holes = self.calculate_mounting_holes()
            for hx, hy in holes:
                # Create hole with slight extension beyond surfaces for clean boolean
                hole_tris = self.create_hole_extended(hx, hy, self.HOLE_DIAMETER / 2, ear_t, segments=16)
                triangles.extend(hole_tris)

        # ============================================
        # JOINING FLANGE (on inner edge, opposite side from ear)
        # This flange extends back into the rack and has M3 holes
        # for connecting two brackets together
        # ============================================
        flange_width = self.flange_thickness  # Width of the joining flange
        flange_depth = 50.8  # 2 inches back into rack
        flange_thickness = fp_t  # Same thickness as faceplate
        
        # Position flange on inner edge (opposite from ear)
        if self.ear_side == 'left':
            flange_x1 = fp_w - flange_width  # Right edge (inner)
            flange_x2 = fp_w
        else:
            flange_x1 = 0  # Left edge (inner)
            flange_x2 = flange_width
        
        flange_z_front = -fp_t
        flange_z_back = -fp_t - flange_depth
        
        # Top face of flange
        self.add_quad(triangles,
            [flange_x1, fp_h, flange_z_front],
            [flange_x2, fp_h, flange_z_front],
            [flange_x2, fp_h, flange_z_back],
            [flange_x1, fp_h, flange_z_back])
        
        # Bottom face of flange
        self.add_quad(triangles,
            [flange_x1, 0, flange_z_front],
            [flange_x1, 0, flange_z_back],
            [flange_x2, 0, flange_z_back],
            [flange_x2, 0, flange_z_front])
        
        # Outer side of flange (away from faceplate center)
        if self.ear_side == 'left':
            # Right side faces outward
            self.add_quad(triangles,
                [flange_x2, 0, flange_z_front],
                [flange_x2, 0, flange_z_back],
                [flange_x2, fp_h, flange_z_back],
                [flange_x2, fp_h, flange_z_front])
        else:
            # Left side faces outward
            self.add_quad(triangles,
                [flange_x1, 0, flange_z_front],
                [flange_x1, fp_h, flange_z_front],
                [flange_x1, fp_h, flange_z_back],
                [flange_x1, 0, flange_z_back])
        
        # Inner side of flange (toward faceplate center)
        if self.ear_side == 'left':
            self.add_quad(triangles,
                [flange_x1, 0, flange_z_front],
                [flange_x1, fp_h, flange_z_front],
                [flange_x1, fp_h, flange_z_back],
                [flange_x1, 0, flange_z_back])
        else:
            self.add_quad(triangles,
                [flange_x2, 0, flange_z_front],
                [flange_x2, 0, flange_z_back],
                [flange_x2, fp_h, flange_z_back],
                [flange_x2, fp_h, flange_z_front])
        
        # Back face of flange
        self.add_quad(triangles,
            [flange_x1, 0, flange_z_back],
            [flange_x1, fp_h, flange_z_back],
            [flange_x2, fp_h, flange_z_back],
            [flange_x2, 0, flange_z_back])
        
        # Front face of flange (connects to faceplate back) - already covered by faceplate
        
        # ============================================
        # FLANGE GUSSETS (small triangular supports)
        # Right-angle triangles in Y-Z plane, extruded along flange width (X)
        # They connect the faceplate back to the flange
        # ============================================
        gusset_height = self.gusset_size  # Height up the faceplate back (Y direction)
        gusset_depth = self.gusset_size   # Depth along the flange (Z direction, into rack)
        
        # Gusset X positions span the flange width
        gusset_x1 = flange_x1
        gusset_x2 = flange_x2
        
        # Bottom gusset - right triangle with corner lifted 10mm from bottom
        # Triangle vertices in Y-Z plane (at each X):
        #   Corner: (Y=10, Z=flange_z_front) - at faceplate back, 10mm up
        #   Up:     (Y=10+gusset_height, Z=flange_z_front) - up the faceplate back
        #   Back:   (Y=10, Z=flange_z_front - gusset_depth) - along the flange
        bottom_gusset_y = 10.0  # Lift bottom gusset up by 10mm
        
        # Left face of bottom gusset (at gusset_x1) - normal should point in -X
        triangles.append([
            [gusset_x1, bottom_gusset_y, flange_z_front],  # Corner
            [gusset_x1, bottom_gusset_y + gusset_height, flange_z_front],  # Up
            [gusset_x1, bottom_gusset_y, flange_z_front - gusset_depth]  # Back
        ])
        
        # Right face of bottom gusset (at gusset_x2) - normal should point in +X
        triangles.append([
            [gusset_x2, bottom_gusset_y, flange_z_front],  # Corner
            [gusset_x2, bottom_gusset_y, flange_z_front - gusset_depth],  # Back
            [gusset_x2, bottom_gusset_y + gusset_height, flange_z_front]  # Up
        ])
        
        # Bottom face of bottom gusset (Y=bottom_gusset_y plane)
        self.add_quad(triangles,
            [gusset_x1, bottom_gusset_y, flange_z_front],
            [gusset_x2, bottom_gusset_y, flange_z_front],
            [gusset_x2, bottom_gusset_y, flange_z_front - gusset_depth],
            [gusset_x1, bottom_gusset_y, flange_z_front - gusset_depth])
        
        # Hypotenuse face of bottom gusset (diagonal from top-front to bottom-back)
        self.add_quad(triangles,
            [gusset_x1, bottom_gusset_y + gusset_height, flange_z_front],
            [gusset_x1, bottom_gusset_y, flange_z_front - gusset_depth],
            [gusset_x2, bottom_gusset_y, flange_z_front - gusset_depth],
            [gusset_x2, bottom_gusset_y + gusset_height, flange_z_front])
        
        # Front face of bottom gusset (on faceplate back, Z=flange_z_front)
        self.add_quad(triangles,
            [gusset_x1, bottom_gusset_y, flange_z_front],
            [gusset_x1, bottom_gusset_y + gusset_height, flange_z_front],
            [gusset_x2, bottom_gusset_y + gusset_height, flange_z_front],
            [gusset_x2, bottom_gusset_y, flange_z_front])
        
        # Top gusset - same triangle but at top of faceplate
        # Corner is at (Y=fp_h - gusset_height), going DOWN to connect to top of faceplate
        # Actually, we want the gusset to be "upside down" - corner at TOP
        #   Corner: (Y=fp_h, Z=flange_z_front) - at top of faceplate back  
        #   Down:   (Y=fp_h - gusset_height, Z=flange_z_front) - down the faceplate back
        #   Back:   (Y=fp_h, Z=flange_z_front - gusset_depth) - along the flange
        
        # Left face of top gusset - normal should point in -X
        triangles.append([
            [gusset_x1, fp_h, flange_z_front],  # Corner at top
            [gusset_x1, fp_h, flange_z_front - gusset_depth],  # Back
            [gusset_x1, fp_h - gusset_height, flange_z_front]  # Down
        ])
        
        # Right face of top gusset - normal should point in +X
        triangles.append([
            [gusset_x2, fp_h, flange_z_front],  # Corner at top
            [gusset_x2, fp_h - gusset_height, flange_z_front],  # Down
            [gusset_x2, fp_h, flange_z_front - gusset_depth]  # Back
        ])
        
        # Top face of top gusset (Y=fp_h plane)
        self.add_quad(triangles,
            [gusset_x1, fp_h, flange_z_front],
            [gusset_x1, fp_h, flange_z_front - gusset_depth],
            [gusset_x2, fp_h, flange_z_front - gusset_depth],
            [gusset_x2, fp_h, flange_z_front])
        
        # Hypotenuse face of top gusset (diagonal from bottom-front to top-back)
        self.add_quad(triangles,
            [gusset_x1, fp_h - gusset_height, flange_z_front],
            [gusset_x2, fp_h - gusset_height, flange_z_front],
            [gusset_x2, fp_h, flange_z_front - gusset_depth],
            [gusset_x1, fp_h, flange_z_front - gusset_depth])
        
        # Front face of top gusset (on faceplate back)
        self.add_quad(triangles,
            [gusset_x1, fp_h - gusset_height, flange_z_front],
            [gusset_x1, fp_h, flange_z_front],
            [gusset_x2, fp_h, flange_z_front],
            [gusset_x2, fp_h - gusset_height, flange_z_front])
        
        # M3 joining holes through the flange (horizontal, for screwing brackets together)
        joining_holes = self.calculate_joining_holes()
        for hy, hz in joining_holes:
            # Holes go through the flange horizontally (X direction)
            if self.ear_side == 'left':
                hx = flange_x2  # Drill from the outer edge
            else:
                hx = flange_x1
            # Create horizontal hole through flange
            hole_tris = self.create_horizontal_hole(hx, hy, hz, 1.6, flange_width, segments=16, direction='x' if self.ear_side == 'right' else '-x')
            triangles.extend(hole_tris)

        return triangles

    def create_hole(self, cx: float, cy: float, radius: float, depth: float, segments: int = 16) -> List:
        """Create a cylindrical hole through material (Z direction).
        Creates only the cylinder wall - the interior surface of the hole.
        Normals point inward (toward cylinder axis) to represent removed material."""
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
            # Winding is set so normals point INWARD toward cylinder axis
            triangles.append([[x1, y1, 0], [x2, y2, 0], [x2, y2, -depth]])
            triangles.append([[x1, y1, 0], [x2, y2, -depth], [x1, y1, -depth]])
        
        return triangles

    def create_hole_extended(self, cx: float, cy: float, radius: float, depth: float, segments: int = 16) -> List:
        """Create a cylindrical hole that extends slightly beyond both surfaces.
        This creates better boolean-like subtraction behavior in slicers.
        The hole extends 0.1mm beyond both the front (Z=0) and back (Z=-depth) surfaces."""
        triangles = []
        extension = 0.1  # Small extension beyond surfaces
        z_front = extension
        z_back = -depth - extension
        
        # Generate points around the circle
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            x1 = cx + radius * math.cos(angle1)
            y1 = cy + radius * math.sin(angle1)
            x2 = cx + radius * math.cos(angle2)
            y2 = cy + radius * math.sin(angle2)
            
            # Cylinder wall with normals pointing OUTWARD (standard solid cylinder)
            # When intersected with solid ear, slicers typically subtract the inner volume
            triangles.append([[x1, y1, z_front], [x1, y1, z_back], [x2, y2, z_back]])
            triangles.append([[x1, y1, z_front], [x2, y2, z_back], [x2, y2, z_front]])
        
        # Add end caps to make it a proper closed solid
        # Front cap (at z_front)
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * ((i + 1) % segments) / segments
            x1 = cx + radius * math.cos(angle1)
            y1 = cy + radius * math.sin(angle1)
            x2 = cx + radius * math.cos(angle2)
            y2 = cy + radius * math.sin(angle2)
            # Front cap facing +Z
            triangles.append([[cx, cy, z_front], [x1, y1, z_front], [x2, y2, z_front]])
        
        # Back cap (at z_back)
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * ((i + 1) % segments) / segments
            x1 = cx + radius * math.cos(angle1)
            y1 = cy + radius * math.sin(angle1)
            x2 = cx + radius * math.cos(angle2)
            y2 = cy + radius * math.sin(angle2)
            # Back cap facing -Z
            triangles.append([[cx, cy, z_back], [x2, y2, z_back], [x1, y1, z_back]])
        
        return triangles

    def create_horizontal_hole(self, cx: float, cy: float, cz: float, radius: float, depth: float, segments: int = 16, direction: str = 'x') -> List:
        """Create a cylindrical hole in horizontal direction (X axis)"""
        triangles = []
        
        # Generate points around the circle (in Y-Z plane)
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            y1 = cy + radius * math.cos(angle1)
            z1 = cz + radius * math.sin(angle1)
            y2 = cy + radius * math.cos(angle2)
            z2 = cz + radius * math.sin(angle2)
            
            if direction == 'x':
                # Hole goes in +X direction
                triangles.append([[cx, y1, z1], [cx, y2, z2], [cx + depth, y2, z2]])
                triangles.append([[cx, y1, z1], [cx + depth, y2, z2], [cx + depth, y1, z1]])
            else:
                # Hole goes in -X direction
                triangles.append([[cx, y1, z1], [cx - depth, y2, z2], [cx, y2, z2]])
                triangles.append([[cx, y1, z1], [cx - depth, y1, z1], [cx - depth, y2, z2]])
        
        return triangles

    def calculate_mounting_holes(self) -> List[Tuple[float, float]]:
        """Calculate positions of standard 19" rack mounting holes on the rack ear"""
        holes = []
        
        # Position holes on the ear (centered in the ear width)
        if self.ear_side == 'left':
            x_pos = -self.ear_width / 2  # Center of left ear
        else:
            x_pos = self.faceplate_width + self.ear_width / 2  # Center of right ear
        
        # Standard rack hole pattern: 3 holes per U
        # Spacing pattern is: 0.625", 0.5", 0.625" (15.875mm, 12.7mm, 15.875mm)
        for u in range(self.rack_units):
            base_y = u * self.RACK_UNIT_HEIGHT
            # Three holes per U at standard positions
            holes.append((x_pos, base_y + 6.35))   # First hole at 0.25"
            holes.append((x_pos, base_y + 22.225)) # Middle hole
            holes.append((x_pos, base_y + 38.1))   # Third hole at 1.5"
        
        return holes

    def calculate_joining_holes(self) -> List[Tuple[float, float]]:
        """
        Calculate positions of M3 joining holes on the joining flange.
        Returns list of (y, z) positions for horizontal holes through the flange.
        Y = height position, Z = depth into rack
        """
        holes = []
        
        fp_t = self.wall_thickness
        flange_depth = 50.8  # 2 inches
        
        # Place holes at regular intervals along the height
        # One hole every ~30mm, starting 15mm from top and bottom
        num_holes_y = max(2, int(self.faceplate_height / 30))
        spacing_y = self.faceplate_height / (num_holes_y + 1)
        
        # Place 2 holes along the depth (z direction)
        # One near front, one near back
        z_front = -fp_t - 15  # 15mm from faceplate back
        z_back = -fp_t - flange_depth + 15  # 15mm from flange back
        
        for i in range(1, num_holes_y + 1):
            y_pos = i * spacing_y
            holes.append((y_pos, z_front))
            holes.append((y_pos, z_back))
        
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
