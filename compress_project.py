"""
Project Compression Utility
Creates a clean ZIP file with only source code and documentation
"""
import os
import zipfile
import shutil
from datetime import datetime
import sys

def create_distribution_zip():
    """Create a distribution ZIP with only source code and documentation."""
    
    # Files and folders to include
    include_files = [
        'src/',
        'main.py',
        'main_enhanced.py', 
        'test_setup.py',
        'requirements.txt',
        'README.md',
        'VIRTUAL_ENV_GUIDE.md',
        'SETUP_COMPLETE.md',
        '.env.example',
        'setup.py',
        'setup.bat',
        'setup.sh',
        'activate.bat',
        'activate.sh',
        '.gitignore'
    ]
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"ShareMarket_Source_{timestamp}.zip"
    
    print(f"📦 Creating distribution ZIP: {zip_filename}")
    print("=" * 50)
    
    total_files = 0
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_files:
            if os.path.exists(item):
                if os.path.isfile(item):
                    zipf.write(item)
                    total_files += 1
                    print(f"✅ Added file: {item}")
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        # Skip __pycache__ directories
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        
                        for file in files:
                            # Skip .pyc files
                            if not file.endswith('.pyc'):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                                total_files += 1
                                print(f"✅ Added: {file_path}")
            else:
                print(f"⚠️  Not found: {item}")
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_filename)
    size_mb = zip_size / (1024 * 1024)
    
    print("=" * 50)
    print(f"🎉 Distribution ZIP created successfully!")
    print(f"📁 Filename: {zip_filename}")
    print(f"📊 Size: {size_mb:.2f} MB")
    print(f"📂 Files: {total_files}")
    print(f"📍 Location: {os.path.abspath(zip_filename)}")
    print("\n💡 This ZIP contains only source code and documentation.")
    print("💡 Recipients can extract and run 'python setup.py' to create their own environment.")
    
    return zip_filename

def cleanup_project():
    """Clean up project for sharing - remove heavy files and cache."""
    
    print("🧹 Cleaning up project for sharing...")
    print("=" * 40)
    
    # Remove venv directory
    if os.path.exists('venv'):
        print("🗑️  Removing virtual environment...")
        try:
            shutil.rmtree('venv')
            print("✅ Virtual environment removed")
        except Exception as e:
            print(f"❌ Error removing venv: {e}")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Removed: {pycache_path}")
            except Exception as e:
                print(f"❌ Error removing {pycache_path}: {e}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
                except Exception as e:
                    print(f"❌ Error removing {file_path}: {e}")
    
    # Optional: Clear large log files but keep directory structure
    if os.path.exists('logs'):
        for file in os.listdir('logs'):
            if file.endswith('.log'):
                file_path = os.path.join('logs', file)
                try:
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    if file_size > 1:  # Remove logs larger than 1MB
                        os.remove(file_path)
                        print(f"✅ Removed large log: {file} ({file_size:.2f} MB)")
                except Exception as e:
                    print(f"❌ Error with log {file}: {e}")
    
    print("=" * 40)
    print("🎉 Cleanup completed!")
    
    # Show final directory size
    total_size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass
    
    final_size_mb = total_size / (1024 * 1024)
    print(f"📊 Final project size: {final_size_mb:.2f} MB")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "cleanup":
            cleanup_project()
        elif sys.argv[1] == "zip":
            create_distribution_zip()
        elif sys.argv[1] == "all":
            cleanup_project()
            create_distribution_zip()
        else:
            print("Usage: python compress_project.py [cleanup|zip|all]")
    else:
        # Interactive mode
        print("\n📦 ShareMarket Project Compression Utility")
        print("=" * 45)
        print("1. Clean up project (remove venv, cache files)")
        print("2. Create distribution ZIP")
        print("3. Do both (cleanup + ZIP)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            cleanup_project()
        elif choice == '2':
            create_distribution_zip()
        elif choice == '3':
            cleanup_project()
            create_distribution_zip()
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()