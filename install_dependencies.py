"""
Quick dependency installer for the current virtual environment
"""
import subprocess
import sys

def install_packages():
    """Install required packages in current environment"""
    
    required_packages = [
        "pandas>=1.5.0",
        "numpy>=1.21.0", 
        "yfinance>=0.2.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "loguru>=0.6.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0"
    ]
    
    print("🔧 Installing required packages...")
    print("=" * 50)
    
    failed_packages = []
    successful_packages = []
    
    for package in required_packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ {package} installed successfully")
            successful_packages.append(package)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            print(f"   Error: {e.stderr}")
            failed_packages.append(package)
    
    print("=" * 50)
    print(f"✅ Successfully installed: {len(successful_packages)} packages")
    print(f"❌ Failed to install: {len(failed_packages)} packages")
    
    if failed_packages:
        print(f"\nFailed packages: {', '.join(failed_packages)}")
        print("\nYou can try installing them manually:")
        for pkg in failed_packages:
            print(f"  pip install {pkg}")
    
    if successful_packages:
        print(f"\n🎉 Ready to test! Try running: python test_imports.py")
    
    return len(failed_packages) == 0

if __name__ == "__main__":
    install_packages()