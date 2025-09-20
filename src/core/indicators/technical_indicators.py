"""
Technical indicators for stock analysis
"""

import pandas as pd
import numpy as np
from typing import Tuple
import sys
import os

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Technical indicators calculation class"""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize with stock data"""
        self.data = data.copy()
        
    def rsi(self, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            close = self.data['Close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50)
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series([50] * len(self.data))
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        try:
            close = self.data['Close']
            exp1 = close.ewm(span=fast).mean()
            exp2 = close.ewm(span=slow).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            return macd_line.fillna(0), signal_line.fillna(0), histogram.fillna(0)
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            zeros = pd.Series([0] * len(self.data))
            return zeros, zeros, zeros
    
    def sma(self, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        try:
            return self.data['Close'].rolling(window=period).mean().bfill()
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return self.data['Close'].bfill()
    
    def ema(self, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        try:
            return self.data['Close'].ewm(span=period).mean().bfill()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return self.data['Close'].bfill()
    
    def bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            close = self.data['Close']
            sma = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return upper.bfill(), sma.bfill(), lower.bfill()
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            close = self.data['Close'].bfill()
            return close, close, close
    
    def stochastic(self, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        try:
            high = self.data['High']
            low = self.data['Low']
            close = self.data['Close']
            
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return k_percent.fillna(50), d_percent.fillna(50)
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            default_series = pd.Series([50] * len(self.data))
            return default_series, default_series
    
    def atr(self, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = self.data['High']
            low = self.data['Low']
            close = self.data['Close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr.fillna(1.0)
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series([1.0] * len(self.data))
    
    def volume_sma(self, period: int = 20) -> pd.Series:
        """Calculate Volume Simple Moving Average"""
        try:
            return self.data['Volume'].rolling(window=period).mean().bfill()
        except Exception as e:
            logger.error(f"Error calculating Volume SMA: {e}")
            return self.data['Volume'].bfill()
