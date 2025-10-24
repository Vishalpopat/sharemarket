"""
Utility functions for handling pandas and yfinance warnings
"""
import warnings
import pandas as pd
import numpy as np
from typing import Optional, Any

def suppress_future_warnings():
    """Suppress common FutureWarnings from pandas and yfinance"""
    # Suppress pandas FutureWarnings
    warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
    warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
    warnings.filterwarnings('ignore', message='.*fill_method.*')
    warnings.filterwarnings('ignore', message='.*auto_adjust.*')

def safe_pct_change(series: pd.Series, periods: int = 1, fill_method: Optional[str] = None) -> pd.Series:
    """
    Safe percentage change calculation that handles both old and new pandas versions
    """
    try:
        # For newer pandas versions, explicitly set fill_method
        if hasattr(pd.Series.pct_change, '__code__') and 'fill_method' in pd.Series.pct_change.__code__.co_varnames:
            return series.pct_change(periods, fill_method=fill_method)
        else:
            # For older versions, use default behavior
            return series.pct_change(periods)
    except Exception as e:
        # Fallback calculation
        shifted = series.shift(periods)
        return (series - shifted) / shifted

def safe_yf_download(*args, **kwargs) -> pd.DataFrame:
    """
    Safe yfinance download with proper parameter handling
    """
    try:
        import yfinance as yf
        
        # Set auto_adjust explicitly to avoid FutureWarning
        if 'auto_adjust' not in kwargs:
            kwargs['auto_adjust'] = False
            
        # Set progress to False by default
        if 'progress' not in kwargs:
            kwargs['progress'] = False
            
        return yf.download(*args, **kwargs)
    except ImportError:
        # Return empty DataFrame if yfinance not available
        return pd.DataFrame()
    except Exception as e:
        print(f"Warning: yfinance download failed: {e}")
        return pd.DataFrame()

# Apply warning suppression when module is imported
suppress_future_warnings()