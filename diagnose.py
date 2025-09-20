"""
Startup script to diagnose and fix common issues
"""
import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Warning: Python 3.8+ recommended")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_virtual_environment():
    """Check if virtual environment is active"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        return True
    else:
        print("⚠️  Virtual environment not detected")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'numpy', 'yfinance', 'requests', 
        'loguru', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n🔧 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_project_structure():
    """Check if project structure is correct"""
    required_dirs = ['src', 'src/core', 'src/core/strategies', 'src/core/indicators', 'src/services', 'src/data', 'src/config']
    required_files = [
        'src/core/strategies/base_strategy.py',
        'src/core/strategies/intraday_strategy.py',
        'src/core/strategies/swing_trading_strategy.py',
        'src/core/indicators/technical_indicators.py',
        'src/services/market_service.py',
        'src/data/stock_lists.py',
        'src/config/settings.py'
    ]
    
    missing_items = []
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            missing_items.append(dir_path)
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            missing_items.append(file_path)
    
    return missing_items

def test_imports():
    """Test if all modules can be imported"""
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    imports_to_test = [
        ('src.core.strategies.base_strategy', 'BaseStrategy'),
        ('src.core.indicators.technical_indicators', 'TechnicalIndicators'),
        ('src.core.strategies.intraday_strategy', 'IntradayStrategy'),
        ('src.core.strategies.swing_trading_strategy', 'SwingTradingStrategy'),
        ('src.services.market_service', 'MarketService'),
        ('src.data.stock_lists', 'get_stock_list'),
        ('src.config.settings', 'Settings')
    ]
    
    failed_imports = []
    
    for module_path, class_name in imports_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ Import: {module_path}.{class_name}")
        except Exception as e:
            print(f"❌ Failed import: {module_path}.{class_name} - {e}")
            failed_imports.append((module_path, class_name, str(e)))
    
    return failed_imports

def main():
    """Main diagnostic function"""
    print("🔍 SHAREMARKET PROJECT DIAGNOSTIC")
    print("=" * 50)
    
    # Check Python version
    print("\n1. Python Version Check:")
    python_ok = check_python_version()
    
    # Check virtual environment
    print("\n2. Virtual Environment Check:")
    venv_active = check_virtual_environment()
    
    # Check required packages
    print("\n3. Package Check:")
    missing_packages = check_required_packages()
    
    # Install missing packages if needed
    if missing_packages:
        install_choice = input("\nInstall missing packages? (y/n): ").strip().lower()
        if install_choice in ['y', 'yes']:
            install_success = install_missing_packages(missing_packages)
            if not install_success:
                print("❌ Installation failed. Please install manually:")
                print(f"pip install {' '.join(missing_packages)}")
                return False
        else:
            print("⚠️  Cannot proceed without required packages")
            return False
    
    # Check project structure
    print("\n4. Project Structure Check:")
    missing_structure = check_project_structure()
    
    if missing_structure:
        print(f"\n❌ Missing project components: {len(missing_structure)}")
        print("Please ensure all project files are present")
        return False
    
    # Test imports
    print("\n5. Import Test:")
    failed_imports = test_imports()
    
    if failed_imports:
        print(f"\n❌ Import failures: {len(failed_imports)}")
        for module_path, class_name, error in failed_imports:
            print(f"   {module_path}.{class_name}: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL CHECKS PASSED!")
    print("✅ Ready to run: python main.py")
    
    # Ask if user wants to run the main application
    run_app = input("\nRun the main application now? (y/n): ").strip().lower()
    if run_app in ['y', 'yes']:
        print("\n🚀 Starting ShareMarket Analysis Tool...")
        try:
            os.system("python main.py")
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
    
    return True

if __name__ == "__main__":
    main()