"""
Market service for coordinating stock analysis
"""

import sys
import os
import pandas as pd
from typing import List, Dict, Any

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
    
    def analyze_stocks_bulk(self, symbols: List[str], strategy) -> List[Dict[str, Any]]:
        """
        Analyze multiple stocks using bulk data fetching for better performance.
        """
        recommendations = []
        
        # Get bulk data for all symbols
        print(f"🔍 Fetching data for {len(symbols)} stocks using bulk processing...")
        bulk_data = self._fetch_bulk_data(symbols)
        
        print(f"✅ Retrieved data for {len(bulk_data)} stocks. Analyzing...")
        
        for symbol, data in bulk_data.items():
            if data is not None and not data.empty:
                try:
                    recommendation = strategy.analyze(data, symbol)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.debug(f"Error analyzing {symbol}: {e}")
        
        return recommendations
    
    def _fetch_bulk_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks in bulk for better performance.
        """
        bulk_data = {}
        batch_size = 20  # Process in batches
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_progress = f"[{i+1}-{min(i+batch_size, len(symbols))}/{len(symbols)}]"
            print(f"\r🔄 Processing batch {batch_progress}...", end="", flush=True)
            
            try:
                # Try to use yfinance for bulk download if available
                try:
                    import yfinance as yf
                    batch_symbols = " ".join(batch)
                    data = yf.download(batch_symbols, period="1y", interval="1d", 
                                     group_by='ticker', progress=False, threads=True,
                                     auto_adjust=False)  # Fix FutureWarning
                    
                    if len(batch) == 1:
                        # Single stock case
                        symbol = batch[0]
                        if not data.empty:
                            # Ensure required columns are present
                            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                            if all(col in data.columns for col in required_columns):
                                bulk_data[symbol] = data
                    else:
                        # Multiple stocks case
                        for symbol in batch:
                            try:
                                if hasattr(data.columns, 'levels') and symbol in data.columns.levels[0]:
                                    stock_data = data[symbol]
                                    if not stock_data.empty and not stock_data.isna().all().all():
                                        # Check if we have required columns
                                        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                                        if all(col in stock_data.columns for col in required_columns):
                                            bulk_data[symbol] = stock_data
                            except (KeyError, AttributeError, IndexError):
                                continue
                                
                except ImportError:
                    # Fallback to individual calls if yfinance not available
                    for symbol in batch:
                        try:
                            stock_data = self.data_provider.get_stock_data(symbol)
                            if stock_data is not None and not stock_data.empty:
                                bulk_data[symbol] = stock_data
                        except Exception:
                            continue
                            
            except Exception as e:
                logger.debug(f"Error fetching batch {batch_progress}: {e}")
                # Fallback to individual calls for this batch
                for symbol in batch:
                    try:
                        stock_data = self.data_provider.get_stock_data(symbol)
                        if stock_data is not None and not stock_data.empty:
                            bulk_data[symbol] = stock_data
                    except Exception:
                        continue
        
        print("\r" + " " * 50 + "\r", end="")  # Clear the line
        return bulk_data

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
