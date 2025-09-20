"""
Utility functions for the stock market analysis tool
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def format_currency(amount: float, currency: str = "₹") -> str:
    """Format currency with Indian Rupee symbol"""
    if amount >= 10000000:  # 1 Crore
        return f"{currency}{amount/10000000:.2f}Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"{currency}{amount/100000:.2f}L"
    else:
        return f"{currency}{amount:,.2f}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def is_trading_day(date: datetime) -> bool:
    """Check if given date is a trading day (Monday-Friday, excluding holidays)"""
    # Basic check for weekends
    if date.weekday() > 4:  # Saturday = 5, Sunday = 6
        return False
    
    # TODO: Add Indian market holidays check
    return True

def get_next_trading_day(date: datetime) -> datetime:
    """Get next trading day from given date"""
    next_day = date + timedelta(days=1)
    while not is_trading_day(next_day):
        next_day += timedelta(days=1)
    return next_day

def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """Calculate price volatility (standard deviation of returns)"""
    if len(prices) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    
    if len(returns) < period:
        return np.std(returns) if returns else 0.0
    
    recent_returns = returns[-period:]
    return np.std(recent_returns)

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.06) -> float:
    """Calculate Sharpe ratio for given returns"""
    if not returns:
        return 0.0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
    # Convert annual risk-free rate to appropriate period
    excess_return = mean_return - (risk_free_rate / 252)  # Assuming daily returns
    return excess_return / std_return

def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to standard format"""
    symbol = symbol.upper().strip()
    
    # Add .NS suffix for Indian stocks if not present
    if not symbol.endswith(('.NS', '.BO')):
        symbol += '.NS'
    
    return symbol

def calculate_position_size_kelly(win_rate: float, avg_win: float, avg_loss: float, 
                                 portfolio_value: float) -> float:
    """Calculate position size using Kelly Criterion"""
    if avg_loss <= 0 or win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    # Kelly formula: f = (bp - q) / b
    # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
    b = avg_win / avg_loss
    p = win_rate
    q = 1 - win_rate
    
    kelly_fraction = (b * p - q) / b
    
    # Cap at 25% of portfolio for risk management
    kelly_fraction = min(kelly_fraction, 0.25)
    kelly_fraction = max(kelly_fraction, 0.0)
    
    return portfolio_value * kelly_fraction

def identify_market_regime(prices: List[float], period: int = 50) -> str:
    """Identify current market regime (Bull/Bear/Sideways)"""
    if len(prices) < period:
        return "Unknown"
    
    recent_prices = prices[-period:]
    
    # Calculate trend using linear regression
    x = np.arange(len(recent_prices))
    slope, _ = np.polyfit(x, recent_prices, 1)
    
    # Calculate relative slope
    avg_price = np.mean(recent_prices)
    relative_slope = slope / avg_price
    
    if relative_slope > 0.001:  # 0.1% daily trend
        return "Bull Market"
    elif relative_slope < -0.001:
        return "Bear Market"
    else:
        return "Sideways Market"

def calculate_support_resistance(prices: List[float], window: int = 20) -> Dict[str, float]:
    """Calculate support and resistance levels"""
    if len(prices) < window:
        return {"support": min(prices), "resistance": max(prices)}
    
    recent_prices = prices[-window:]
    
    # Simple approach: use recent min/max
    support = min(recent_prices)
    resistance = max(recent_prices)
    
    return {
        "support": support,
        "resistance": resistance,
        "range_percent": ((resistance - support) / support) * 100
    }

def format_recommendation_table(recommendations: List[Dict[str, Any]]) -> str:
    """Format recommendations as a readable table"""
    if not recommendations:
        return "No recommendations available."
    
    table_rows = []
    table_rows.append("+" + "-" * 80 + "+")
    table_rows.append(f"| {'Symbol':<10} | {'Action':<6} | {'Price':<8} | {'Target':<8} | {'Stop Loss':<8} | {'Confidence':<10} |")
    table_rows.append("+" + "-" * 80 + "+")
    
    for rec in recommendations:
        symbol = rec['symbol'].replace('.NS', '')[:10]
        action = rec['action'][:6]
        price = f"₹{rec['current_price']:.1f}"[:8]
        target = f"₹{rec['target']:.1f}"[:8]
        stop_loss = f"₹{rec['stop_loss']:.1f}"[:8]
        confidence = f"{rec['confidence']:.1f}%"[:10]
        
        table_rows.append(f"| {symbol:<10} | {action:<6} | {price:<8} | {target:<8} | {stop_loss:<8} | {confidence:<10} |")
    
    table_rows.append("+" + "-" * 80 + "+")
    
    return "\n".join(table_rows)

class TimeFrameConverter:
    """Utility class for time frame conversions"""
    
    @staticmethod
    def minutes_to_pandas_freq(minutes: int) -> str:
        """Convert minutes to pandas frequency string"""
        freq_map = {
            1: "1T",
            5: "5T", 
            15: "15T",
            30: "30T",
            60: "1H",
            1440: "1D"  # Daily
        }
        return freq_map.get(minutes, "5T")
    
    @staticmethod
    def get_period_for_timeframe(timeframe: str) -> str:
        """Get appropriate data period for given timeframe"""
        timeframe_periods = {
            "1m": "1d",
            "5m": "5d", 
            "15m": "1mo",
            "30m": "1mo",
            "1h": "2mo",
            "1d": "1y",
            "1wk": "2y"
        }
        return timeframe_periods.get(timeframe, "1mo")
