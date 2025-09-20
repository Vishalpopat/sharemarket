"""
Market service for coordinating stock analysis
"""

import sys
import os
import pandas as pd
from typing import List, Dict

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from src.data.providers.yahoo_finance_provider import YahooFinanceProvider
from src.core.strategies.base_strategy import BaseStrategy

class MarketService:
    """Service for coordinating market analysis and stock recommendations"""
    
    def __init__(self):
        """Initialize market service"""
        self.data_provider = YahooFinanceProvider()
        
    def analyze_stocks(self, symbols: List[str], strategy: BaseStrategy) -> List[Dict]:
        """
        Analyze multiple stocks using given strategy
        
        Args:
            symbols: List of stock symbols
            strategy: Trading strategy to use
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for symbol in symbols:
            try:
                print(f"📊 Analyzing {symbol.replace('.NS', '')}...")
                
                # Get stock data
                data = self.data_provider.get_stock_data(symbol, strategy.timeframe)
                
                if data is None or data.empty:
                    logger.warning(f"No data available for {symbol}")
                    continue
                
                # Validate data
                if not strategy.validate_data(data):
                    logger.warning(f"Invalid data for {symbol}")
                    continue
                
                # Analyze using strategy
                recommendation = strategy.analyze(data, symbol)
                
                if recommendation:
                    recommendations.append(recommendation)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                # Add default recommendation for failed analysis
                try:
                    default_rec = strategy._default_recommendation(symbol, pd.DataFrame())
                    recommendations.append(default_rec)
                except:
                    pass
        
        return recommendations
    
    def display_market_overview(self):
        """Display market overview"""
        print("\n🌍 INDIAN MARKET OVERVIEW")
        print("=" * 50)
        
        # Major indices to check
        indices = {
            "^NSEI": "NIFTY 50",
            "^NSEBANK": "NIFTY BANK", 
            "^NSEIT": "NIFTY IT",
            "^CNXIT": "NIFTY IT"
        }
        
        for symbol, name in indices.items():
            try:
                data = self.data_provider.get_stock_data(symbol, "1d", period="5d")
                if data is not None and not data.empty:
                    current = data['Close'].iloc[-1]
                    previous = data['Close'].iloc[-2] if len(data) > 1 else current
                    change = current - previous
                    change_pct = (change / previous) * 100
                    
                    status = "🟢" if change >= 0 else "🔴"
                    print(f"{status} {name}: ₹{current:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
                else:
                    print(f"⚪ {name}: Data not available")
            except Exception as e:
                print(f"⚪ {name}: Error fetching data")
                logger.error(f"Error fetching {symbol}: {e}")
        
        print("\n📈 Market Status: Live data from Yahoo Finance")
        print("💡 Note: Data may have 15-20 minute delay")
        print("=" * 50)
