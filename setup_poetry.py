"""
Poetry Setup Script for ShareMarket Analysis Tool
"""
import subprocess
import sys
import os
from pathlib import Path

def check_poetry_installed():
    """Check if Poetry is installed"""
    try:
        result = subprocess.run(['poetry', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Poetry found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_poetry():
    """Install Poetry"""
    print("📦 Installing Poetry...")
    
    # Poetry installation command for Windows
    if os.name == 'nt':  # Windows
        install_cmd = [
            'powershell', '-Command',
            '(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -'
        ]
    else:  # Unix/Linux/macOS
        install_cmd = [
            'curl', '-sSL', 'https://install.python-poetry.org', '|', 'python3', '-'
        ]
    
    try:
        subprocess.run(install_cmd, check=True)
        print("✅ Poetry installed successfully")
        
        # Add Poetry to PATH (Windows)
        if os.name == 'nt':
            print("⚠️  Please restart your terminal or add Poetry to your PATH manually")
            print("   Poetry is typically installed to: %APPDATA%\\Python\\Scripts")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Poetry: {e}")
        return False

def setup_with_poetry():
    """Setup project using Poetry"""
    print("🚀 Setting up ShareMarket Analysis Tool with Poetry...")
    print("=" * 60)
    
    # Check if Poetry is installed
    if not check_poetry_installed():
        print("❌ Poetry not found. Installing Poetry...")
        if not install_poetry():
            print("❌ Failed to install Poetry. Please install manually:")
            print("   Visit: https://python-poetry.org/docs/#installation")
            return False
    
    # Initialize Poetry project (if not already initialized)
    print("\n📋 Configuring Poetry project...")
    
    # Install dependencies
    print("📦 Installing dependencies with Poetry...")
    try:
        result = subprocess.run(['poetry', 'install'], 
                              capture_output=True, text=True, check=True)
        print("✅ Dependencies installed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test the installation
    print("\n🧪 Testing installation...")
    try:
        result = subprocess.run(['poetry', 'run', 'python', 'test_imports.py'], 
                              capture_output=True, text=True, check=True)
        print("✅ Installation test passed")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Installation test failed: {e}")
        print(f"Error output: {e.stderr}")
    
    print("\n" + "=" * 60)
    print("🎉 Poetry setup completed!")
    print("=" * 60)
    
    print("\n📋 How to use:")
    print("  poetry shell          # Activate virtual environment")
    print("  poetry run python main.py    # Run the application")
    print("  poetry add <package>  # Add new dependencies")
    print("  poetry install        # Install dependencies")
    print("\n🚀 Quick start:")
    print("  poetry run python main.py")
    
    return True

def main():
    """Main setup function"""
    print("🇮🇳 Indian Stock Market Analysis Tool - Poetry Setup")
    print("=" * 60)
    
    # Check if pyproject.toml exists
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found!")
        print("   Please ensure you're in the correct directory")
        return False
    
    try:
        success = setup_with_poetry()
        if success:
            print("\n✅ Setup completed successfully!")
            print("\n🚀 Ready to run:")
            print("   poetry run python main.py")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            return False
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()