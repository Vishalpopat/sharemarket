"""
Test the fixed data provider and strategies
"""
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing Fixed Data Provider...")
print("=" * 50)

try:
    from src.data.providers.yahoo_finance_provider import YahooFinanceProvider
    from src.core.strategies.intraday_strategy import IntradayStrategy
    from src.services.market_service import MarketService
    
    # Test data provider
    provider = YahooFinanceProvider()
    print("✅ Data provider initialized")
    
    # Test with a single stock
    print("📊 Testing with RELIANCE.NS...")
    data = provider.get_stock_data("RELIANCE.NS", "1d", "1mo")
    
    if data is not None:
        print(f"✅ Data fetched successfully: {len(data)} rows")
        print(f"   Columns: {list(data.columns)}")
        print(f"   Date range: {data.index[0] if not data.empty else 'N/A'} to {data.index[-1] if not data.empty else 'N/A'}")
        
        # Test strategy
        strategy = IntradayStrategy()
        print("✅ Strategy initialized")
        
        # Test analysis
        result = strategy.analyze(data, "RELIANCE.NS")
        if result:
            print("✅ Analysis completed")
            print(f"   Action: {result['action']}")
            print(f"   Confidence: {result['confidence']:.1f}%")
            print(f"   Current: ₹{result['current_price']:.2f}")
            print(f"   Target: ₹{result['target']:.2f}")
        else:
            print("❌ Analysis failed")
    else:
        print("❌ No data fetched")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("🚀 Try running: venv\\Scripts\\python.exe main.py")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()