"""
Quick test to demonstrate the difference between intraday and swing strategies
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.market_service import MarketService
from src.core.strategies.intraday_strategy import IntradayStrategy
from src.core.strategies.swing_trading_strategy import SwingTradingStrategy

def compare_strategies():
    print("=" * 70)
    print("🔍 INTRADAY vs SWING STRATEGY COMPARISON")
    print("=" * 70)
    
    # Initialize market service
    market_service = MarketService()
    
    # Test with a single stock
    test_stock = ['RELIANCE.NS']
    
    print("\n📈 INTRADAY STRATEGY RESULTS:")
    print("-" * 40)
    intraday_strategy = IntradayStrategy()
    intraday_recs = market_service.analyze_stocks(test_stock, intraday_strategy)
    
    if intraday_recs:
        rec = intraday_recs[0]
        print(f"Stock: {rec['symbol'].replace('.NS', '')}")
        print(f"Current Price: ₹{rec['current_price']:.2f}")
        print(f"Target: ₹{rec['target']:.2f} ({((rec['target']/rec['current_price']-1)*100):+.2f}%)")
        print(f"Stop Loss: ₹{rec['stop_loss']:.2f} ({((rec['stop_loss']/rec['current_price']-1)*100):+.2f}%)")
        print(f"Risk-Reward: {rec['risk_reward']:.2f}")
        print(f"Confidence: {rec['confidence']:.1f}%")
    
    print("\n📊 SWING STRATEGY RESULTS:")
    print("-" * 40)
    swing_strategy = SwingTradingStrategy()
    swing_recs = market_service.analyze_stocks(test_stock, swing_strategy)
    
    if swing_recs:
        rec = swing_recs[0]
        print(f"Stock: {rec['symbol'].replace('.NS', '')}")
        print(f"Current Price: ₹{rec['current_price']:.2f}")
        print(f"Target: ₹{rec['target']:.2f} ({((rec['target']/rec['current_price']-1)*100):+.2f}%)")
        print(f"Stop Loss: ₹{rec['stop_loss']:.2f} ({((rec['stop_loss']/rec['current_price']-1)*100):+.2f}%)")
        print(f"Risk-Reward: {rec['risk_reward']:.2f}")
        print(f"Confidence: {rec['confidence']:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ Key Differences:")
    print("• Intraday: Shorter timeframe (5m), smaller targets (2.5%), tighter stops (1.5%)")
    print("• Swing: Longer timeframe (1d), larger targets (6%), wider stops (3%)")
    print("• Different risk-reward profiles for different trading styles")
    print("=" * 70)

if __name__ == "__main__":
    compare_strategies()
