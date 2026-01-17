@echo off
REM 19" Rack Mount Generator - Startup Script for Windows

echo.
echo 🔧 19" Rack Mount Generator - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION%
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install/update dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Check for required files
if not exist "app.py" (
    echo ❌ app.py not found in current directory
    pause
    exit /b 1
)

if not exist "index.html" (
    echo ❌ index.html not found in current directory
    pause
    exit /b 1
)

if not exist "stl_generator.py" (
    echo ❌ stl_generator.py not found in current directory
    pause
    exit /b 1
)

echo ✓ All required files found
echo.

REM Display startup info
echo ========================================
echo 🚀 Starting Server...
echo ========================================
echo.
echo 📍 Web Interface: http://localhost:5000
echo 📝 API Base: http://localhost:5000/api
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

pause
