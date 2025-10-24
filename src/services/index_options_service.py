"""
Index Options Analysis Service for Nifty, BankNifty, FinNifty, and other indices
Provides Call/Put recommendations based on market conditions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

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
    logger.warning("yfinance not available. Using fallback data.")

from ..data.stock_lists import FNO_INDICES


class IndexOptionsAnalyzer:
    """Analyzes index options and suggests Call/Put strategies"""
    
    def __init__(self):
        """Initialize the Index Options Analyzer"""
        self.indices = FNO_INDICES
        self.vix_level = 15.0  # Default VIX
        
    def analyze_all_indices(self) -> Dict[str, Any]:
        """Analyze all F&O indices and suggest options strategies"""
        print("📊 Analyzing Index Options for all major indices...")
        
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vix_level': self.vix_level,
            'market_sentiment': 'Neutral',
            'indices_analysis': {}
        }
        
        # Get VIX data
        self.vix_level = self._get_vix_level()
        results['vix_level'] = self.vix_level
        results['market_sentiment'] = self._determine_market_sentiment(self.vix_level)
        
        # Analyze each index
        for index_name, index_info in self.indices.items():
            try:
                analysis = self._analyze_single_index(index_name, index_info)
                if analysis:
                    results['indices_analysis'][index_name] = analysis
            except Exception as e:
                logger.debug(f"Error analyzing {index_name}: {e}")
        
        return results
    
    def _get_vix_level(self) -> float:
        """Get current VIX level (India VIX)"""
        try:
            if YFINANCE_AVAILABLE:
                import yfinance as yf
                vix = yf.Ticker("^INDIAVIX")
                hist = vix.history(period="1d", auto_adjust=False)
                if not hist.empty:
                    return float(hist['Close'].iloc[-1])
        except Exception as e:
            logger.debug(f"Error fetching VIX: {e}")
        
        # Simulate VIX based on typical market conditions
        return np.random.uniform(12, 22)
    
    def _determine_market_sentiment(self, vix: float) -> str:
        """Determine market sentiment based on VIX"""
        if vix < 13:
            return 'Very_Calm'
        elif vix < 16:
            return 'Calm'
        elif vix < 20:
            return 'Normal'
        elif vix < 25:
            return 'Elevated'
        else:
            return 'High_Fear'
    
    def _analyze_single_index(self, index_name: str, index_info: Dict) -> Dict[str, Any]:
        """Analyze a single index and suggest options strategies"""
        # Get index data
        index_data = self._fetch_index_data(index_info['symbol'])
        
        if index_data is None or index_data.empty:
            return None
        
        latest = index_data.iloc[-1]
        current_price = latest['Close']
        
        # Get intraday information if available
        intraday_change = index_data.attrs.get('intraday_change', None)
        intraday_high = index_data.attrs.get('intraday_high', latest['High'])
        intraday_low = index_data.attrs.get('intraday_low', latest['Low'])
        
        # Calculate technical indicators
        analysis = {
            'index_name': index_info['name'],
            'current_level': current_price,
            'lot_size': index_info['lot_size'],
            'expiry_type': index_info['expiry'],
            'price_change': self._calculate_price_change(index_data),
            'intraday_info': {
                'change': intraday_change if intraday_change else latest['Close'] / latest['Open'] - 1,
                'high': intraday_high,
                'low': intraday_low,
                'range_pct': (intraday_high - intraday_low) / latest['Close'] * 100
            },
            'trend': self._determine_trend(index_data),
            'volatility': self._calculate_volatility(index_data),
            'support_resistance': self._calculate_support_resistance(index_data),
            'rsi': self._calculate_rsi(index_data),
            'macd_signal': self._calculate_macd_signal(index_data),
            'price_momentum': self._calculate_momentum_score(index_data),
            'options_recommendation': {},
            'strike_suggestions': {}
        }
        
        # Generate options recommendations
        analysis['options_recommendation'] = self._generate_options_recommendation(analysis)
        analysis['strike_suggestions'] = self._suggest_strike_prices(current_price, analysis)
        
        return analysis
    
    def _calculate_momentum_score(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum scores for different timeframes"""
        try:
            current = data['Close'].iloc[-1]
            
            # Calculate momentum indicators
            momentum = {
                'short_term': 0,  # 1-3 days
                'medium_term': 0,  # 1 week
                'long_term': 0,   # 1 month
                'overall_score': 0
            }
            
            # Short-term momentum (1-3 days)
            if len(data) >= 3:
                ma3 = data['Close'].tail(3).mean()
                momentum['short_term'] = (current / ma3 - 1) * 100
            
            # Medium-term momentum (1 week)
            if len(data) >= 5:
                ma5 = data['Close'].tail(5).mean()
                momentum['medium_term'] = (current / ma5 - 1) * 100
            
            # Long-term momentum (1 month)
            if len(data) >= 20:
                ma20 = data['Close'].tail(20).mean()
                momentum['long_term'] = (current / ma20 - 1) * 100
            
            # Overall score (weighted average)
            momentum['overall_score'] = (
                momentum['short_term'] * 0.5 +
                momentum['medium_term'] * 0.3 +
                momentum['long_term'] * 0.2
            )
            
            return momentum
            
        except Exception as e:
            logger.debug(f"Error calculating momentum: {e}")
            return {'short_term': 0, 'medium_term': 0, 'long_term': 0, 'overall_score': 0}
    
    def _fetch_index_data(self, symbol: str) -> pd.DataFrame:
        """Fetch index historical data with real-time focus"""
        try:
            if YFINANCE_AVAILABLE:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                # Get more recent data for better intraday analysis
                data = ticker.history(period="3mo", interval="1d", auto_adjust=False)
                
                if not data.empty and len(data) > 20:
                    # Add intraday context if available
                    try:
                        intraday = ticker.history(period="1d", interval="5m", auto_adjust=False)
                        if not intraday.empty:
                            # Calculate intraday trend
                            intraday_trend = (intraday['Close'].iloc[-1] - intraday['Open'].iloc[0]) / intraday['Open'].iloc[0] * 100
                            # Store intraday info in the dataframe
                            data.attrs['intraday_change'] = intraday_trend
                            data.attrs['intraday_high'] = intraday['High'].max()
                            data.attrs['intraday_low'] = intraday['Low'].min()
                    except:
                        pass
                    
                    return data
        except Exception as e:
            logger.debug(f"Error fetching data for {symbol}: {e}")
        
        # Simulate index data with realistic negative bias for testing
        return self._simulate_index_data()
    
    def _simulate_index_data(self, negative_bias: bool = True) -> pd.DataFrame:
        """Simulate index data with realistic market conditions"""
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        base_price = 21500  # Nifty approximate level
        
        # Simulate realistic price movement with optional negative bias
        if negative_bias:
            # Simulate a declining market (for testing)
            returns = np.random.normal(-0.0008, 0.015, 60)  # Slight negative bias
            # Make today more negative
            returns[-1] = -0.012  # -1.2% today
        else:
            returns = np.random.normal(0.0005, 0.012, 60)
        
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data = pd.DataFrame({
            'Open': [prices[0]] + [prices[i-1] for i in range(1, len(prices))],
            'High': [p * 1.008 for p in prices],
            'Low': [p * 0.992 for p in prices],
            'Close': prices,
            'Volume': np.random.randint(100000, 500000, 60)
        }, index=dates)
        
        # Add intraday simulation
        data.attrs['intraday_change'] = returns[-1] * 100
        data.attrs['intraday_high'] = prices[-1] * 1.005
        data.attrs['intraday_low'] = prices[-1] * 0.995
        
        return data
    
    def _calculate_price_change(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate price changes over different periods"""
        current = data['Close'].iloc[-1]
        
        return {
            '1D': (current / data['Close'].iloc[-2] - 1) * 100 if len(data) >= 2 else 0,
            '1W': (current / data['Close'].iloc[-5] - 1) * 100 if len(data) >= 5 else 0,
            '1M': (current / data['Close'].iloc[-20] - 1) * 100 if len(data) >= 20 else 0
        }
    
    def _determine_trend(self, data: pd.DataFrame) -> str:
        """Determine the trend of the index"""
        sma_20 = data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else sma_20
        current = data['Close'].iloc[-1]
        
        if current > sma_20 > sma_50:
            return 'Strong_Uptrend'
        elif current > sma_20:
            return 'Uptrend'
        elif current < sma_20 < sma_50:
            return 'Strong_Downtrend'
        elif current < sma_20:
            return 'Downtrend'
        else:
            return 'Sideways'
    
    def _calculate_volatility(self, data: pd.DataFrame) -> float:
        """Calculate annualized volatility"""
        returns = data['Close'].pct_change(fill_method=None).dropna()
        return returns.std() * np.sqrt(252) * 100
    
    def _calculate_support_resistance(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        recent_data = data.tail(20)
        
        return {
            'support': recent_data['Low'].min(),
            'resistance': recent_data['High'].max(),
            'pivot': (recent_data['High'].iloc[-1] + recent_data['Low'].iloc[-1] + recent_data['Close'].iloc[-1]) / 3
        }
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def _calculate_macd_signal(self, data: pd.DataFrame) -> str:
        """Calculate MACD signal"""
        try:
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            if macd.iloc[-1] > signal.iloc[-1]:
                return 'Bullish'
            else:
                return 'Bearish'
        except:
            return 'Neutral'
    
    def _generate_options_recommendation(self, analysis: Dict) -> Dict[str, Any]:
        """Generate options trading recommendations with enhanced accuracy"""
        recommendations = {
            'primary_strategy': '',
            'call_rating': 0,  # 0-100
            'put_rating': 0,   # 0-100
            'strategy_type': '',
            'risk_level': '',
            'conviction': '',
            'reasoning': []
        }
        
        # Scoring based on multiple factors with improved weights
        bullish_score = 0
        bearish_score = 0
        
        # Factor 1: Intraday/Recent Price Action (30 points) - MOST IMPORTANT
        price_chg_1d = analysis['price_change']['1D']
        if price_chg_1d < -1.0:
            bearish_score += 30
            recommendations['reasoning'].append(f"⚠️ Today's sharp decline ({price_chg_1d:+.2f}%)")
        elif price_chg_1d < -0.5:
            bearish_score += 20
            recommendations['reasoning'].append(f"Today negative ({price_chg_1d:+.2f}%)")
        elif price_chg_1d < 0:
            bearish_score += 10
        elif price_chg_1d > 1.0:
            bullish_score += 30
            recommendations['reasoning'].append(f"✅ Today's strong gain ({price_chg_1d:+.2f}%)")
        elif price_chg_1d > 0.5:
            bullish_score += 20
            recommendations['reasoning'].append(f"Today positive ({price_chg_1d:+.2f}%)")
        elif price_chg_1d > 0:
            bullish_score += 10
        
        # Factor 2: Weekly Momentum (20 points)
        price_chg_1w = analysis['price_change']['1W']
        if price_chg_1w > 3:
            bullish_score += 20
            recommendations['reasoning'].append(f"Strong weekly momentum ({price_chg_1w:+.1f}%)")
        elif price_chg_1w > 1:
            bullish_score += 12
        elif price_chg_1w < -3:
            bearish_score += 20
            recommendations['reasoning'].append(f"Weak weekly trend ({price_chg_1w:+.1f}%)")
        elif price_chg_1w < -1:
            bearish_score += 12
        
        # Factor 3: Trend Analysis (15 points)
        trend = analysis['trend']
        if trend == 'Strong_Uptrend':
            bullish_score += 15
            recommendations['reasoning'].append("Strong uptrend in place")
        elif trend == 'Uptrend':
            bullish_score += 10
        elif trend == 'Strong_Downtrend':
            bearish_score += 15
            recommendations['reasoning'].append("Strong downtrend in place")
        elif trend == 'Downtrend':
            bearish_score += 10
        
        # Factor 4: RSI (15 points) - Contrarian + Trend
        rsi = analysis['rsi']
        if rsi < 30:
            # Oversold - bullish reversal potential BUT check if still falling
            if price_chg_1d < -0.5:
                bearish_score += 10  # Still falling
                recommendations['reasoning'].append(f"⚠️ Oversold but still declining (RSI: {rsi:.1f})")
            else:
                bullish_score += 15  # Reversal
                recommendations['reasoning'].append(f"RSI oversold - reversal potential ({rsi:.1f})")
        elif rsi > 70:
            # Overbought - bearish reversal potential
            if price_chg_1d > 0.5:
                bullish_score += 5  # Still rising but overbought
            else:
                bearish_score += 15
                recommendations['reasoning'].append(f"RSI overbought ({rsi:.1f})")
        elif rsi > 55:
            bullish_score += 8
        elif rsi < 45:
            bearish_score += 8
        
        # Factor 5: MACD (10 points)
        macd = analysis['macd_signal']
        if macd == 'Bullish':
            bullish_score += 10
            recommendations['reasoning'].append("MACD bullish")
        elif macd == 'Bearish':
            bearish_score += 10
            recommendations['reasoning'].append("MACD bearish")
        
        # Factor 6: Support/Resistance Position (10 points)
        current = analysis['current_level']
        support = analysis['support_resistance']['support']
        resistance = analysis['support_resistance']['resistance']
        range_size = resistance - support
        
        if range_size > 0:
            position_in_range = (current - support) / range_size
            if position_in_range < 0.3:
                bullish_score += 10
                recommendations['reasoning'].append("Near support level")
            elif position_in_range > 0.7:
                bearish_score += 10
                recommendations['reasoning'].append("Near resistance level")
        
        # Factor 7: Volatility Environment (VIX consideration)
        vix_adjustment = 0
        if self.vix_level > 25:
            # High fear - contrarian bullish BUT only if not crashing
            if price_chg_1d > -1:
                bullish_score += 5
                recommendations['reasoning'].append(f"High VIX ({self.vix_level:.1f}) - fear extreme")
        elif self.vix_level > 20:
            # Elevated volatility
            vix_adjustment = -5  # Reduce conviction
        
        # Apply VIX adjustment
        bullish_score = max(0, bullish_score + vix_adjustment)
        bearish_score = max(0, bearish_score + vix_adjustment)
        
        # Factor 8: Monthly Trend (confirmation)
        price_chg_1m = analysis['price_change']['1M']
        if price_chg_1m > 5:
            bullish_score += 5
        elif price_chg_1m < -5:
            bearish_score += 5
        
        # Calculate final ratings
        recommendations['call_rating'] = min(100, bullish_score)
        recommendations['put_rating'] = min(100, bearish_score)
        
        # Enhanced decision logic with better thresholds
        score_diff = abs(bullish_score - bearish_score)
        
        if bullish_score > bearish_score and score_diff >= 15:
            # Bullish bias
            if bullish_score >= 65 and score_diff >= 25:
                recommendations['primary_strategy'] = 'Buy Call Options (Aggressive)'
                recommendations['conviction'] = 'High'
            elif bullish_score >= 50:
                recommendations['primary_strategy'] = 'Buy Call Options (Moderate)'
                recommendations['conviction'] = 'Medium'
            else:
                recommendations['primary_strategy'] = 'Bullish Bias (Call Spreads)'
                recommendations['conviction'] = 'Low'
            recommendations['strategy_type'] = 'Directional_Bullish'
            
        elif bearish_score > bullish_score and score_diff >= 15:
            # Bearish bias
            if bearish_score >= 65 and score_diff >= 25:
                recommendations['primary_strategy'] = 'Buy Put Options (Aggressive)'
                recommendations['conviction'] = 'High'
            elif bearish_score >= 50:
                recommendations['primary_strategy'] = 'Buy Put Options (Moderate)'
                recommendations['conviction'] = 'Medium'
            else:
                recommendations['primary_strategy'] = 'Bearish Bias (Put Spreads)'
                recommendations['conviction'] = 'Low'
            recommendations['strategy_type'] = 'Directional_Bearish'
            
        else:
            # Neutral/Mixed signals
            if self.vix_level > 22:
                recommendations['primary_strategy'] = 'Sell Options (Premium Collection)'
                recommendations['reasoning'].append("High IV - sell premium")
                recommendations['conviction'] = 'Medium'
            elif score_diff < 10:
                recommendations['primary_strategy'] = 'Neutral (Straddle/Strangle)'
                recommendations['reasoning'].append("Mixed signals - no clear direction")
                recommendations['conviction'] = 'Low'
            else:
                recommendations['primary_strategy'] = 'Wait for Clear Signal'
                recommendations['reasoning'].append("Insufficient conviction")
                recommendations['conviction'] = 'Very Low'
            recommendations['strategy_type'] = 'Non_Directional'
        
        # Enhanced Risk Assessment
        risk_factors = 0
        if analysis['volatility'] > 25:
            risk_factors += 2
        elif analysis['volatility'] > 20:
            risk_factors += 1
        
        if self.vix_level > 22:
            risk_factors += 1
        
        if abs(price_chg_1d) > 1.5:
            risk_factors += 1  # High intraday volatility
        
        if rsi > 75 or rsi < 25:
            risk_factors += 1  # Extreme RSI
        
        if risk_factors >= 4:
            recommendations['risk_level'] = 'Very High'
        elif risk_factors >= 3:
            recommendations['risk_level'] = 'High'
        elif risk_factors >= 2:
            recommendations['risk_level'] = 'Medium'
        else:
            recommendations['risk_level'] = 'Low'
        
        # Add summary reasoning
        if not recommendations['reasoning']:
            recommendations['reasoning'].append("Insufficient signals for clear recommendation")
        
        return recommendations
    
    def _suggest_strike_prices(self, current_price: float, analysis: Dict) -> Dict[str, Any]:
        """Suggest strike prices for options trading"""
        round_base = 50 if current_price < 20000 else 100
        atm_strike = round(current_price / round_base) * round_base
        
        strikes = {
            'ATM': atm_strike,
            'CALL_OTM': [],
            'CALL_ITM': [],
            'PUT_OTM': [],
            'PUT_ITM': []
        }
        
        # Generate OTM and ITM strikes
        for i in range(1, 4):
            strikes['CALL_OTM'].append(atm_strike + (i * round_base))
            strikes['CALL_ITM'].append(atm_strike - (i * round_base))
            strikes['PUT_OTM'].append(atm_strike - (i * round_base))
            strikes['PUT_ITM'].append(atm_strike + (i * round_base))
        
        # Add recommendations based on analysis
        recommendation = analysis['options_recommendation']
        
        if recommendation['primary_strategy'] == 'Buy Call Options':
            strikes['recommended_calls'] = [
                {'strike': strikes['CALL_OTM'][0], 'type': 'Slightly OTM', 'confidence': 'High'},
                {'strike': atm_strike, 'type': 'ATM', 'confidence': 'Medium'}
            ]
        elif recommendation['primary_strategy'] == 'Buy Put Options':
            strikes['recommended_puts'] = [
                {'strike': strikes['PUT_OTM'][0], 'type': 'Slightly OTM', 'confidence': 'High'},
                {'strike': atm_strike, 'type': 'ATM', 'confidence': 'Medium'}
            ]
        
        return strikes