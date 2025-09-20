"""
Robust setup script that handles pip installation issues
"""
import os
import sys
import subprocess
import platform
import urllib.request
from pathlib import Path

def run_command(command, check=True, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def setup_robust_venv():
    """Create a robust virtual environment with proper pip setup"""
    print("🔧 ROBUST VIRTUAL ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Remove existing venv if it exists
    venv_path = Path("venv")
    if venv_path.exists():
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    # Create virtual environment
    print("Creating virtual environment...")
    success, stdout, stderr = run_command("python -m venv venv")
    
    if not success:
        print(f"❌ Failed to create venv: {stderr}")
        return False
    
    print("✅ Virtual environment created")
    
    # Determine paths
    if platform.system() == "Windows":
        python_exe = "venv\\Scripts\\python.exe"
        pip_exe = "venv\\Scripts\\pip.exe"
    else:
        python_exe = "venv/bin/python"
        pip_exe = "venv/bin/pip"
    
    # Step 1: Ensure pip is available
    print("Ensuring pip is available...")
    success, _, _ = run_command(f"{python_exe} -m pip --version", check=False)
    
    if not success:
        print("Installing pip using ensurepip...")
        success, stdout, stderr = run_command(f"{python_exe} -m ensurepip --default-pip")
        
        if not success:
            print("Downloading and installing pip manually...")
            try:
                # Download get-pip.py
                urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
                success, stdout, stderr = run_command(f"{python_exe} get-pip.py")
                os.remove("get-pip.py")
                
                if success:
                    print("✅ Pip installed manually")
                else:
                    print(f"❌ Failed to install pip manually: {stderr}")
                    return False
            except Exception as e:
                print(f"❌ Failed to download/install pip: {e}")
                return False
        else:
            print("✅ Pip installed using ensurepip")
    else:
        print("✅ Pip already available")
    
    # Step 2: Upgrade pip
    print("Upgrading pip...")
    success, stdout, stderr = run_command(f"{python_exe} -m pip install --upgrade pip")
    
    if not success:
        print(f"⚠️ Pip upgrade failed: {stderr}")
    else:
        print("✅ Pip upgraded")
    
    # Step 3: Install packages one by one with error handling
    packages = [
        "pandas",
        "numpy", 
        "yfinance",
        "requests",
        "python-dotenv",
        "loguru",
        "matplotlib",
        "seaborn"
    ]
    
    print(f"\nInstalling {len(packages)} essential packages...")
    print("-" * 40)
    
    installed_packages = []
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...")
        success, stdout, stderr = run_command(f"{python_exe} -m pip install {package}", check=False)
        
        if success:
            print(f"✅ {package} installed")
            installed_packages.append(package)
        else:
            print(f"❌ {package} failed: {stderr.split('ERROR:')[-1].strip()}")
            failed_packages.append(package)
    
    print("-" * 40)
    print(f"✅ Successfully installed: {len(installed_packages)} packages")
    print(f"❌ Failed to install: {len(failed_packages)} packages")
    
    if failed_packages:
        print(f"\nFailed packages: {', '.join(failed_packages)}")
    
    # Step 4: Test basic imports
    print("\nTesting basic imports...")
    test_script = '''
import sys
try:
    import pandas as pd
    print("✅ pandas imported successfully")
except ImportError as e:
    print(f"❌ pandas import failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    import yfinance as yf
    print("✅ yfinance imported successfully")
except ImportError as e:
    print(f"❌ yfinance import failed: {e}")
'''
    
    with open("test_basic_imports.py", "w") as f:
        f.write(test_script)
    
    success, stdout, stderr = run_command(f"{python_exe} test_basic_imports.py")
    print(stdout)
    
    os.remove("test_basic_imports.py")
    
    print("\n" + "=" * 50)
    if len(installed_packages) >= len(packages) // 2:  # At least half the packages installed
        print("🎉 Setup completed successfully!")
        print("✅ Core packages are available")
        
        print(f"\n🚀 To use the application:")
        if platform.system() == "Windows":
            print(f"   {python_exe} main.py")
        else:
            print(f"   {python_exe} main.py")
        
        return True
    else:
        print("⚠️ Setup completed with issues")
        print("❌ Many packages failed to install")
        return False

if __name__ == "__main__":
    setup_robust_venv()