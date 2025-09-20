"""
Quick test to check import issues
"""
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🔍 Testing imports...")
print("=" * 40)

try:
    from src.core.strategies.base_strategy import BaseStrategy
    print("✅ BaseStrategy import successful")
except Exception as e:
    print(f"❌ BaseStrategy import failed: {e}")

try:
    from src.core.indicators.technical_indicators import TechnicalIndicators
    print("✅ TechnicalIndicators import successful")
except Exception as e:
    print(f"❌ TechnicalIndicators import failed: {e}")

try:
    from src.core.strategies.intraday_strategy import IntradayStrategy
    print("✅ IntradayStrategy import successful")
except Exception as e:
    print(f"❌ IntradayStrategy import failed: {e}")

try:
    from src.core.strategies.swing_trading_strategy import SwingTradingStrategy
    print("✅ SwingTradingStrategy import successful")
except Exception as e:
    print(f"❌ SwingTradingStrategy import failed: {e}")

try:
    from src.services.market_service import MarketService
    print("✅ MarketService import successful")
except Exception as e:
    print(f"❌ MarketService import failed: {e}")

try:
    from src.data.stock_lists import get_stock_list
    print("✅ stock_lists import successful")
except Exception as e:
    print(f"❌ stock_lists import failed: {e}")

try:
    from src.config.settings import Settings
    print("✅ Settings import successful")
except Exception as e:
    print(f"❌ Settings import failed: {e}")

try:
    from src.data.providers.yahoo_finance_provider import YahooFinanceProvider
    print("✅ YahooFinanceProvider import successful")
except Exception as e:
    print(f"❌ YahooFinanceProvider import failed: {e}")

print("=" * 40)
print("🎯 Import test completed!")

# Test basic functionality
print("\n🧪 Testing basic functionality...")
try:
    from src.config.settings import Settings
    settings = Settings()
    print("✅ Settings initialization successful")
    
    stocks = get_stock_list('NIFTY_50')
    print(f"✅ Stock list loaded: {len(stocks)} stocks")
    
    from src.core.strategies.intraday_strategy import IntradayStrategy
    strategy = IntradayStrategy()
    print("✅ IntradayStrategy initialization successful")
    
    from src.services.market_service import MarketService
    market_service = MarketService()
    print("✅ MarketService initialization successful")
    
    print("\n🎉 All basic tests passed!")
    print("🚀 Ready to run: python main.py")
    
except Exception as e:
    print(f"❌ Basic functionality test failed: {e}")
    print("⚠️  Some components may not work, but core functionality should be available")

print("\nImport test completed!")