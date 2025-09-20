"""
Quick fix for the current venv pip issue
"""
import subprocess
import sys
import os
import urllib.request

def fix_pip_in_current_venv():
    """Fix pip in the existing virtual environment"""
    print("🔧 FIXING PIP IN CURRENT VIRTUAL ENVIRONMENT")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    venv_python = "venv\\Scripts\\python.exe" if os.name == 'nt' else "venv/bin/python"
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("Please run: python setup_robust.py")
        return False
    
    print("📦 Installing pip in virtual environment...")
    
    # Method 1: Try ensurepip
    print("Trying ensurepip...")
    try:
        result = subprocess.run([venv_python, "-m", "ensurepip", "--default-pip"], 
                              capture_output=True, text=True, check=True)
        print("✅ Pip installed using ensurepip")
    except subprocess.CalledProcessError:
        print("⚠️ ensurepip failed, trying manual installation...")
        
        # Method 2: Download get-pip.py
        try:
            print("Downloading get-pip.py...")
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            
            print("Installing pip...")
            result = subprocess.run([venv_python, "get-pip.py"], 
                                  capture_output=True, text=True, check=True)
            os.remove("get-pip.py")
            print("✅ Pip installed manually")
        except Exception as e:
            print(f"❌ Manual pip installation failed: {e}")
            return False
    
    # Test pip
    print("Testing pip...")
    try:
        result = subprocess.run([venv_python, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Pip is working: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pip test failed: {e}")
        return False
    
    # Upgrade pip
    print("Upgrading pip...")
    try:
        result = subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], 
                              capture_output=True, text=True, check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Pip upgrade failed: {e}")
    
    # Install essential packages
    essential_packages = ["pandas", "numpy", "yfinance", "requests", "loguru"]
    
    print(f"\nInstalling essential packages...")
    for package in essential_packages:
        print(f"Installing {package}...")
        try:
            result = subprocess.run([venv_python, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} failed: {e.stderr.split('ERROR:')[-1].strip()}")
    
    print("\n" + "=" * 50)
    print("🎉 Pip fix completed!")
    print("🚀 Try running: venv\\Scripts\\python.exe main.py")
    
    return True

if __name__ == "__main__":
    fix_pip_in_current_venv()