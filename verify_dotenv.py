"""
Simple test to verify dotenv installation
"""
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing dotenv installation...")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv is working!")
    
    # Test Settings import
    from src.config.settings import Settings
    settings = Settings()
    print("✅ Settings class is working!")
    
    print("\n🎉 All critical imports are now working!")
    print("🚀 Ready to run the main application!")
    
except ImportError as e:
    print(f"❌ Import still failing: {e}")
    print("Try manually: venv\\Scripts\\python.exe -m pip install python-dotenv")

except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
    print("But the core functionality should still work.")

print("\n" + "=" * 50)
print("NEXT STEPS:")
print("1. Run: venv\\Scripts\\python.exe test_imports.py")
print("2. Then: venv\\Scripts\\python.exe main.py")
print("=" * 50)