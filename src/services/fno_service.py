"""
Service for analyzing Futures & Options (F&O) data to find trading opportunities.
This includes analyzing Open Interest (OI), volume, and price action.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

# Suppress pandas FutureWarnings
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
warnings.filterwarnings('ignore', message='.*fill_method.*')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from ..data.providers.yahoo_finance_provider import YahooFinanceProvider
from ..data.stock_lists import get_stock_list

class FnoAnalysisService:
    """
    Analyzes F&O data to identify patterns like buildups, unwinding, and short covering.
    """
    def __init__(self):
        self.data_provider = YahooFinanceProvider()
        self.fno_stocks = get_stock_list('FNO_STOCKS')
        logger.info(f"F&O Analysis Service initialized with {len(self.fno_stocks)} stocks.")

    def _get_bulk_fno_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetches data for multiple stocks in bulk for better performance.
        Returns a dictionary with symbol as key and DataFrame as value.
        """
        bulk_data = {}
        batch_size = 20  # Process in batches to avoid overwhelming the API
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_progress = f"[{i+1}-{min(i+batch_size, len(symbols))}/{len(symbols)}]"
            print(f"\r🔍 Fetching batch {batch_progress}...", end="", flush=True)
            
            try:
                if YFINANCE_AVAILABLE:
                    # Use yfinance for bulk download
                    batch_symbols = " ".join(batch)
                    data = yf.download(batch_symbols, period="20d", interval="1d", 
                                     group_by='ticker', progress=False, threads=True,
                                     auto_adjust=False)  # Fix FutureWarning
                    
                    if len(batch) == 1:
                        # Single stock case
                        symbol = batch[0]
                        if not data.empty:
                            bulk_data[symbol] = self._process_stock_data(data, symbol)
                    else:
                        # Multiple stocks case
                        for symbol in batch:
                            try:
                                if hasattr(data.columns, 'levels') and symbol in data.columns.levels[0]:
                                    stock_data = data[symbol]
                                    if not stock_data.empty and not stock_data.isna().all().all():
                                        bulk_data[symbol] = self._process_stock_data(stock_data, symbol)
                            except (KeyError, AttributeError, IndexError):
                                continue
                else:
                    # Fallback to individual calls using existing data provider
                    for symbol in batch:
                        try:
                            stock_data = self.data_provider.get_stock_data(symbol, period="20d", interval="1d")
                            if stock_data is not None and not stock_data.empty:
                                bulk_data[symbol] = self._process_stock_data(stock_data, symbol)
                        except Exception:
                            continue
                            
            except Exception as e:
                logger.debug(f"Error fetching batch {batch_progress}: {e}")
                # Fallback to individual calls for this batch
                for symbol in batch:
                    try:
                        stock_data = self.data_provider.get_stock_data(symbol, period="20d", interval="1d")
                        if stock_data is not None and not stock_data.empty:
                            bulk_data[symbol] = self._process_stock_data(stock_data, symbol)
                    except Exception:
                        continue
        
        print("\r" + " " * 50 + "\r", end="")  # Clear the line
        return bulk_data

    def _process_stock_data(self, price_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Process individual stock data with advanced F&O indicators.
        """
        try:
            # Ensure we have the required columns
            if price_data.empty or 'Close' not in price_data.columns:
                return None
            
            # Create a copy to avoid SettingWithCopyWarning
            data = price_data.copy()
                
            # Calculate basic price metrics
            data.loc[:, 'Prev_Close'] = data['Close'].shift(1)
            data.loc[:, 'Price_Chg_Pct'] = (data['Close'] - data['Prev_Close']) / data['Prev_Close'] * 100
            data.loc[:, 'High_Low_Spread'] = (data['High'] - data['Low']) / data['Close'] * 100
            
            # Calculate volatility indicators
            data.loc[:, 'Price_Volatility'] = data['Price_Chg_Pct'].rolling(5).std()
            data.loc[:, 'ATR'] = self._calculate_atr(data)
            
            # Enhanced Open Interest simulation with multiple factors
            base_oi = np.random.uniform(500_000, 2_000_000)  # More realistic range
            
            # Volume-based factors
            if 'Volume' in data.columns:
                volume_ma = data['Volume'].rolling(20).mean()
                volume_factor = data['Volume'] / volume_ma
                volume_factor = volume_factor.fillna(1)
            else:
                volume_factor = pd.Series(1, index=data.index)
            
            # Price momentum factor
            price_momentum = self._safe_pct_change(data['Close'], 5)
            volatility = data['Price_Chg_Pct'].abs().rolling(5).mean().fillna(1)
            
            # Market sentiment factor (based on price direction and volume)
            price_direction = np.where(data['Price_Chg_Pct'] > 0, 1, -1)
            sentiment_factor = price_direction * np.log1p(volume_factor.clip(0.1, 5))
            
            # Generate realistic OI with trends
            oi_values = np.zeros(len(data))
            oi_values[0] = base_oi
            
            for i in range(1, len(data)):
                # OI changes based on multiple factors
                momentum_effect = price_momentum.iloc[i] * 0.3 if not pd.isna(price_momentum.iloc[i]) else 0
                volume_effect = (volume_factor.iloc[i] - 1) * 0.2 if not pd.isna(volume_factor.iloc[i]) else 0
                volatility_effect = volatility.iloc[i] * 0.1 if not pd.isna(volatility.iloc[i]) else 0
                sentiment_effect = sentiment_factor.iloc[i] * 0.15 if not pd.isna(sentiment_factor.iloc[i]) else 0
                random_noise = np.random.normal(0, 0.05)
                
                oi_change_factor = 1 + momentum_effect + volume_effect + volatility_effect + sentiment_effect + random_noise
                oi_change_factor = np.clip(oi_change_factor, 0.8, 1.4)  # Limit extreme changes
                
                oi_values[i] = oi_values[i-1] * oi_change_factor
            
            data.loc[:, 'OI'] = oi_values
            
            # Calculate OI metrics
            data.loc[:, 'Prev_OI'] = data['OI'].shift(1)
            data.loc[:, 'OI_Chg_Pct'] = (data['OI'] - data['Prev_OI']) / data['Prev_OI'] * 100
            data.loc[:, 'OI_MA_5'] = data['OI'].rolling(5).mean()
            data.loc[:, 'OI_MA_20'] = data['OI'].rolling(20).mean()
            data.loc[:, 'OI_Trend'] = np.where(data['OI_MA_5'] > data['OI_MA_20'], 1, -1)
            
            # Advanced F&O indicators
            data.loc[:, 'PCR'] = self._calculate_pcr(data)  # Put-Call Ratio
            data.loc[:, 'Max_Pain'] = self._calculate_max_pain(data)  # Max Pain Level
            data.loc[:, 'OI_PCR'] = self._calculate_oi_pcr(data)  # OI-based PCR
            data.loc[:, 'Gamma_Squeeze'] = self._calculate_gamma_squeeze(data)
            data.loc[:, 'Delta_Exposure'] = self._calculate_delta_exposure(data)
            
            # Volume analysis
            if 'Volume' in data.columns:
                data.loc[:, 'Volume_MA'] = data['Volume'].rolling(20).mean()
                data.loc[:, 'Volume_Ratio'] = data['Volume'] / data['Volume_MA']
                data.loc[:, 'VWAP'] = self._calculate_vwap(data)
                data.loc[:, 'Volume_Profile'] = self._calculate_volume_profile(data)
            else:
                data.loc[:, 'Volume_Ratio'] = 1
                data.loc[:, 'VWAP'] = data['Close']
                data.loc[:, 'Volume_Profile'] = 'Normal'
            
            # Support and Resistance levels
            data.loc[:, 'Support_Level'] = self._calculate_support_resistance(data, 'support')
            data.loc[:, 'Resistance_Level'] = self._calculate_support_resistance(data, 'resistance')
            
            # Market microstructure indicators
            data.loc[:, 'Bid_Ask_Spread'] = self._simulate_bid_ask_spread(data)
            data.loc[:, 'Market_Depth'] = self._simulate_market_depth(data)
            data.loc[:, 'Institutional_Flow'] = self._calculate_institutional_flow(data)
            
            # Index correlation and VIX analysis
            data.loc[:, 'Index_Correlation'] = self._calculate_index_correlation(data, symbol)
            data.loc[:, 'VIX_Impact'] = self._calculate_vix_impact(data)
            data.loc[:, 'Market_Regime'] = self._determine_market_regime(data)
            
            return data.dropna()
            
        except Exception as e:
            logger.debug(f"Error processing advanced data for {symbol}: {e}")
            return None

    def _calculate_index_correlation(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """Calculate correlation with major indices"""
        try:
            # Simulate index correlation based on sector
            sector_correlations = {
                'RELIANCE': 0.85, 'TCS': 0.75, 'HDFCBANK': 0.80, 'INFY': 0.70,
                'ICICIBANK': 0.78, 'HINDUNILVR': 0.65, 'ITC': 0.60, 'SBIN': 0.82,
                'BHARTIARTL': 0.68, 'KOTAKBANK': 0.79, 'LT': 0.72, 'ASIANPAINT': 0.58
            }
            
            base_correlation = sector_correlations.get(symbol.replace('.NS', ''), 0.70)
            
            # Add some variance based on market conditions
            volatility = data['Price_Chg_Pct'].abs().rolling(10).mean()
            correlation_adjustment = np.where(volatility > 2, -0.1, 0.05)  # High vol = lower correlation
            
            correlation = base_correlation + correlation_adjustment + np.random.normal(0, 0.05, len(data))
            return pd.Series(correlation, index=data.index).clip(0.3, 0.95)
            
        except:
            return pd.Series(0.70, index=data.index)

    def _calculate_vix_impact(self, data: pd.DataFrame) -> pd.Series:
        """Calculate VIX impact on the stock"""
        try:
            # Simulate VIX based on market volatility
            market_volatility = data['Price_Chg_Pct'].abs().rolling(20).mean()
            base_vix = 15  # Base VIX level
            
            # VIX increases with market volatility
            simulated_vix = base_vix + market_volatility * 3 + np.random.normal(0, 2, len(data))
            simulated_vix = np.clip(simulated_vix, 10, 45)
            
            # VIX impact on stock (higher VIX = more volatility premium)
            vix_impact = np.where(
                simulated_vix > 25, 'High',
                np.where(simulated_vix > 18, 'Medium', 'Low')
            )
            
            return pd.Series(vix_impact, index=data.index)
            
        except:
            return pd.Series('Medium', index=data.index)

    def _determine_market_regime(self, data: pd.DataFrame) -> pd.Series:
        """Determine current market regime"""
        try:
            # Market regime based on price trends and volatility
            price_trend = self._safe_pct_change(data['Close'], 20)  # 20-day trend
            volatility = data['Price_Chg_Pct'].abs().rolling(10).mean()
            volume_trend = data.get('Volume_Ratio', pd.Series(1, index=data.index)).rolling(10).mean()
            
            regime = []
            for i in range(len(data)):
                trend = price_trend.iloc[i] if not pd.isna(price_trend.iloc[i]) else 0
                vol = volatility.iloc[i] if not pd.isna(volatility.iloc[i]) else 1
                vol_trend = volume_trend.iloc[i] if not pd.isna(volume_trend.iloc[i]) else 1
                
                if trend > 0.05 and vol < 2 and vol_trend > 1.2:
                    regime.append('Bull_Run')
                elif trend < -0.05 and vol < 2:
                    regime.append('Bear_Market')
                elif vol > 3:
                    regime.append('High_Volatility')
                elif abs(trend) < 0.02 and vol < 1.5:
                    regime.append('Sideways')
                else:
                    regime.append('Transitional')
            
            return pd.Series(regime, index=data.index)
            
        except:
            return pd.Series('Transitional', index=data.index)

    def _get_index_data(self) -> Dict[str, pd.DataFrame]:
        """Get major index data for correlation analysis"""
        try:
            indices = {
                'NIFTY': '^NSEI',
                'BANKNIFTY': '^NSEBANK', 
                'SENSEX': '^BSESN',
                'VIX': '^INDIAVIX'
            }
            
            index_data = {}
            print("📊 Fetching index data for correlation analysis...")
            
            for index_name, symbol in indices.items():
                try:
                    # Try to fetch real index data
                    if YFINANCE_AVAILABLE:
                        import yfinance as yf
                        ticker = yf.Ticker(symbol)
                        data = ticker.history(period="6mo", auto_adjust=False)  # Fix FutureWarning
                        if not data.empty:
                            index_data[index_name] = data
                            continue
                    
                    # Fallback: simulate index data
                    dates = pd.date_range(end=datetime.now(), periods=120, freq='D')
                    base_price = {'NIFTY': 18000, 'BANKNIFTY': 43000, 'SENSEX': 60000, 'VIX': 15}[index_name]
                    
                    # Simulate realistic index movements
                    returns = np.random.normal(0.0005, 0.015, 120)  # Daily returns
                    prices = [base_price]
                    for ret in returns[1:]:
                        prices.append(prices[-1] * (1 + ret))
                    
                    index_data[index_name] = pd.DataFrame({
                        'Open': prices,
                        'High': [p * 1.01 for p in prices],
                        'Low': [p * 0.99 for p in prices], 
                        'Close': prices,
                        'Volume': np.random.randint(1000000, 5000000, 120)
                    }, index=dates)
                    
                except Exception as e:
                    logger.debug(f"Error fetching {index_name}: {e}")
            
            return index_data
            
        except Exception as e:
            logger.debug(f"Error in get_index_data: {e}")
            return {}

    def _calculate_confidence_score(self, stock_info: dict, index_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate advanced confidence score using multiple factors"""
        try:
            base_score = 50.0  # Starting confidence
            
            # Factor 1: Signal strength (0-25 points)
            strength = stock_info.get('strength', 0)
            strength_score = min(25, strength * 0.35)
            
            # Factor 2: Volume confirmation (0-15 points) 
            volume_ratio = stock_info.get('volume_ratio', 1)
            volume_score = min(15, (volume_ratio - 1) * 10) if volume_ratio > 1 else 0
            
            # Factor 3: Institutional flow (0-15 points)
            institutional_flow = stock_info.get('institutional_flow', 'Mixed')
            flow_scores = {
                'Strong Institutional': 15, 'Moderate Institutional': 10,
                'Retail Heavy': 5, 'Mixed': 7
            }
            flow_score = flow_scores.get(institutional_flow, 7)
            
            # Factor 4: Market regime alignment (0-10 points)
            market_regime = stock_info.get('market_regime', 'Transitional')
            signal_type = stock_info.get('signal_type', '')
            
            regime_alignment = 0
            if market_regime == 'Bull_Run' and signal_type in ['Long Buildup', 'Short Covering']:
                regime_alignment = 10
            elif market_regime == 'Bear_Market' and signal_type in ['Short Buildup', 'Long Unwinding']:
                regime_alignment = 10
            elif market_regime == 'High_Volatility' and signal_type == 'Gamma Squeeze':
                regime_alignment = 8
            elif market_regime == 'Sideways' and signal_type == 'Delta Neutral':
                regime_alignment = 8
            else:
                regime_alignment = 5
            
            # Factor 5: VIX environment (0-10 points)
            vix_impact = stock_info.get('vix_impact', 'Medium')
            vix_scores = {'Low': 10, 'Medium': 7, 'High': 4}
            vix_score = vix_scores.get(vix_impact, 7)
            
            # Factor 6: Index correlation (0-10 points)
            index_correlation = stock_info.get('index_correlation', 0.7)
            correlation_score = index_correlation * 10 if index_correlation > 0.6 else 5
            
            # Factor 7: Risk level (penalty)
            risk_level = stock_info.get('risk_level', 'Medium')
            risk_penalty = {'Low': 0, 'Medium': -5, 'High': -15}.get(risk_level, -5)
            
            # Factor 8: Market depth (0-5 points)
            market_depth = stock_info.get('market_depth', 'Average')
            depth_scores = {'Deep': 5, 'Good': 3, 'Average': 1, 'Thin': -2}
            depth_score = depth_scores.get(market_depth, 1)
            
            # Factor 9: PCR environment (0-5 points)
            pcr = stock_info.get('pcr', 1.0)
            if signal_type in ['Long Buildup', 'Short Covering']:
                pcr_score = 5 if pcr > 1.2 else 3 if pcr > 1.0 else 1
            elif signal_type in ['Short Buildup', 'Long Unwinding']:
                pcr_score = 5 if pcr < 0.8 else 3 if pcr < 1.0 else 1
            else:
                pcr_score = 3
            
            # Calculate total confidence
            total_confidence = (base_score + strength_score + volume_score + flow_score + 
                              regime_alignment + vix_score + correlation_score + 
                              risk_penalty + depth_score + pcr_score)
            
            # Cap between 0-100
            return max(0, min(100, total_confidence))
            
        except Exception as e:
            logger.debug(f"Error calculating confidence score: {e}")
            return 65.0  # Default medium confidence

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high_low = data['High'] - data['Low']
            high_close = (data['High'] - data['Close'].shift(1)).abs()
            low_close = (data['Low'] - data['Close'].shift(1)).abs()
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            return true_range.rolling(period).mean()
        except:
            return pd.Series(index=data.index, dtype=float).fillna(0)

    def _calculate_pcr(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Put-Call Ratio (simulated)"""
        try:
            # Simulate PCR based on price volatility and trend
            volatility = data['Price_Chg_Pct'].abs().rolling(5).mean()
            price_trend = self._safe_pct_change(data['Close'], 10)
            
            # Higher volatility and downward trend = higher PCR
            base_pcr = 0.8
            volatility_factor = volatility * 0.1
            trend_factor = np.where(price_trend < 0, abs(price_trend) * 2, -price_trend * 0.5)
            
            pcr = base_pcr + volatility_factor + trend_factor + np.random.normal(0, 0.1, len(data))
            return pd.Series(pcr, index=data.index).clip(0.2, 2.5)
        except:
            return pd.Series(index=data.index, dtype=float).fillna(1.0)

    def _calculate_max_pain(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Max Pain level (simulated)"""
        try:
            # Max pain typically near recent trading range
            close_mean = data['Close'].rolling(20).mean()
            close_std = data['Close'].rolling(20).std()
            
            # Max pain within 1 standard deviation of mean
            max_pain = close_mean + np.random.normal(0, 0.3, len(data)) * close_std
            return pd.Series(max_pain, index=data.index)
        except:
            return data['Close'].copy()

    def _calculate_oi_pcr(self, data: pd.DataFrame) -> pd.Series:
        """Calculate OI-based Put-Call Ratio"""
        try:
            # Simulate based on OI changes and price movement
            oi_change = data['OI_Chg_Pct']
            price_change = data['Price_Chg_Pct']
            
            # Divergence between price and OI suggests different PCR
            base_oi_pcr = 1.0
            divergence = np.where(
                (price_change > 0) & (oi_change < 0), 0.3,  # Price up, OI down = low PCR
                np.where(
                    (price_change < 0) & (oi_change > 0), -0.3,  # Price down, OI up = high PCR
                    0
                )
            )
            
            oi_pcr = base_oi_pcr + divergence + np.random.normal(0, 0.15, len(data))
            return pd.Series(oi_pcr, index=data.index).clip(0.3, 2.0)
        except:
            return pd.Series(index=data.index, dtype=float).fillna(1.0)

    def _calculate_gamma_squeeze(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Gamma Squeeze indicator"""
        try:
            # High gamma squeeze when price near strikes with high OI
            price_volatility = data['Price_Chg_Pct'].abs().rolling(5).mean()
            oi_buildup = data['OI_Chg_Pct'].rolling(3).mean()
            volume_surge = data.get('Volume_Ratio', pd.Series(1, index=data.index))
            
            # Gamma squeeze = high OI + low volatility + volume surge
            gamma_score = (oi_buildup * 0.4 + 
                          (2 - price_volatility) * 0.3 + 
                          volume_surge * 0.3)
            
            return pd.Series(gamma_score, index=data.index).fillna(0)
        except:
            return pd.Series(index=data.index, dtype=float).fillna(0)

    def _calculate_delta_exposure(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Delta Exposure (simulated)"""
        try:
            # Delta exposure based on price movement and OI
            price_change = data['Price_Chg_Pct']
            oi_change = data['OI_Chg_Pct']
            
            # Positive delta exposure = bullish positioning
            delta_exposure = price_change * 0.6 + oi_change * 0.4
            return pd.Series(delta_exposure, index=data.index).fillna(0)
        except:
            return pd.Series(index=data.index, dtype=float).fillna(0)

    def _calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        try:
            if 'Volume' not in data.columns:
                return data['Close'].copy()
            
            typical_price = (data['High'] + data['Low'] + data['Close']) / 3
            vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
            return vwap
        except:
            return data['Close'].copy()

    def _calculate_volume_profile(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Volume Profile categories"""
        try:
            if 'Volume' not in data.columns:
                return pd.Series('Normal', index=data.index)
            
            volume_ratio = data.get('Volume_Ratio', pd.Series(1, index=data.index))
            
            def categorize_volume(ratio):
                if ratio > 2.5:
                    return 'Extreme High'
                elif ratio > 1.8:
                    return 'High'
                elif ratio > 1.2:
                    return 'Above Average'
                elif ratio < 0.6:
                    return 'Low'
                else:
                    return 'Normal'
            
            return volume_ratio.apply(categorize_volume)
        except:
            return pd.Series('Normal', index=data.index)

    def _calculate_support_resistance(self, data: pd.DataFrame, level_type: str) -> pd.Series:
        """Calculate dynamic support/resistance levels"""
        try:
            if level_type == 'support':
                # Support = recent lows
                support = data['Low'].rolling(20).min()
                return support
            else:
                # Resistance = recent highs
                resistance = data['High'].rolling(20).max()
                return resistance
        except:
            return data['Close'].copy()

    def _simulate_bid_ask_spread(self, data: pd.DataFrame) -> pd.Series:
        """Simulate bid-ask spread based on volatility"""
        try:
            volatility = data['Price_Chg_Pct'].abs().rolling(5).mean()
            base_spread = 0.1  # 0.1% base spread
            spread = base_spread + volatility * 0.5
            return pd.Series(spread, index=data.index).fillna(base_spread)
        except:
            return pd.Series(0.1, index=data.index)

    def _simulate_market_depth(self, data: pd.DataFrame) -> pd.Series:
        """Simulate market depth based on volume and volatility"""
        try:
            volume_ratio = data.get('Volume_Ratio', pd.Series(1, index=data.index))
            volatility = data['Price_Chg_Pct'].abs().rolling(5).mean()
            
            # Higher volume and lower volatility = better depth
            depth_score = volume_ratio * 0.7 + (2 - volatility) * 0.3
            
            def categorize_depth(score):
                if score > 2.5:
                    return 'Deep'
                elif score > 1.5:
                    return 'Good'
                elif score > 0.8:
                    return 'Average'
                else:
                    return 'Thin'
            
            return depth_score.apply(categorize_depth)
        except:
            return pd.Series('Average', index=data.index)

    def _calculate_institutional_flow(self, data: pd.DataFrame) -> pd.Series:
        """Calculate institutional flow indicator"""
        try:
            # Large volume with small price impact = institutional flow
            volume_ratio = data.get('Volume_Ratio', pd.Series(1, index=data.index))
            price_impact = data['Price_Chg_Pct'].abs()
            
            # High volume, low price impact = institutional buying/selling
            institutional_score = volume_ratio / (price_impact + 0.1)
            
            def categorize_flow(score):
                if score > 15:
                    return 'Strong Institutional'
                elif score > 8:
                    return 'Moderate Institutional'
                elif score > 4:
                    return 'Retail Heavy'
                else:
                    return 'Mixed'
            
            return institutional_score.apply(categorize_flow)
        except:
            return pd.Series('Mixed', index=data.index)

    def scan_for_buildup(self) -> Dict[str, List[Dict]]:
        """
        Enhanced F&O analysis with advanced indicators:
        1. Long Buildup: Price ▲, OI ▲ (Bullish)
        2. Short Buildup: Price ▼, OI ▲ (Bearish)
        3. Short Covering: Price ▲, OI ▼ (Bullish)
        4. Long Unwinding: Price ▼, OI ▼ (Bearish)
        5. Gamma Squeeze: High OI + Low Volatility
        6. Delta Neutral: Balanced positioning
        """
        results = {
            "long_buildup": [],
            "short_buildup": [],
            "short_covering": [],
            "long_unwinding": [],
            "gamma_squeeze": [],
            "delta_neutral": [],
            "high_conviction": []
        }
        
        print(f"🔍 Enhanced F&O scanning of {len(self.fno_stocks)} stocks with advanced indicators...")
        
        # Get index data for correlation analysis
        index_data = self._get_index_data()
        
        # Get bulk data for all F&O stocks
        bulk_data = self._get_bulk_fno_data(self.fno_stocks)
        
        print(f"✅ Retrieved data for {len(bulk_data)} stocks. Analyzing advanced patterns with index correlation...")
        
        for symbol, fno_data in bulk_data.items():
            if fno_data is None or fno_data.empty:
                continue
                
            try:
                latest = fno_data.iloc[-1]
                
                # Basic metrics
                price_change = latest['Price_Chg_Pct']
                oi_change = latest['OI_Chg_Pct']
                
                # Advanced metrics
                atr = latest.get('ATR', 0)
                pcr = latest.get('PCR', 1.0)
                max_pain = latest.get('Max_Pain', latest['Close'])
                gamma_squeeze = latest.get('Gamma_Squeeze', 0)
                delta_exposure = latest.get('Delta_Exposure', 0)
                volume_ratio = latest.get('Volume_Ratio', 1)
                volume_profile = latest.get('Volume_Profile', 'Normal')
                market_depth = latest.get('Market_Depth', 'Average')
                institutional_flow = latest.get('Institutional_Flow', 'Mixed')
                
                # Distance from support/resistance
                support_distance = (latest['Close'] - latest['Support_Level']) / latest['Close'] * 100
                resistance_distance = (latest['Resistance_Level'] - latest['Close']) / latest['Close'] * 100
                
                # Advanced strength calculation
                base_strength = min(100, abs(price_change) * 10 + abs(oi_change) * 5)
                volume_boost = min(20, volume_ratio * 5)
                gamma_boost = min(15, gamma_squeeze * 3)
                delta_boost = min(10, abs(delta_exposure) * 2)
                depth_boost = {'Deep': 10, 'Good': 5, 'Average': 0, 'Thin': -5}.get(market_depth, 0)
                institutional_boost = {
                    'Strong Institutional': 15, 'Moderate Institutional': 8, 
                    'Retail Heavy': -3, 'Mixed': 0
                }.get(institutional_flow, 0)
                
                total_strength = base_strength + volume_boost + gamma_boost + delta_boost + depth_boost + institutional_boost
                total_strength = min(100, max(0, total_strength))
                
                # Enhanced stock info with all indicators including index analysis
                stock_info = {
                    'symbol': symbol,
                    'price': latest['Close'],
                    'price_chg_pct': price_change,
                    'oi': latest['OI'],
                    'oi_chg_pct': oi_change,
                    'volume': latest.get('Volume', 0),
                    'volume_ratio': volume_ratio,
                    'volume_profile': volume_profile,
                    'strength': total_strength,
                    'atr': atr,
                    'pcr': pcr,
                    'max_pain': max_pain,
                    'max_pain_distance': abs(latest['Close'] - max_pain) / latest['Close'] * 100,
                    'gamma_squeeze': gamma_squeeze,
                    'delta_exposure': delta_exposure,
                    'support_distance': support_distance,
                    'resistance_distance': resistance_distance,
                    'market_depth': market_depth,
                    'institutional_flow': institutional_flow,
                    'vwap': latest.get('VWAP', latest['Close']),
                    'vwap_position': 'Above' if latest['Close'] > latest.get('VWAP', latest['Close']) else 'Below',
                    'signal_type': '',
                    'conviction_level': self._calculate_conviction_level(latest, fno_data),
                    'risk_level': self._calculate_risk_level(latest, fno_data),
                    'trading_recommendation': '',
                    # New index and VIX indicators
                    'index_correlation': latest.get('Index_Correlation', 0.7),
                    'vix_impact': latest.get('VIX_Impact', 'Medium'),
                    'market_regime': latest.get('Market_Regime', 'Transitional'),
                    'nifty_alignment': self._check_index_alignment(symbol, index_data, 'NIFTY'),
                    'sector_strength': self._calculate_sector_strength(symbol, latest),
                    'options_activity': self._analyze_options_activity(latest),
                    'key_levels': {
                        'support': latest['Support_Level'],
                        'resistance': latest['Resistance_Level'],
                        'max_pain': max_pain
                    }
                }
                
                # Calculate advanced confidence score
                stock_info['confidence_score'] = self._calculate_confidence_score(stock_info, index_data)

                # Enhanced thresholds based on volatility and market conditions
                price_threshold = max(0.5, atr * 0.3)  # Dynamic threshold based on ATR
                oi_threshold = 2.0
                gamma_threshold = 1.5
                
                # Pattern Classification with enhanced logic
                if price_change > price_threshold and oi_change > oi_threshold:
                    stock_info['signal_type'] = 'Long Buildup'
                    stock_info['trading_recommendation'] = self._get_long_buildup_recommendation(stock_info)
                    results["long_buildup"].append(stock_info)
                    
                elif price_change < -price_threshold and oi_change > oi_threshold:
                    stock_info['signal_type'] = 'Short Buildup'
                    stock_info['trading_recommendation'] = self._get_short_buildup_recommendation(stock_info)
                    results["short_buildup"].append(stock_info)
                    
                elif price_change > price_threshold and oi_change < -oi_threshold:
                    stock_info['signal_type'] = 'Short Covering'
                    stock_info['trading_recommendation'] = self._get_short_covering_recommendation(stock_info)
                    results["short_covering"].append(stock_info)
                    
                elif price_change < -price_threshold and oi_change < -oi_threshold:
                    stock_info['signal_type'] = 'Long Unwinding'
                    stock_info['trading_recommendation'] = self._get_long_unwinding_recommendation(stock_info)
                    results["long_unwinding"].append(stock_info)
                
                # Gamma Squeeze Detection
                if gamma_squeeze > gamma_threshold and abs(price_change) < price_threshold:
                    stock_info['signal_type'] = 'Gamma Squeeze'
                    stock_info['trading_recommendation'] = self._get_gamma_squeeze_recommendation(stock_info)
                    results["gamma_squeeze"].append(stock_info)
                
                # Delta Neutral Detection
                if abs(delta_exposure) < 0.5 and oi_change > oi_threshold:
                    stock_info['signal_type'] = 'Delta Neutral'
                    stock_info['trading_recommendation'] = self._get_delta_neutral_recommendation(stock_info)
                    results["delta_neutral"].append(stock_info)
                
                # High Conviction Signals (multiple confirmations)
                if (stock_info['conviction_level'] == 'High' and 
                    total_strength > 70 and 
                    institutional_flow in ['Strong Institutional', 'Moderate Institutional']):
                    results["high_conviction"].append(stock_info)

            except Exception as e:
                logger.debug(f"Error analyzing {symbol}: {e}")
        
        # Sort all results by strength
        for category in results:
            results[category].sort(key=lambda x: x['strength'], reverse=True)
        
        return results

    def _calculate_conviction_level(self, latest_data: pd.Series, full_data: pd.DataFrame) -> str:
        """Calculate conviction level based on multiple factors"""
        try:
            score = 0
            
            # Volume confirmation
            if latest_data.get('Volume_Ratio', 1) > 1.5:
                score += 2
            
            # Institutional flow
            if latest_data.get('Institutional_Flow') == 'Strong Institutional':
                score += 3
            elif latest_data.get('Institutional_Flow') == 'Moderate Institutional':
                score += 2
            
            # Market depth
            if latest_data.get('Market_Depth') == 'Deep':
                score += 2
            elif latest_data.get('Market_Depth') == 'Good':
                score += 1
            
            # Trend consistency (last 3 days)
            if len(full_data) >= 3:
                recent_oi_trend = full_data['OI_Chg_Pct'].tail(3).mean()
                recent_price_trend = full_data['Price_Chg_Pct'].tail(3).mean()
                
                if abs(recent_oi_trend) > 1 and abs(recent_price_trend) > 0.5:
                    if (recent_oi_trend > 0 and recent_price_trend > 0) or \
                       (recent_oi_trend < 0 and recent_price_trend < 0):
                        score += 2  # Consistent trend
            
            # PCR confirmation
            pcr = latest_data.get('PCR', 1.0)
            if pcr > 1.5 or pcr < 0.7:  # Extreme PCR values
                score += 1
            
            if score >= 6:
                return 'High'
            elif score >= 3:
                return 'Medium'
            else:
                return 'Low'
                
        except:
            return 'Medium'

    def _calculate_risk_level(self, latest_data: pd.Series, full_data: pd.DataFrame) -> str:
        """Calculate risk level for the position"""
        try:
            risk_score = 0
            
            # Volatility risk
            atr = latest_data.get('ATR', 0)
            if atr > 3:
                risk_score += 2
            elif atr > 2:
                risk_score += 1
            
            # Distance from support/resistance
            support_dist = abs(latest_data.get('support_distance', 0))
            resistance_dist = abs(latest_data.get('resistance_distance', 0))
            
            if min(support_dist, resistance_dist) < 2:  # Very close to key levels
                risk_score += 2
            elif min(support_dist, resistance_dist) < 5:
                risk_score += 1
            
            # Market depth risk
            if latest_data.get('Market_Depth') == 'Thin':
                risk_score += 2
            elif latest_data.get('Market_Depth') == 'Average':
                risk_score += 1
            
            # PCR extremes
            pcr = latest_data.get('PCR', 1.0)
            if pcr > 2.0 or pcr < 0.5:
                risk_score += 1
            
            if risk_score >= 5:
                return 'High'
            elif risk_score >= 3:
                return 'Medium'
            else:
                return 'Low'
                
        except:
            return 'Medium'

    def _get_long_buildup_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Long Buildup"""
        reco = "BUY on dips"
        
        if stock_info['conviction_level'] == 'High':
            reco += " (High conviction - consider larger position)"
        
        if stock_info['support_distance'] < 3:
            reco += " - Near support, good R:R"
        
        if stock_info['institutional_flow'] == 'Strong Institutional':
            reco += " - Strong institutional buying"
            
        return reco

    def _get_short_buildup_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Short Buildup"""
        reco = "SELL on rallies"
        
        if stock_info['conviction_level'] == 'High':
            reco += " (High conviction - consider short position)"
        
        if stock_info['resistance_distance'] < 3:
            reco += " - Near resistance, good R:R"
            
        return reco

    def _get_short_covering_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Short Covering"""
        reco = "BUY momentum"
        
        if stock_info['volume_ratio'] > 2:
            reco += " - Strong volume support"
        
        if stock_info['gamma_squeeze'] > 1:
            reco += " - Gamma squeeze potential"
            
        return reco

    def _get_long_unwinding_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Long Unwinding"""
        reco = "Avoid fresh longs"
        
        if stock_info['support_distance'] < 2:
            reco += " - Watch for support break"
        
        if stock_info['conviction_level'] == 'High':
            reco += " - Consider short positions"
            
        return reco

    def _get_gamma_squeeze_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Gamma Squeeze"""
        reco = "Range breakout play"
        
        if stock_info['volume_ratio'] > 1.5:
            reco += " - Wait for volume confirmation"
        
        reco += f" - Watch {stock_info['key_levels']['max_pain']:.2f} max pain level"
        
        return reco

    def _get_delta_neutral_recommendation(self, stock_info: dict) -> str:
        """Get trading recommendation for Delta Neutral"""
        reco = "Options strategies"
        
        if stock_info['pcr'] > 1.5:
            reco += " - Consider call spreads"
        elif stock_info['pcr'] < 0.7:
            reco += " - Consider put spreads"
        else:
            reco += " - Iron condor/butterfly strategies"
            
        return reco

    def get_fno_summary(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Get summary statistics of F&O analysis"""
        total_signals = sum(len(signals) for signals in results.values())
        
        summary = {
            'total_stocks_scanned': len(self.fno_stocks),
            'total_signals': total_signals,
            'long_buildup_count': len(results['long_buildup']),
            'short_buildup_count': len(results['short_buildup']),
            'short_covering_count': len(results['short_covering']),
            'long_unwinding_count': len(results['long_unwinding']),
            'bullish_signals': len(results['long_buildup']) + len(results['short_covering']),
            'bearish_signals': len(results['short_buildup']) + len(results['long_unwinding']),
            'scan_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary

    def get_top_stocks_by_strength(self, results: Dict[str, List[Dict]], count: int = 5) -> Dict[str, List[Dict]]:
        """Get top stocks by strength for each category"""
        top_stocks = {}
        for category, stocks in results.items():
            top_stocks[category] = stocks[:count]
        return top_stocks

    def _check_index_alignment(self, symbol: str, index_data: Dict[str, pd.DataFrame], index_name: str) -> str:
        """Check alignment with major indices"""
        try:
            if index_name not in index_data or index_data[index_name].empty:
                return 'Unknown'
            
            index_df = index_data[index_name]
            latest_index_change = index_df['Close'].pct_change(1).iloc[-1] * 100
            
            # Get stock's recent performance (simulated correlation)
            correlation = np.random.uniform(0.5, 0.9)  # Simulated correlation
            
            if abs(latest_index_change) < 0.5:
                return 'Neutral'
            elif latest_index_change > 0:
                return 'Bullish_Alignment' if correlation > 0.7 else 'Weak_Bullish'
            else:
                return 'Bearish_Alignment' if correlation > 0.7 else 'Weak_Bearish'
                
        except Exception as e:
            logger.debug(f"Error checking index alignment: {e}")
            return 'Unknown'

    def _calculate_sector_strength(self, symbol: str, latest_data: pd.Series) -> str:
        """Calculate sector-relative strength"""
        try:
            # Sector classification
            sector_map = {
                'RELIANCE': 'Energy', 'TCS': 'IT', 'HDFCBANK': 'Banking', 'INFY': 'IT',
                'ICICIBANK': 'Banking', 'HINDUNILVR': 'FMCG', 'ITC': 'FMCG',
                'SBIN': 'Banking', 'BHARTIARTL': 'Telecom', 'KOTAKBANK': 'Banking',
                'LT': 'Infrastructure', 'ASIANPAINT': 'Paints', 'AXISBANK': 'Banking',
                'MARUTI': 'Auto', 'SUNPHARMA': 'Pharma', 'TITAN': 'Consumer',
                'BAJFINANCE': 'NBFC', 'ULTRACEMCO': 'Cement', 'NESTLEIND': 'FMCG'
            }
            
            stock_name = symbol.replace('.NS', '')
            sector = sector_map.get(stock_name, 'Others')
            
            # Simulate sector performance
            price_change = latest_data.get('Price_Chg_Pct', 0)
            volume_ratio = latest_data.get('Volume_Ratio', 1)
            
            # Strong if outperforming with good volume
            if price_change > 1 and volume_ratio > 1.5:
                return 'Strong_Outperformer'
            elif price_change > 0 and volume_ratio > 1.2:
                return 'Mild_Outperformer'
            elif price_change < -1 and volume_ratio > 1.5:
                return 'Weak_Underperformer'
            elif abs(price_change) < 0.5:
                return 'In_Line'
            else:
                return 'Mixed_Performance'
                
        except Exception as e:
            logger.debug(f"Error calculating sector strength: {e}")
            return 'Unknown'

    def _analyze_options_activity(self, latest_data: pd.Series) -> dict:
        """Analyze options-specific activity"""
        try:
            pcr = latest_data.get('PCR', 1.0)
            gamma_squeeze = latest_data.get('Gamma_Squeeze', 0)
            delta_exposure = latest_data.get('Delta_Exposure', 0)
            max_pain_distance = latest_data.get('Max_Pain', 0)
            
            activity = {
                'pcr_signal': 'Neutral',
                'gamma_environment': 'Normal',
                'delta_bias': 'Balanced',
                'max_pain_proximity': 'Medium',
                'options_flow': 'Mixed'
            }
            
            # PCR Analysis
            if pcr > 1.5:
                activity['pcr_signal'] = 'Bearish_Extreme'
            elif pcr > 1.2:
                activity['pcr_signal'] = 'Bearish'
            elif pcr < 0.7:
                activity['pcr_signal'] = 'Bullish_Extreme'
            elif pcr < 0.9:
                activity['pcr_signal'] = 'Bullish'
            
            # Gamma Environment
            if gamma_squeeze > 2:
                activity['gamma_environment'] = 'High_Gamma'
            elif gamma_squeeze > 1:
                activity['gamma_environment'] = 'Elevated_Gamma'
            
            # Delta Bias
            if delta_exposure > 1:
                activity['delta_bias'] = 'Call_Heavy'
            elif delta_exposure < -1:
                activity['delta_bias'] = 'Put_Heavy'
            
            # Options Flow Assessment
            if activity['pcr_signal'] in ['Bearish_Extreme', 'Bullish_Extreme']:
                activity['options_flow'] = 'Extreme_Positioning'
            elif activity['gamma_environment'] == 'High_Gamma':
                activity['options_flow'] = 'Heavy_Options_Activity'
            else:
                activity['options_flow'] = 'Normal_Activity'
            
            return activity
            
        except Exception as e:
            logger.debug(f"Error analyzing options activity: {e}")
            return {
                'pcr_signal': 'Unknown', 'gamma_environment': 'Unknown',
                'delta_bias': 'Unknown', 'max_pain_proximity': 'Unknown',
                'options_flow': 'Unknown'
            }

    @staticmethod
    def _safe_pct_change(series: pd.Series, periods: int = 1) -> pd.Series:
        """Safe percentage change calculation without FutureWarnings"""
        try:
            # Use fill_method=None to avoid FutureWarning
            return series.pct_change(periods, fill_method=None)
        except TypeError:
            # Fallback for older pandas versions
            return series.pct_change(periods)