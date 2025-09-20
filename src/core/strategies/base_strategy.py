"""
Base strategy class for all trading strategies
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self):
        self.timeframe = "1d"  # Default timeframe
        self.min_confidence = 50  # Minimum confidence threshold
        
    @abstractmethod
    def analyze(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Analyze stock data and return trading recommendation
        
        Args:
            data: Historical stock data
            symbol: Stock symbol
            
        Returns:
            Dict containing recommendation details
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        if data is None or data.empty:
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        if len(data) < 20:  # Minimum data points for analysis
            return False
            
        return True
    
    def _default_recommendation(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Return default recommendation when analysis fails"""
        try:
            current_price = float(data['Close'].iloc[-1])
        except:
            current_price = 100.0  # Fallback price
            
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 20,
            'current_price': current_price,
            'target': current_price * 1.02,  # 2% default target
            'stop_loss': current_price * 0.98,  # 2% default stop
            'risk_reward': 1.0,
            'reason': 'Default recommendation due to insufficient data or analysis error'
        }
