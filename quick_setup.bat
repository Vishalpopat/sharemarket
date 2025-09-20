@echo off
echo 🇮🇳 ShareMarket Analysis Tool - Quick Setup
echo ==========================================

echo.
echo Choose setup method:
echo 1. Install in current virtual environment (Quick)
echo 2. Setup with Poetry (Recommended)
echo 3. Setup with pip + venv (Classic)
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🔧 Installing in current environment...
    python install_dependencies.py
    echo.
    echo ✅ Testing installation...
    python test_imports.py
    echo.
    echo 🚀 Ready to run: python main.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo 📦 Setting up with Poetry...
    python setup_poetry.py
    echo.
    echo 🚀 Ready to run: poetry run python main.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo 🔧 Setting up with pip + venv...
    python setup.py
    echo.
    echo 🚀 Ready to run after activation: python main.py
    pause
) else (
    echo ❌ Invalid choice!
    pause
)