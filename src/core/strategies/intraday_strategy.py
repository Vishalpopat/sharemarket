"""
Intraday trading strategy implementation
"""
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

from src.core.strategies.base_strategy import BaseStrategy
from src.core.indicators.technical_indicators import TechnicalIndicators

class IntradayStrategy(BaseStrategy):
    """Strategy for intraday trading with 5-minute timeframes"""
    
    def __init__(self):
        super().__init__()
        self.timeframe = "1d"  # Use daily data instead of 5m (not available)
        self.min_confidence = 35  # Lowered threshold
        
    def analyze(self, data: pd.DataFrame, symbol: str) -> Dict:
        """Analyze stock for intraday trading"""
        try:
            indicators = TechnicalIndicators(data)
            current_price = float(data['Close'].iloc[-1])
            
            # Calculate technical indicators
            rsi = indicators.rsi()
            macd_line, macd_signal, _ = indicators.macd()
            sma_20 = indicators.sma(20)
            ema_12 = indicators.ema(12)
            ema_26 = indicators.ema(26)
            bb_upper, bb_middle, bb_lower = indicators.bollinger_bands()
            stoch_k, stoch_d = indicators.stochastic()
            
            # Get the latest values safely
            rsi_current = rsi.iloc[-1] if len(rsi) > 0 else 50
            macd_current = macd_line.iloc[-1] if len(macd_line) > 0 else 0
            macd_signal_current = macd_signal.iloc[-1] if len(macd_signal) > 0 else 0
            macd_prev = macd_line.iloc[-2] if len(macd_line) > 1 else 0
            macd_signal_prev = macd_signal.iloc[-2] if len(macd_signal) > 1 else 0
            sma_20_current = sma_20.iloc[-1] if len(sma_20) > 0 else current_price
            ema_12_current = ema_12.iloc[-1] if len(ema_12) > 0 else current_price
            ema_26_current = ema_26.iloc[-1] if len(ema_26) > 0 else current_price
            bb_upper_current = bb_upper.iloc[-1] if len(bb_upper) > 0 else current_price * 1.02
            bb_middle_current = bb_middle.iloc[-1] if len(bb_middle) > 0 else current_price
            bb_lower_current = bb_lower.iloc[-1] if len(bb_lower) > 0 else current_price * 0.98
            
            # Volume analysis
            avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Calculate confidence and action
            confidence = 0
            signals = []
            
            # RSI signals (30-70 range for intraday)
            if rsi_current < 30:
                confidence += 20
                signals.append("RSI oversold")
            elif rsi_current > 70:
                confidence += 20
                signals.append("RSI overbought")
            elif 40 <= rsi_current <= 60:
                confidence += 10
                signals.append("RSI neutral")
            
            # MACD signals
            if macd_current > macd_signal_current and macd_prev <= macd_signal_prev:
                confidence += 15
                signals.append("MACD bullish crossover")
            elif macd_current < macd_signal_current and macd_prev >= macd_signal_prev:
                confidence += 15
                signals.append("MACD bearish crossover")
            
            # Moving average signals
            if current_price > ema_12_current > ema_26_current:
                confidence += 15
                signals.append("Bullish EMA trend")
            elif current_price < ema_12_current < ema_26_current:
                confidence += 15
                signals.append("Bearish EMA trend")
            
            # Bollinger Bands signals
            if current_price <= bb_lower_current:
                confidence += 12
                signals.append("BB oversold")
            elif current_price >= bb_upper_current:
                confidence += 12
                signals.append("BB overbought")
            
            # Volume confirmation
            if volume_ratio > 1.5:
                confidence += 8
                signals.append("High volume")
            
            # Determine action based on multiple signals
            bullish_signals = any(s in ["RSI oversold", "MACD bullish crossover", "Bullish EMA trend", "BB oversold"] for s in signals)
            bearish_signals = any(s in ["RSI overbought", "MACD bearish crossover", "Bearish EMA trend", "BB overbought"] for s in signals)
            
            if bullish_signals and confidence >= 35:
                action = "BUY"
                # Dynamic target calculation for BUY
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 2
                target_pct = min(max(1.2, volatility * 0.3), 3.5)  # 1.2% to 3.5%
                stop_pct = min(max(0.8, volatility * 0.2), 2.0)   # 0.8% to 2.0%
                
                target = current_price * (1 + target_pct / 100)
                stop_loss = current_price * (1 - stop_pct / 100)
                
            elif bearish_signals and confidence >= 35:
                action = "SELL"
                # Dynamic target calculation for SELL
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 2
                target_pct = min(max(1.2, volatility * 0.3), 3.5)  # 1.2% to 3.5%
                stop_pct = min(max(0.8, volatility * 0.2), 2.0)   # 0.8% to 2.0%
                
                target = current_price * (1 - target_pct / 100)
                stop_loss = current_price * (1 + stop_pct / 100)
                
            else:
                action = "HOLD"
                # For HOLD, show potential levels
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 2
                target_pct = min(max(1.0, volatility * 0.25), 2.5)
                stop_pct = min(max(0.6, volatility * 0.15), 1.5)
                
                if rsi_current < 50:  # Slight bullish bias for HOLD
                    target = current_price * (1 + target_pct / 100)
                    stop_loss = current_price * (1 - stop_pct / 100)
                else:  # Slight bearish bias for HOLD
                    target = current_price * (1 - target_pct / 100)
                    stop_loss = current_price * (1 + stop_pct / 100)
            
            risk_reward = abs(target - current_price) / abs(stop_loss - current_price) if abs(stop_loss - current_price) > 0 else 1
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'current_price': current_price,
                'target': target,
                'stop_loss': stop_loss,
                'risk_reward': risk_reward,
                'reason': f"Intraday: {', '.join(signals[:3])}, Volume: {volume_ratio:.1f}x"
            }
            
        except Exception as e:
            logger.error(f"Error in intraday analysis for {symbol}: {e}")
            return self._default_recommendation(symbol, data)
    
    def _default_recommendation(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Return default recommendation when analysis fails"""
        current_price = float(data['Close'].iloc[-1])
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 20,
            'current_price': current_price,
            'target': current_price * 1.015,  # 1.5% default target
            'stop_loss': current_price * 0.985,  # 1.5% default stop
            'risk_reward': 1.0,
            'reason': 'Default intraday recommendation due to analysis error'
        }
