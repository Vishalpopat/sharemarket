"""
Install missing python-dotenv package
"""
import subprocess
import sys
import os

def install_dotenv():
    """Install python-dotenv package"""
    print("📦 Installing missing python-dotenv package...")
    
    venv_python = "venv\\Scripts\\python.exe" if os.name == 'nt' else "venv/bin/python"
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        return False
    
    try:
        result = subprocess.run([venv_python, "-m", "pip", "install", "python-dotenv"], 
                              capture_output=True, text=True, check=True)
        print("✅ python-dotenv installed successfully")
        
        # Test the installation
        print("Testing import...")
        test_result = subprocess.run([venv_python, "-c", "from dotenv import load_dotenv; print('dotenv import successful')"], 
                                   capture_output=True, text=True, check=True)
        print("✅ " + test_result.stdout.strip())
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install python-dotenv: {e}")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    install_dotenv()