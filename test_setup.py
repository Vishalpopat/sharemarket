"""
Test script to verify the stock market analysis tool setup
"""

import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test data models
        from src.data.models.market_models import StockData, TradingRecommendation
        print("✓ Data models imported successfully")
        
        # Test strategies
        from src.core.strategies.intraday_strategy import IntradayStrategy
        from src.core.strategies.swing_trading_strategy import SwingTradingStrategy
        print("✓ Trading strategies imported successfully")
        
        # Test technical indicators
        from src.core.indicators.technical_indicators import TechnicalIndicatorCalculator
        print("✓ Technical indicators imported successfully")
        
        # Test market service
        from src.services.market_service import MarketService
        print("✓ Market service imported successfully")
        
        # Test configuration
        from src.config.settings import Settings
        print("✓ Configuration imported successfully")
        
        print("All imports successful! The tool is ready to use.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    try:
        print("\nTesting basic functionality...")
        
        # Test strategy creation
        from src.core.strategies.intraday_strategy import IntradayStrategy
        strategy = IntradayStrategy()
        print(f"✓ Created {strategy.name}")
        
        # Test settings
        from src.config.settings import Settings
        settings = Settings()
        config = settings.get_trading_config('intraday')
        print(f"✓ Loaded trading config: {len(config)} parameters")
        
        print("Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Indian Stock Market Analysis Tool - Setup Test")
    print("=" * 55)
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup test failed. Please check the installation.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality test failed.")
        return False
    
    print("All tests passed! You can now run the main application.")
    print("\nTo start the application, run:")
    print("  python main.py")
    print("\nMake sure to install dependencies first:")
    print("  pip install -r requirements.txt")
    
    return True

if __name__ == "__main__":
    main()
