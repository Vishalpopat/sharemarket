"""
F&O Breakout Detection Module
Detects various technical breakout patterns for futures and options trading
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class BreakoutType(Enum):
    """Types of breakout patterns"""
    BOLLINGER_BULLISH = "Bollinger Bullish Breakout"
    BOLLINGER_BEARISH = "Bollinger Bearish Breakout"
    MOMENTUM_BULLISH = "Momentum Bullish Breakout"
    MOMENTUM_BEARISH = "Momentum Bearish Breakout"
    MACD_BULLISH = "MACD Bullish Crossover"
    MACD_BEARISH = "MACD Bearish Crossover"


@dataclass
class BreakoutSignal:
    """Data class for breakout signals"""
    symbol: str
    breakout_type: BreakoutType
    price: float
    timestamp: pd.Timestamp
    strength: float  # Signal strength 0-100
    details: Dict


class FNOBreakoutDetector:
    """Detects technical breakout patterns for F&O instruments"""
    
    def __init__(self, 
                 bb_period: int = 20, 
                 bb_std: float = 2.0,
                 momentum_period: int = 14,
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9):
        """
        Initialize breakout detector with technical indicator parameters
        
        Args:
            bb_period: Bollinger Bands period
            bb_std: Bollinger Bands standard deviation
            momentum_period: Momentum indicator period
            macd_fast: MACD fast EMA period
            macd_slow: MACD slow EMA period
            macd_signal: MACD signal line period
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.momentum_period = momentum_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df = df.copy()
        df['BB_Middle'] = df['close'].rolling(window=self.bb_period).mean()
        df['BB_Std'] = df['close'].rolling(window=self.bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (self.bb_std * df['BB_Std'])
        df['BB_Lower'] = df['BB_Middle'] - (self.bb_std * df['BB_Std'])
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Percent'] = (df['close'] - df['BB_Lower']) / df['BB_Width']
        return df
    
    def calculate_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Momentum indicator"""
        df = df.copy()
        df['Momentum'] = df['close'] - df['close'].shift(self.momentum_period)
        df['Momentum_MA'] = df['Momentum'].rolling(window=10).mean()
        df['ROC'] = ((df['close'] - df['close'].shift(self.momentum_period)) / 
                     df['close'].shift(self.momentum_period)) * 100
        return df
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        df = df.copy()
        df['EMA_Fast'] = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        df['EMA_Slow'] = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
        df['MACD_Signal'] = df['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        return df
    
    def detect_bollinger_breakout(self, df: pd.DataFrame, symbol: str) -> List[BreakoutSignal]:
        """
        Detect Bollinger Bands breakout patterns
        
        Bullish: Price breaks above upper band with volume
        Bearish: Price breaks below lower band with volume
        """
        signals = []
        df = self.calculate_bollinger_bands(df)
        
        if len(df) < self.bb_period + 1:
            return signals
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Bullish Breakout
        if (latest['close'] > latest['BB_Upper'] and 
            previous['close'] <= previous['BB_Upper']):
            
            strength = min(100, ((latest['close'] - latest['BB_Upper']) / 
                                latest['BB_Upper'] * 100) * 10)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.BOLLINGER_BULLISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'bb_upper': latest['BB_Upper'],
                    'bb_middle': latest['BB_Middle'],
                    'bb_lower': latest['BB_Lower'],
                    'bb_width': latest['BB_Width'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        # Bearish Breakout
        if (latest['close'] < latest['BB_Lower'] and 
            previous['close'] >= previous['BB_Lower']):
            
            strength = min(100, ((latest['BB_Lower'] - latest['close']) / 
                                latest['BB_Lower'] * 100) * 10)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.BOLLINGER_BEARISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'bb_upper': latest['BB_Upper'],
                    'bb_middle': latest['BB_Middle'],
                    'bb_lower': latest['BB_Lower'],
                    'bb_width': latest['BB_Width'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        return signals
    
    def detect_momentum_breakout(self, df: pd.DataFrame, symbol: str) -> List[BreakoutSignal]:
        """
        Detect Momentum breakout patterns
        
        Bullish: Momentum crosses above zero with increasing ROC
        Bearish: Momentum crosses below zero with decreasing ROC
        """
        signals = []
        df = self.calculate_momentum(df)
        
        if len(df) < self.momentum_period + 10:
            return signals
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Bullish Momentum Breakout
        if (latest['Momentum'] > 0 and previous['Momentum'] <= 0 and 
            latest['ROC'] > 0):
            
            strength = min(100, abs(latest['ROC']) * 5)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MOMENTUM_BULLISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'momentum': latest['Momentum'],
                    'momentum_ma': latest['Momentum_MA'],
                    'roc': latest['ROC'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        # Bearish Momentum Breakout
        if (latest['Momentum'] < 0 and previous['Momentum'] >= 0 and 
            latest['ROC'] < 0):
            
            strength = min(100, abs(latest['ROC']) * 5)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MOMENTUM_BEARISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'momentum': latest['Momentum'],
                    'momentum_ma': latest['Momentum_MA'],
                    'roc': latest['ROC'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        return signals
    
    def detect_macd_crossover(self, df: pd.DataFrame, symbol: str) -> List[BreakoutSignal]:
        """
        Detect MACD crossover signals
        
        Bullish: MACD crosses above signal line
        Bearish: MACD crosses below signal line
        """
        signals = []
        df = self.calculate_macd(df)
        
        if len(df) < max(self.macd_slow, self.macd_signal) + 1:
            return signals
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Bullish MACD Crossover
        if (latest['MACD'] > latest['MACD_Signal'] and 
            previous['MACD'] <= previous['MACD_Signal']):
            
            strength = min(100, abs(latest['MACD_Histogram']) * 10)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MACD_BULLISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'macd': latest['MACD'],
                    'macd_signal': latest['MACD_Signal'],
                    'macd_histogram': latest['MACD_Histogram'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        # Bearish MACD Crossover
        if (latest['MACD'] < latest['MACD_Signal'] and 
            previous['MACD'] >= previous['MACD_Signal']):
            
            strength = min(100, abs(latest['MACD_Histogram']) * 10)
            
            signals.append(BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MACD_BEARISH,
                price=latest['close'],
                timestamp=latest.name,
                strength=strength,
                details={
                    'macd': latest['MACD'],
                    'macd_signal': latest['MACD_Signal'],
                    'macd_histogram': latest['MACD_Histogram'],
                    'volume': latest.get('volume', 0)
                }
            ))
        
        return signals
    
    def scan_all_patterns(self, df: pd.DataFrame, symbol: str) -> List[BreakoutSignal]:
        """Scan for all breakout patterns"""
        all_signals = []
        
        all_signals.extend(self.detect_bollinger_breakout(df, symbol))
        all_signals.extend(self.detect_momentum_breakout(df, symbol))
        all_signals.extend(self.detect_macd_crossover(df, symbol))
        
        return all_signals
    
    def filter_by_type(self, signals: List[BreakoutSignal], 
                       breakout_types: List[BreakoutType]) -> List[BreakoutSignal]:
        """Filter signals by breakout type"""
        return [s for s in signals if s.breakout_type in breakout_types]
    
    def filter_by_strength(self, signals: List[BreakoutSignal], 
                          min_strength: float = 50.0) -> List[BreakoutSignal]:
        """Filter signals by minimum strength"""
        return [s for s in signals if s.strength >= min_strength]


def format_breakout_report(signals: List[BreakoutSignal]) -> str:
    """Format breakout signals into a readable report"""
    if not signals:
        return "No breakout signals detected."
    
    report = f"\n{'='*80}\n"
    report += f"F&O BREAKOUT SCANNER RESULTS - {pd.Timestamp.now()}\n"
    report += f"{'='*80}\n\n"
    
    for signal in signals:
        report += f"Symbol: {signal.symbol}\n"
        report += f"Pattern: {signal.breakout_type.value}\n"
        report += f"Price: ₹{signal.price:.2f}\n"
        report += f"Signal Strength: {signal.strength:.2f}%\n"
        report += f"Time: {signal.timestamp}\n"
        report += f"Details: {signal.details}\n"
        report += f"{'-'*80}\n"
    
    return report
