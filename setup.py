"""
Cross-platform setup script for Indian Stock Market Analysis Tool
This script creates a virtual environment and installs dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python():
    """Check if Python is available"""
    success, stdout, stderr = run_command("python --version", check=False)
    if success:
        return True, "python"
    
    success, stdout, stderr = run_command("python3 --version", check=False)
    if success:
        return True, "python3"
    
    return False, None

def create_virtual_environment():
    """Create and setup virtual environment"""
    print("=" * 50)
    print("🇮🇳 Indian Stock Market Analysis Tool Setup")
    print("=" * 50)
    
    # Check Python installation
    print("Checking Python installation...")
    python_available, python_cmd = check_python()
    
    if not python_available:
        print("❌ ERROR: Python is not installed or not in PATH")
        print("Please install Python from https://python.org")
        return False
    
    print(f"✓ Python found: {python_cmd}")
    
    # Remove existing virtual environment
    venv_path = Path("venv")
    if venv_path.exists():
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    # Create virtual environment with pip
    print("Creating virtual environment...")
    success, stdout, stderr = run_command(f"{python_cmd} -m venv venv --with-pip")
    
    if not success:
        print("Trying without --with-pip flag...")
        success, stdout, stderr = run_command(f"{python_cmd} -m venv venv")
        
        if not success:
            print(f"❌ ERROR: Failed to create virtual environment")
            print(f"Error: {stderr}")
            return False
    
    print("✓ Virtual environment created")
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate.bat"
        pip_path = "venv\\Scripts\\pip.exe"
        python_venv = "venv\\Scripts\\python.exe"
    else:
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
        python_venv = "venv/bin/python"
    
    # Bootstrap pip if not available
    print("Ensuring pip is available...")
    success, stdout, stderr = run_command(f"{python_venv} -m pip --version", check=False)
    
    if not success:
        print("Installing pip...")
        # Download and install pip
        get_pip_cmd = f"{python_venv} -m ensurepip --default-pip"
        success, stdout, stderr = run_command(get_pip_cmd, check=False)
        
        if not success:
            print("Trying alternative pip installation...")
            # Alternative: try using get-pip.py
            import urllib.request
            try:
                urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
                success, stdout, stderr = run_command(f"{python_venv} get-pip.py")
                os.remove("get-pip.py")
            except Exception as e:
                print(f"⚠️ Could not install pip: {e}")
    
    # Upgrade pip in virtual environment
    print("Upgrading pip...")
    success, stdout, stderr = run_command(f"{python_venv} -m pip install --upgrade pip")
    
    if not success:
        print(f"⚠️ Warning: Failed to upgrade pip: {stderr}")
        # Try using the pip executable directly
        success, stdout, stderr = run_command(f"{pip_path} install --upgrade pip", check=False)
        if success:
            print("✓ Pip upgraded using direct path")
        else:
            print("⚠️ Pip upgrade failed, continuing anyway...")
    else:
        print("✓ Pip upgraded")
    
    # Install dependencies
    print("Installing dependencies...")
    success, stdout, stderr = run_command(f"{pip_path} install -r requirements.txt")
    
    if not success:
        print(f"❌ ERROR: Failed to install dependencies")
        print(f"Error: {stderr}")
        print("\nTrying to install packages individually...")
        
        # Try installing packages one by one
        packages = [
            "yfinance", "pandas", "numpy", "scikit-learn", 
            "matplotlib", "seaborn", "plotly", "ta", 
            "requests", "python-dotenv", "loguru"
        ]
        
        failed_packages = []
        for package in packages:
            print(f"Installing {package}...")
            success, _, err = run_command(f"{pip_path} install {package}", check=False)
            if not success:
                failed_packages.append(package)
                print(f"⚠️ Failed to install {package}")
            else:
                print(f"✓ {package} installed")
        
        if failed_packages:
            print(f"\n⚠️ Some packages failed to install: {', '.join(failed_packages)}")
            print("The tool may still work with reduced functionality.")
    else:
        print("✓ All dependencies installed successfully")
    
    # Test the installation
    print("\nTesting installation...")
    success, stdout, stderr = run_command(f"{python_venv} test_setup.py")
    
    if success:
        print("✓ Installation test passed")
    else:
        print(f"⚠️ Installation test failed: {stderr}")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("=" * 50)
    
    # Display activation instructions
    if platform.system() == "Windows":
        print("\nTo activate the virtual environment:")
        print("  venv\\Scripts\\activate")
        print("\nTo run the application:")
        print("  python main.py")
        print("\nTo deactivate:")
        print("  deactivate")
    else:
        print("\nTo activate the virtual environment:")
        print("  source venv/bin/activate")
        print("\nTo run the application:")
        print("  python main.py")
        print("\nTo deactivate:")
        print("  deactivate")
    
    return True

def main():
    """Main setup function"""
    try:
        success = create_virtual_environment()
        if success:
            print("\n✅ Setup completed successfully!")
            print("You can now run 'python main.py' after activating the virtual environment.")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
