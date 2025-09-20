"""
Swing trading strategy implementation
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

class SwingTradingStrategy(BaseStrategy):
    """Strategy for swing trading with daily timeframes"""
    
    def __init__(self):
        super().__init__()
        self.timeframe = "1d"
        self.min_confidence = 40  # Lowered threshold
        
    def analyze(self, data: pd.DataFrame, symbol: str) -> Dict:
        """Analyze stock for swing trading"""
        try:
            indicators = TechnicalIndicators(data)
            current_price = float(data['Close'].iloc[-1])
            
            # Calculate technical indicators
            rsi = indicators.rsi()
            macd_line, macd_signal, _ = indicators.macd()
            sma_50 = indicators.sma(50)
            sma_200 = indicators.sma(200)
            ema_20 = indicators.ema(20)
            bb_upper, bb_middle, bb_lower = indicators.bollinger_bands()
            stoch_k, stoch_d = indicators.stochastic()
            
            # Get the latest values safely
            rsi_current = rsi.iloc[-1] if len(rsi) > 0 else 50
            macd_current = macd_line.iloc[-1] if len(macd_line) > 0 else 0
            macd_signal_current = macd_signal.iloc[-1] if len(macd_signal) > 0 else 0
            macd_prev = macd_line.iloc[-2] if len(macd_line) > 1 else 0
            macd_signal_prev = macd_signal.iloc[-2] if len(macd_signal) > 1 else 0
            sma_50_current = sma_50.iloc[-1] if len(sma_50) > 0 else current_price
            sma_200_current = sma_200.iloc[-1] if len(sma_200) > 0 else current_price
            ema_20_current = ema_20.iloc[-1] if len(ema_20) > 0 else current_price
            bb_upper_current = bb_upper.iloc[-1] if len(bb_upper) > 0 else current_price * 1.02
            bb_middle_current = bb_middle.iloc[-1] if len(bb_middle) > 0 else current_price
            bb_lower_current = bb_lower.iloc[-1] if len(bb_lower) > 0 else current_price * 0.98
            
            # Volume analysis
            avg_volume = data['Volume'].rolling(50).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Price momentum
            price_change_5d = (current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100 if len(data) > 5 else 0
            price_change_20d = (current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21] * 100 if len(data) > 20 else 0
            
            # Calculate confidence and action
            confidence = 0
            signals = []
            
            # RSI signals (25-75 range for swing)
            if rsi_current < 25:
                confidence += 25
                signals.append("RSI deeply oversold")
            elif rsi_current < 35:
                confidence += 18
                signals.append("RSI oversold")
            elif rsi_current > 75:
                confidence += 25
                signals.append("RSI deeply overbought")
            elif rsi_current > 65:
                confidence += 18
                signals.append("RSI overbought")
            elif 45 <= rsi_current <= 55:
                confidence += 8
                signals.append("RSI neutral")
            
            # MACD signals
            if macd_current > macd_signal_current and macd_prev <= macd_signal_prev:
                confidence += 20
                signals.append("MACD bullish crossover")
            elif macd_current < macd_signal_current and macd_prev >= macd_signal_prev:
                confidence += 20
                signals.append("MACD bearish crossover")
            elif macd_current > macd_signal_current:
                confidence += 10
                signals.append("MACD bullish")
            
            # Moving average signals
            if current_price > sma_50_current > sma_200_current:
                confidence += 20
                signals.append("Strong uptrend")
            elif current_price < sma_50_current < sma_200_current:
                confidence += 20
                signals.append("Strong downtrend")
            elif current_price > ema_20_current:
                confidence += 10
                signals.append("Above EMA20")
            
            # Bollinger Bands signals
            if current_price <= bb_lower_current:
                confidence += 15
                signals.append("BB oversold")
            elif current_price >= bb_upper_current:
                confidence += 15
                signals.append("BB overbought")
            
            # Volume and momentum
            if volume_ratio > 1.2 and price_change_5d > 2:
                confidence += 12
                signals.append("Volume breakout")
            elif volume_ratio > 1.2 and price_change_5d < -2:
                confidence += 12
                signals.append("Volume breakdown")
            
            # Price momentum signals
            if price_change_20d > 5:
                confidence += 8
                signals.append("Strong momentum")
            elif price_change_20d < -5:
                confidence += 8
                signals.append("Weak momentum")
            
            # Determine action based on multiple signals
            bullish_signals = ["RSI oversold", "RSI deeply oversold", "MACD bullish crossover", "Strong uptrend", "BB oversold", "Volume breakout"]
            bearish_signals = ["RSI overbought", "RSI deeply overbought", "MACD bearish crossover", "Strong downtrend", "BB overbought", "Volume breakdown"]
            
            bull_count = sum(1 for s in signals if any(bs in s for bs in bullish_signals))
            bear_count = sum(1 for s in signals if any(bs in s for bs in bearish_signals))
            
            if bull_count >= 2 and confidence >= 40:
                action = "BUY"
                # Dynamic target calculation for swing BUY
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 3
                momentum_factor = max(1, abs(price_change_20d) / 10)
                
                target_pct = min(max(2.5, volatility * 0.8 * momentum_factor), 8.0)  # 2.5% to 8%
                stop_pct = min(max(1.5, volatility * 0.4), 4.0)   # 1.5% to 4%
                
                target = current_price * (1 + target_pct / 100)
                stop_loss = current_price * (1 - stop_pct / 100)
                
            elif bear_count >= 2 and confidence >= 40:
                action = "SELL"
                # Dynamic target calculation for swing SELL
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 3
                momentum_factor = max(1, abs(price_change_20d) / 10)
                
                target_pct = min(max(2.5, volatility * 0.8 * momentum_factor), 8.0)  # 2.5% to 8%
                stop_pct = min(max(1.5, volatility * 0.4), 4.0)   # 1.5% to 4%
                
                target = current_price * (1 - target_pct / 100)
                stop_loss = current_price * (1 + stop_pct / 100)
                
            else:
                action = "HOLD"
                # For HOLD, show potential levels based on trend
                volatility = (bb_upper_current - bb_lower_current) / bb_middle_current * 100 if bb_middle_current > 0 else 3
                target_pct = min(max(2.0, volatility * 0.5), 5.0)
                stop_pct = min(max(1.2, volatility * 0.3), 3.0)
                
                if price_change_20d > 0 or rsi_current < 50:  # Slight bullish bias for HOLD
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
                'reason': f"Swing: {', '.join(signals[:3])}, 20D: {price_change_20d:+.1f}%"
            }
            
        except Exception as e:
            logger.error(f"Error in swing analysis for {symbol}: {e}")
            return self._default_recommendation(symbol, data)
    
    def _default_recommendation(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Return default recommendation when analysis fails"""
        current_price = float(data['Close'].iloc[-1])
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 25,
            'current_price': current_price,
            'target': current_price * 1.03,  # 3% default target
            'stop_loss': current_price * 0.97,  # 3% default stop
            'risk_reward': 1.0,
            'reason': 'Default swing recommendation due to analysis error'
        }
