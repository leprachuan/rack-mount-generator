#!/usr/bin/env python3
"""
Setup verification script
Checks that all dependencies and files are correctly installed
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check Python version"""
    print("\n🐍 Python Version Check")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python 3.8+ (Required)")
        return True
    else:
        print("   ❌ Python 3.8+ required (Current: {version.major}.{version.minor})")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Dependency Check")

    dependencies = {
        'flask': 'Flask (Web Framework)',
        'flask_cors': 'Flask-CORS (CORS Support)',
        'numpy': 'NumPy (Numerical Computing)',
        'werkzeug': 'Werkzeug (WSGI Utilities)',
    }

    all_ok = True

    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (Missing)")
            all_ok = False

    if not all_ok:
        print("\n   💡 Install missing dependencies:")
        print("      pip install -r requirements.txt")

    return all_ok


def check_files():
    """Check if all required files exist"""
    print("\n📁 File Check")

    required_files = {
        'index.html': 'Web Interface',
        'app.py': 'Flask Application',
        'stl_generator.py': 'STL Generation Engine',
        'requirements.txt': 'Dependencies',
        'README.md': 'Documentation',
    }

    all_ok = True

    for filename, description in required_files.items():
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            size_str = f"({file_size / 1024:.1f} KB)"
            print(f"   ✅ {filename:20} {description:30} {size_str}")
        else:
            print(f"   ❌ {filename:20} {description:30} (Missing)")
            all_ok = False

    return all_ok


def check_file_integrity():
    """Check file integrity and content"""
    print("\n🔍 File Integrity Check")

    # Check index.html for key content
    if os.path.exists('index.html'):
        with open('index.html', 'r') as f:
            content = f.read()
            checks = {
                'Three.js': 'three.js' in content.lower(),
                'API endpoint': '/api/generate' in content,
                'Form elements': 'id="deviceWidth"' in content,
            }

            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} index.html - {check_name}")

    # Check app.py for key functions
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
            checks = {
                'Flask app': "app = Flask(__name__" in content,
                'API routes': "@app.route('/api" in content,
                'STL generation': "from stl_generator import" in content,
            }

            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} app.py - {check_name}")

    # Check stl_generator.py for key classes
    if os.path.exists('stl_generator.py'):
        with open('stl_generator.py', 'r') as f:
            content = f.read()
            checks = {
                'RackMountGenerator': "class RackMountGenerator" in content,
                'STLWriter': "class STLWriter" in content,
                'Triangle generation': "create_bracket" in content,
            }

            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} stl_generator.py - {check_name}")

    return True


def check_directories():
    """Check if required directories can be created"""
    print("\n📂 Directory Check")

    # Check if temp directory is writable
    import tempfile
    temp_dir = tempfile.gettempdir()
    test_dir = os.path.join(temp_dir, 'rack_mounts_test')

    try:
        os.makedirs(test_dir, exist_ok=True)
        # Try to create a test file
        test_file = os.path.join(test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"   ✅ Temporary directory writable ({temp_dir})")
        return True
    except Exception as e:
        print(f"   ❌ Cannot write to temp directory: {str(e)}")
        return False


def check_stl_generation():
    """Test basic STL generation"""
    print("\n🔧 STL Generation Test")

    try:
        from stl_generator import RackMountGenerator

        # Create a simple generator
        gen = RackMountGenerator(100, 44, 200)
        parts = gen.generate_all_parts()

        if 'bracket_left' in parts:
            bracket = parts['bracket_left']
            print(f"   ✅ Basic generation works")
            print(f"      Generated bracket with {len(bracket)} triangles")
            return True
        else:
            print(f"   ❌ No bracket geometry generated")
            return False

    except Exception as e:
        print(f"   ❌ Generation failed: {str(e)}")
        return False


def check_port_availability():
    """Check if port 5000 is available"""
    print("\n🔌 Port Availability Check")

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))

    if result != 0:
        print(f"   ✅ Port 5000 is available")
        sock.close()
        return True
    else:
        print(f"   ⚠️  Port 5000 might be in use")
        print(f"      (This is only an issue if you start the server)")
        sock.close()
        return True  # Not a critical failure


def generate_summary(results):
    """Generate verification summary"""
    print_header("Verification Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"\n   Checks Passed: {passed}/{total}")

    if failed > 0:
        print(f"   ⚠️  Failed Checks: {failed}")
        print(f"\n   Failed items:")
        for check, result in results.items():
            if not result:
                print(f"   - {check}")
    else:
        print(f"   ✅ All checks passed!")

    return failed == 0


def main():
    """Run all verification checks"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  19\" Rack Mount Generator - Setup Verification         ║")
    print("╚══════════════════════════════════════════════════════════╝")

    results = {}

    # Run checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    results['Required Files'] = check_files()
    results['File Integrity'] = check_file_integrity()
    results['Directories'] = check_directories()
    results['STL Generation'] = check_stl_generation()
    results['Port Availability'] = check_port_availability()

    # Generate summary
    all_ok = generate_summary(results)

    # Provide next steps
    print_header("Next Steps")

    if all_ok:
        print("\n   ✅ Setup verification successful!")
        print("\n   You can now start the server:")
        print("\n   On macOS/Linux:")
        print("      ./run.sh")
        print("\n   On Windows:")
        print("      run.bat")
        print("\n   Then open: http://localhost:5000")
    else:
        print("\n   ⚠️  Please fix the issues above before running the server.")
        print("\n   Common fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Verify Python 3.8+: python --version")
        print("   3. Check all files are present")

    print("\n")

    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
