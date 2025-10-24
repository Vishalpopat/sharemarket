"""
Configuration settings for the Stock Market Analysis Tool
"""

import os
from typing import Dict, Any

# Try to import python-dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

class Settings:
    """Application settings and configuration"""
    
    def __init__(self):
        """Initialize settings"""
        self.load_settings()
    
    def load_settings(self):
        """Load settings from environment or defaults"""
        # Market settings
        self.market_timezone = "Asia/Kolkata"
        self.market_currency = "INR"
        
        # Trading settings
        self.default_risk_ratio = 2.0  # Risk-reward ratio
        self.max_position_size = 0.05  # 5% of portfolio
        self.min_confidence_threshold = 60.0
        
        # Data settings
        self.data_provider = "yahoo"
        self.cache_duration = 300  # 5 minutes in seconds
        
        # API settings
        self.yahoo_timeout = 30
        self.max_retries = 3
        self.auto_adjust = False  # Control yfinance auto_adjust behavior
        
        # F&O Analysis settings
        self.fno_batch_size = 20
        self.fno_confidence_threshold = 65.0
        self.vix_thresholds = {'low': 18, 'high': 25}  # VIX level thresholds
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_rotation = "1 day"
        self.log_retention = "30 days"
        
        # UI settings
        self.display_currency_symbol = "₹"
        self.decimal_places = 2
        
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return getattr(self, key, default)
    
    def update_setting(self, key: str, value: Any):
        """Update a setting value"""
        setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
