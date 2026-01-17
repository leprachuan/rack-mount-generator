#!/usr/bin/env python3
"""
Test script for 19" Rack Mount Generator
Generates sample mount files for testing
"""

import os
import sys
from stl_generator import (
    RackMountGenerator,
    STLWriter,
    calculate_print_stats,
    generate_assembly_guide
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def test_basic_generation():
    """Test basic mount generation"""
    print_header("Test 1: Basic Mount Generation")

    config = {
        'width': 100,
        'height': 44,
        'depth': 200,
        'tolerance': 2,
        'wall_thickness': 3,
        'add_support': True,
        'add_rack_holes': False,
        'infill': 20
    }

    print("\n📋 Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    generator = RackMountGenerator(
        config['width'],
        config['height'],
        config['depth'],
        config['tolerance'],
        config['wall_thickness'],
        config['add_support'],
        config['add_rack_holes']
    )

    parts = generator.generate_all_parts()

    print("\n📊 Generated Parts:")
    for part_name, triangles in parts.items():
        if len(triangles) > 0:
            print(f"\n  {part_name}:")
            print(f"    Triangles: {len(triangles)}")

            stats = calculate_print_stats(triangles, config['infill'])
            print(f"    Volume: {stats['volume_cm3']:.1f} cm³")
            print(f"    Material: {stats['material_volume_cm3']:.1f} cm³")
            print(f"    Weight: {stats['weight_grams']:.1f}g")
            print(f"    Print Time: {stats['print_time_hours']:.1f}h")

    return parts


def test_different_sizes():
    """Test with different device sizes"""
    print_header("Test 2: Different Device Sizes")

    sizes = [
        {'name': 'Small (50x44x100)', 'w': 50, 'h': 44, 'd': 100},
        {'name': 'Medium (100x44x200)', 'w': 100, 'h': 44, 'd': 200},
        {'name': 'Large (200x44x300)', 'w': 200, 'h': 44, 'd': 300},
    ]

    for size_config in sizes:
        print(f"\n  Testing: {size_config['name']}")

        generator = RackMountGenerator(
            size_config['w'],
            size_config['h'],
            size_config['d']
        )

        parts = generator.generate_all_parts()
        bracket = parts['bracket_left']
        stats = calculate_print_stats(bracket, 20)

        print(f"    Bracket weight: {stats['weight_grams']:.1f}g")
        print(f"    Print time: {stats['print_time_hours']:.1f}h")


def test_tolerances():
    """Test different tolerance settings"""
    print_header("Test 3: Different Tolerance Settings")

    tolerances = [0.5, 1.0, 2.0, 5.0]

    for tol in tolerances:
        generator = RackMountGenerator(
            100, 44, 200,
            tolerance=tol,
            wall_thickness=3
        )

        parts = generator.generate_all_parts()
        bracket = parts['bracket_left']
        stats = calculate_print_stats(bracket, 20)

        print(f"\n  Tolerance: {tol}mm")
        print(f"    Volume: {stats['material_volume_cm3']:.1f} cm³")
        print(f"    Weight: {stats['weight_grams']:.1f}g")


def test_infill_settings():
    """Test different infill percentages"""
    print_header("Test 4: Different Infill Settings")

    infills = [15, 20, 30, 50]
    generator = RackMountGenerator(100, 44, 200)
    parts = generator.generate_all_parts()
    bracket = parts['bracket_left']

    for infill in infills:
        stats = calculate_print_stats(bracket, infill)
        print(f"\n  Infill: {infill}%")
        print(f"    Material: {stats['material_volume_cm3']:.1f} cm³")
        print(f"    Weight: {stats['weight_grams']:.1f}g")
        print(f"    Print Time: {stats['print_time_hours']:.1f}h")


def test_file_generation():
    """Test actual STL file generation"""
    print_header("Test 5: File Generation")

    output_dir = './test_output'
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📁 Output directory: {os.path.abspath(output_dir)}")

    config = {
        'width': 100,
        'height': 44,
        'depth': 200,
        'tolerance': 2,
        'wall_thickness': 3,
        'add_support': True,
        'add_rack_holes': False,
        'infill': 20
    }

    generator = RackMountGenerator(
        config['width'],
        config['height'],
        config['depth'],
        config['tolerance'],
        config['wall_thickness'],
        config['add_support'],
        config['add_rack_holes']
    )

    parts = generator.generate_all_parts()

    print("\n📝 Writing files...")
    for part_name, triangles in parts.items():
        if len(triangles) > 0:
            stl_path = os.path.join(output_dir, f'{part_name}.stl')
            STLWriter.write_binary_stl(stl_path, triangles, part_name)

            file_size = os.path.getsize(stl_path)
            print(f"  ✓ {part_name}.stl ({file_size / 1024:.1f} KB)")

    # Generate assembly guide
    generate_assembly_guide(output_dir, config)
    print(f"  ✓ ASSEMBLY_GUIDE.md")

    print(f"\n✅ Test files generated in: {os.path.abspath(output_dir)}")


def test_edge_cases():
    """Test edge cases"""
    print_header("Test 6: Edge Cases")

    edge_cases = [
        {'name': 'Minimum size', 'w': 10, 'h': 10, 'd': 10},
        {'name': 'Maximum size', 'w': 500, 'h': 500, 'd': 500},
        {'name': 'Thin walls', 'w': 100, 'h': 44, 'd': 200, 'wt': 1.5},
        {'name': 'Thick walls', 'w': 100, 'h': 44, 'd': 200, 'wt': 10},
        {'name': 'Tight tolerance', 'w': 100, 'h': 44, 'd': 200, 't': 0.5},
        {'name': 'Loose tolerance', 'w': 100, 'h': 44, 'd': 200, 't': 10},
    ]

    for case in edge_cases:
        try:
            generator = RackMountGenerator(
                case['w'],
                case['h'],
                case['d'],
                case.get('t', 2),
                case.get('wt', 3)
            )

            parts = generator.generate_all_parts()
            bracket = parts['bracket_left']

            if len(bracket) > 0:
                stats = calculate_print_stats(bracket, 20)
                print(f"\n  ✓ {case['name']}")
                print(f"    Weight: {stats['weight_grams']:.1f}g")
            else:
                print(f"\n  ⚠ {case['name']} - No geometry generated")

        except Exception as e:
            print(f"\n  ❌ {case['name']}")
            print(f"    Error: {str(e)}")


def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════╗")
    print("║  19\" Rack Mount Generator - Test Suite          ║")
    print("╚══════════════════════════════════════════════════╝")

    try:
        test_basic_generation()
        test_different_sizes()
        test_tolerances()
        test_infill_settings()
        test_file_generation()
        test_edge_cases()

        print_header("Test Summary")
        print("\n✅ All tests completed successfully!")
        print("\nGenerated test files are in: ./test_output/")
        print("You can now open these files in Cura or your slicer.")

    except Exception as e:
        print_header("Test Error")
        print(f"\n❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
