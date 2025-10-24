"""
Stock Scanner service for finding stocks with specific technical patterns
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any

# Handle imports with fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..data.providers.yahoo_finance_provider import YahooFinanceProvider
from ..core.indicators.technical_indicators import TechnicalIndicators
from ..data.stock_lists import get_stock_list

class StockScanner:
    """Scanner for finding stocks matching technical criteria"""
    
    def __init__(self):
        self.data_provider = YahooFinanceProvider()
        
        # Load all stock universes
        print("🔄 Loading stock universes...")
        
        try:
            nifty50 = get_stock_list('NIFTY_50')
            print(f"✅ Nifty 50: {len(nifty50)} stocks")
        except Exception as e:
            print(f"❌ Nifty 50 load failed: {e}")
            nifty50 = []
        
        try:
            midcap150 = get_stock_list('MIDCAP_150')
            print(f"✅ MidCap 150: {len(midcap150)} stocks")
        except Exception as e:
            print(f"❌ MidCap 150 load failed: {e}")
            midcap150 = []
        
        try:
            smallcap150 = get_stock_list('SMALLCAP_150')
            print(f"✅ SmallCap 150: {len(smallcap150)} stocks")
        except Exception as e:
            print(f"❌ SmallCap 150 load failed: {e}")
            smallcap150 = []
        
        # Configure stock universe options
        self.stock_universes = {
            'nifty50': nifty50,
            'midcap150': midcap150,
            'smallcap150': smallcap150,
            'banking': get_stock_list('BANKING')[:15],
            'it': get_stock_list('IT')[:15],
            'pharma': get_stock_list('PHARMA')[:15],
            'auto': get_stock_list('AUTO')[:15],
            'fmcg': get_stock_list('FMCG')[:10],
            'metals': get_stock_list('METALS')[:10]
        }
        
        # Default universe - start with Nifty 50
        self.stock_universe = self.stock_universes['nifty50']
        self.current_universe = 'nifty50'
        
        print(f"🎯 Scanner initialized with {len(self.stock_universe)} stocks (Nifty 50)")
        
    def _get_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Get stock data with error handling"""
        try:
            data = self.data_provider.get_stock_data(symbol, "1d", period)
            return data
        except Exception as e:
            logger.debug(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _calculate_signal_strength(self, value1: float, value2: float) -> str:
        """Calculate signal strength based on difference"""
        diff_pct = abs((value1 - value2) / value2 * 100) if value2 != 0 else 0
        
        if diff_pct > 5:
            return "Strong"
        elif diff_pct > 2:
            return "Medium"
        else:
            return "Weak"
    
    def _calculate_change_percent(self, data: pd.DataFrame) -> float:
        """Calculate daily change percentage"""
        if len(data) < 2:
            return 0
        current = data['Close'].iloc[-1]
        previous = data['Close'].iloc[-2]
        return ((current - previous) / previous * 100)
    
    def _analyze_volume(self, data: pd.DataFrame) -> str:
        """Analyze volume compared to average"""
        if len(data) < 20:
            return "Normal"
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].iloc[-20:].mean()
        
        ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if ratio > 2:
            return "Very High"
        elif ratio > 1.5:
            return "High"
        elif ratio < 0.5:
            return "Low"
        else:
            return "Normal"
    
    def find_golden_crossover(self, lookback_days: int = 5) -> List[Dict]:
        """Find stocks with golden crossover (50 SMA crosses above 200 SMA)"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for Golden Crossover...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 200:
                    continue
                
                indicators = TechnicalIndicators(data)
                sma_50 = indicators.sma(50)
                sma_200 = indicators.sma(200)
                
                if len(sma_50) < lookback_days or len(sma_200) < lookback_days:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Golden crossover: 50 SMA crosses above 200 SMA
                if (sma_50.iloc[-1] > sma_200.iloc[-1] and 
                    sma_50.iloc[-lookback_days] <= sma_200.iloc[-lookback_days]):
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': self._calculate_signal_strength(sma_50.iloc[-1], sma_200.iloc[-1]),
                        'details': f'50SMA: ₹{sma_50.iloc[-1]:.2f} crossed above 200SMA: ₹{sma_200.iloc[-1]:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for golden crossover: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_death_cross(self, lookback_days: int = 5) -> List[Dict]:
        """Find stocks with death cross (50 SMA crosses below 200 SMA)"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for Death Cross...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 200:
                    continue
                
                indicators = TechnicalIndicators(data)
                sma_50 = indicators.sma(50)
                sma_200 = indicators.sma(200)
                
                if len(sma_50) < lookback_days or len(sma_200) < lookback_days:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # Death cross: 50 SMA crosses below 200 SMA
                if (sma_50.iloc[-1] < sma_200.iloc[-1] and 
                    sma_50.iloc[-lookback_days] >= sma_200.iloc[-lookback_days]):
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BEARISH',
                        'strength': self._calculate_signal_strength(sma_50.iloc[-1], sma_200.iloc[-1]),
                        'details': f'50SMA: ₹{sma_50.iloc[-1]:.2f} crossed below 200SMA: ₹{sma_200.iloc[-1]:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for death cross: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'])
    
    def find_volume_breakout(self, volume_threshold: float = 2.0) -> List[Dict]:
        """Find stocks with high volume breakout"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for Volume Breakout...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 20:
                    continue
                
                current_price = data['Close'].iloc[-1]
                current_volume = data['Volume'].iloc[-1]
                avg_volume = data['Volume'].iloc[-20:].mean()
                
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                change_pct = self._calculate_change_percent(data)
                
                # High volume with significant price movement
                if volume_ratio > volume_threshold and abs(change_pct) > 1:
                    signal = 'BULLISH' if change_pct > 0 else 'BEARISH'
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': signal,
                        'strength': 'Strong' if volume_ratio > 3 else 'Medium',
                        'details': f'Volume {volume_ratio:.1f}x average with {change_pct:+.1f}% price move',
                        'change_percent': change_pct,
                        'volume_info': f'{volume_ratio:.1f}x Avg'
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for volume breakout: {e}")
                continue
        
        return sorted(results, key=lambda x: abs(x['change_percent']), reverse=True)
    
    def find_rsi_oversold_recovery(self) -> List[Dict]:
        """Find stocks recovering from RSI oversold levels"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for RSI Oversold Recovery...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 30:
                    continue
                
                indicators = TechnicalIndicators(data)
                rsi = indicators.rsi()
                
                if len(rsi) < 5:
                    continue
                
                current_price = data['Close'].iloc[-1]
                current_rsi = rsi.iloc[-1]
                prev_rsi = rsi.iloc[-3]  # 3 days ago
                
                # RSI was oversold and now recovering
                if prev_rsi < 30 and current_rsi > 35 and current_rsi < 50:
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': 'Medium' if current_rsi < 40 else 'Weak',
                        'details': f'RSI recovering: {prev_rsi:.1f} → {current_rsi:.1f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for RSI recovery: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_rsi_overbought(self) -> List[Dict]:
        """Find stocks with RSI overbought levels"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for RSI Overbought...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 30:
                    continue
                
                indicators = TechnicalIndicators(data)
                rsi = indicators.rsi()
                
                if len(rsi) < 1:
                    continue
                
                current_price = data['Close'].iloc[-1]
                current_rsi = rsi.iloc[-1]
                
                # RSI overbought
                if current_rsi > 70:
                    strength = 'Strong' if current_rsi > 80 else 'Medium'
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BEARISH',
                        'strength': strength,
                        'details': f'RSI overbought: {current_rsi:.1f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for RSI overbought: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_bollinger_breakout(self) -> List[Dict]:
        """Find stocks breaking out of Bollinger Bands"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for Bollinger Breakout...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 30:
                    continue
                
                indicators = TechnicalIndicators(data)
                bb_upper, bb_middle, bb_lower = indicators.bollinger_bands()
                
                if len(bb_upper) < 1:
                    continue
                
                current_price = data['Close'].iloc[-1]
                upper_band = bb_upper.iloc[-1]
                lower_band = bb_lower.iloc[-1]
                
                # Breakout above upper band
                if current_price > upper_band:
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': 'Strong',
                        'details': f'Price ₹{current_price:.2f} broke above upper BB ₹{upper_band:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                # Breakdown below lower band
                elif current_price < lower_band:
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BEARISH',
                        'strength': 'Strong',
                        'details': f'Price ₹{current_price:.2f} broke below lower BB ₹{lower_band:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for BB breakout: {e}")
                continue
        
        return sorted(results, key=lambda x: abs(x['change_percent']), reverse=True)
    
    def find_near_52_week_high(self, threshold_pct: float = 5) -> List[Dict]:
        """Find stocks near 52-week high"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks near 52-week high...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 200:
                    continue
                
                current_price = data['Close'].iloc[-1]
                week_52_high = data['High'].max()
                
                distance_pct = ((week_52_high - current_price) / week_52_high * 100)
                
                if distance_pct <= threshold_pct:
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': 'Strong' if distance_pct < 2 else 'Medium',
                        'details': f'{distance_pct:.1f}% from 52W high ₹{week_52_high:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for 52W high: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_near_52_week_low(self, threshold_pct: float = 5) -> List[Dict]:
        """Find stocks near 52-week low"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks near 52-week low...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 200:
                    continue
                
                current_price = data['Close'].iloc[-1]
                week_52_low = data['Low'].min()
                
                distance_pct = ((current_price - week_52_low) / week_52_low * 100)
                
                if distance_pct <= threshold_pct:
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',  # Near low can be bullish for recovery
                        'strength': 'Strong' if distance_pct < 2 else 'Medium',
                        'details': f'{distance_pct:.1f}% from 52W low ₹{week_52_low:.2f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for 52W low: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_macd_bullish_crossover(self) -> List[Dict]:
        """Find stocks with MACD bullish crossover"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for MACD Bullish Crossover...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 50:
                    continue
                
                indicators = TechnicalIndicators(data)
                macd_line, macd_signal, _ = indicators.macd()
                
                if len(macd_line) < 3 or len(macd_signal) < 3:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # MACD line crosses above signal line
                if (macd_line.iloc[-1] > macd_signal.iloc[-1] and 
                    macd_line.iloc[-2] <= macd_signal.iloc[-2]):
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': 'Medium',
                        'details': f'MACD bullish crossover: {macd_line.iloc[-1]:.3f} > {macd_signal.iloc[-1]:.3f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for MACD bullish: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def find_macd_bearish_crossover(self) -> List[Dict]:
        """Find stocks with MACD bearish crossover"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for MACD Bearish Crossover...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 50:
                    continue
                
                indicators = TechnicalIndicators(data)
                macd_line, macd_signal, _ = indicators.macd()
                
                if len(macd_line) < 3 or len(macd_signal) < 3:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # MACD line crosses below signal line
                if (macd_line.iloc[-1] < macd_signal.iloc[-1] and 
                    macd_line.iloc[-2] >= macd_signal.iloc[-2]):
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BEARISH',
                        'strength': 'Medium',
                        'details': f'MACD bearish crossover: {macd_line.iloc[-1]:.3f} < {macd_signal.iloc[-1]:.3f}',
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for MACD bearish: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'])
    
    def find_momentum_breakout(self) -> List[Dict]:
        """Find stocks with momentum breakout (price + volume)"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks for Momentum Breakout...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 30:
                    continue
                
                current_price = data['Close'].iloc[-1]
                sma_20 = data['Close'].rolling(20).mean().iloc[-1]
                
                change_pct = self._calculate_change_percent(data)
                volume_info = self._analyze_volume(data)
                
                # Momentum: Price above 20 SMA + high volume + positive change
                if (current_price > sma_20 and 
                    change_pct > 2 and 
                    volume_info in ['High', 'Very High']):
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': 'BULLISH',
                        'strength': 'Strong',
                        'details': f'Price above 20SMA ₹{sma_20:.2f} with high volume',
                        'change_percent': change_pct,
                        'volume_info': volume_info
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for momentum: {e}")
                continue
        
        return sorted(results, key=lambda x: x['change_percent'], reverse=True)
    
    def custom_scan(self, criteria: Dict) -> List[Dict]:
        """Custom scan with multiple criteria"""
        results = []
        
        print(f"Scanning {len(self.stock_universe)} stocks with custom criteria...")
        
        for i, symbol in enumerate(self.stock_universe):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.stock_universe)}")
                
            try:
                data = self._get_stock_data(symbol)
                if data is None or len(data) < 50:
                    continue
                
                indicators = TechnicalIndicators(data)
                current_price = data['Close'].iloc[-1]
                matches = []
                
                # Check RSI criteria
                if 'rsi' in criteria:
                    rsi = indicators.rsi()
                    if len(rsi) > 0:
                        current_rsi = rsi.iloc[-1]
                        if criteria['rsi'] == 'oversold' and current_rsi < 30:
                            matches.append(f"RSI oversold: {current_rsi:.1f}")
                        elif criteria['rsi'] == 'overbought' and current_rsi > 70:
                            matches.append(f"RSI overbought: {current_rsi:.1f}")
                        elif criteria['rsi'] == 'neutral' and 40 <= current_rsi <= 60:
                            matches.append(f"RSI neutral: {current_rsi:.1f}")
                
                # Check volume criteria
                if 'volume' in criteria:
                    volume_status = self._analyze_volume(data)
                    if criteria['volume'] == 'high' and volume_status in ['High', 'Very High']:
                        matches.append(f"High volume: {volume_status}")
                    elif criteria['volume'] == 'low' and volume_status == 'Low':
                        matches.append("Low volume")
                    elif criteria['volume'] == 'normal' and volume_status == 'Normal':
                        matches.append("Normal volume")
                
                # Check MACD criteria
                if 'macd' in criteria:
                    macd_line, macd_signal, _ = indicators.macd()
                    if len(macd_line) > 0 and len(macd_signal) > 0:
                        if criteria['macd'] == 'bullish' and macd_line.iloc[-1] > macd_signal.iloc[-1]:
                            matches.append("MACD bullish")
                        elif criteria['macd'] == 'bearish' and macd_line.iloc[-1] < macd_signal.iloc[-1]:
                            matches.append("MACD bearish")
                
                # If all criteria match
                if len(matches) == len(criteria):
                    signal = 'BULLISH' if any('bullish' in m or 'oversold' in m for m in matches) else 'NEUTRAL'
                    
                    results.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': signal,
                        'strength': 'Medium',
                        'details': ', '.join(matches),
                        'change_percent': self._calculate_change_percent(data),
                        'volume_info': self._analyze_volume(data)
                    })
                    
            except Exception as e:
                logger.debug(f"Error in custom scan for {symbol}: {e}")
                continue
        
        return sorted(results, key=lambda x: abs(x['change_percent']), reverse=True)
    
    def set_universe(self, universe_name: str) -> bool:
        """Set the scanning universe"""
        if universe_name in self.stock_universes:
            universe_stocks = self.stock_universes[universe_name]
            if universe_stocks:  # Check if universe has stocks
                self.stock_universe = universe_stocks
                self.current_universe = universe_name
                logger.info(f"Scanning universe changed to {universe_name}: {len(self.stock_universe)} stocks")
                return True
            else:
                logger.warning(f"Universe {universe_name} is empty")
                return False
        else:
            logger.warning(f"Unknown universe: {universe_name}")
            return False
    
    def get_available_universes(self) -> Dict[str, int]:
        """Get available universes with stock counts"""
        universes = {}
        for name, stocks in self.stock_universes.items():
            universes[name] = len(stocks) if stocks else 0
        return universes
    
    def get_current_universe_info(self) -> Dict[str, Any]:
        """Get current universe information"""
        return {
            'name': self.current_universe,
            'stock_count': len(self.stock_universe),
            'sample_stocks': self.stock_universe[:5]  # First 5 as sample
        }
    
    def scan_bulk(self, scan_function, scan_name: str):
        """
        Perform bulk scanning using the specified scan function.
        """
        print(f"🔍 {scan_name} - Bulk scanning {len(self.current_universe)} stocks...")
        
        # Get bulk data for current universe
        bulk_data = self._fetch_bulk_scanner_data(self.current_universe)
        
        print(f"✅ Retrieved data for {len(bulk_data)} stocks. Scanning for patterns...")
        
        results = []
        processed = 0
        
        for symbol, data in bulk_data.items():
            if data is not None and not data.empty:
                try:
                    processed += 1
                    print(f"\r📊 Analyzing patterns... [{processed}/{len(bulk_data)}]", end="", flush=True)
                    
                    # Apply the scan function
                    result = scan_function(data, symbol)
                    if result:
                        results.append(result)
                        
                except Exception as e:
                    logger.debug(f"Error scanning {symbol}: {e}")
        
        print("\r" + " " * 50 + "\r", end="")  # Clear the line
        return results
    
    def _fetch_bulk_scanner_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for scanner in bulk for better performance.
        """
        bulk_data = {}
        batch_size = 25  # Slightly larger batch for scanner
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_progress = f"[{i+1}-{min(i+batch_size, len(symbols))}/{len(symbols)}]"
            print(f"\r🔄 Fetching scanner data {batch_progress}...", end="", flush=True)
            
            try:
                # Try bulk download with yfinance
                try:
                    import yfinance as yf
                    batch_symbols = " ".join(batch)
                    # Get more data for technical analysis
                    data = yf.download(batch_symbols, period="6mo", interval="1d", 
                                     group_by='ticker', progress=False, threads=True,
                                     auto_adjust=False)  # Fix FutureWarning
                    
                    if len(batch) == 1:
                        symbol = batch[0]
                        if not data.empty and len(data) > 50:  # Need enough data for technical indicators
                            bulk_data[symbol] = data
                    else:
                        for symbol in batch:
                            try:
                                if hasattr(data.columns, 'levels') and symbol in data.columns.levels[0]:
                                    stock_data = data[symbol]
                                    if not stock_data.empty and len(stock_data) > 50:
                                        bulk_data[symbol] = stock_data
                            except (KeyError, AttributeError, IndexError):
                                continue
                                
                except ImportError:
                    # Fallback to individual calls
                    for symbol in batch:
                        try:
                            stock_data = self.data_provider.get_stock_data(symbol, period="6mo")
                            if stock_data is not None and not stock_data.empty and len(stock_data) > 50:
                                bulk_data[symbol] = stock_data
                        except Exception:
                            continue
            
            except Exception as e:
                logger.debug(f"Error fetching scanner batch {batch_progress}: {e}")
                # Individual fallback
                for symbol in batch:
                    try:
                        stock_data = self.data_provider.get_stock_data(symbol, period="6mo")
                        if stock_data is not None and not stock_data.empty:
                            bulk_data[symbol] = stock_data
                    except Exception:
                        continue
        
        print("\r" + " " * 50 + "\r", end="")  # Clear progress
        return bulk_data

    # Enhanced scanner functions using bulk processing