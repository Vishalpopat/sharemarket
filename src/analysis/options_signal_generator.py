import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta

class OptionsSignalGenerator:
    """Generate Call/Put signals based on technical analysis"""
    
    def __init__(self, symbol="^NSEI"):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_data(self, period="1mo"):
        """Fetch historical data"""
        data = self.ticker.history(period=period, interval="15m")
        return data
    
    def calculate_indicators(self, data):
        """Calculate technical indicators"""
        # RSI
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        
        # MACD
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        data['MACD_Diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(data['Close'])
        data['BB_High'] = bollinger.bollinger_hband()
        data['BB_Low'] = bollinger.bollinger_lband()
        data['BB_Mid'] = bollinger.bollinger_mavg()
        
        # Moving Averages
        data['EMA_9'] = ta.trend.EMAIndicator(data['Close'], window=9).ema_indicator()
        data['EMA_21'] = ta.trend.EMAIndicator(data['Close'], window=21).ema_indicator()
        data['SMA_50'] = ta.trend.SMAIndicator(data['Close'], window=50).sma_indicator()
        
        # Stochastic
        stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
        data['Stoch_K'] = stoch.stoch()
        data['Stoch_D'] = stoch.stoch_signal()
        
        # ATR for volatility
        data['ATR'] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
        
        return data
    
    def generate_signal(self):
        """Generate Call/Put signal with reasoning"""
        try:
            data = self.get_data(period="5d")
            if len(data) < 50:
                return {"error": "Insufficient data"}
            
            data = self.calculate_indicators(data)
            current = data.iloc[-1]
            prev = data.iloc[-2]
            
            signals = []
            confidence = 0
            signal_type = "NEUTRAL"
            
            # === BULLISH SIGNALS (BUY CALL) ===
            bullish_score = 0
            bullish_reasons = []
            
            # 1. RSI Oversold Reversal
            if current['RSI'] < 30 and current['RSI'] > prev['RSI']:
                bullish_score += 20
                bullish_reasons.append(f"RSI oversold reversal ({current['RSI']:.1f})")
            elif 30 < current['RSI'] < 50 and current['RSI'] > prev['RSI']:
                bullish_score += 10
                bullish_reasons.append(f"RSI bullish ({current['RSI']:.1f})")
            
            # 2. MACD Crossover
            if current['MACD'] > current['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                bullish_score += 25
                bullish_reasons.append("MACD bullish crossover")
            elif current['MACD'] > current['MACD_Signal']:
                bullish_score += 10
                bullish_reasons.append("MACD above signal")
            
            # 3. Price above EMAs
            if current['Close'] > current['EMA_9'] > current['EMA_21']:
                bullish_score += 15
                bullish_reasons.append("Price above EMAs (trending up)")
            
            # 4. Bollinger Bands
            if current['Close'] < current['BB_Low'] and current['Close'] > prev['Close']:
                bullish_score += 20
                bullish_reasons.append("Bounce from lower Bollinger Band")
            
            # 5. Stochastic
            if current['Stoch_K'] < 20 and current['Stoch_K'] > prev['Stoch_K']:
                bullish_score += 15
                bullish_reasons.append("Stochastic oversold reversal")
            
            # === BEARISH SIGNALS (BUY PUT) ===
            bearish_score = 0
            bearish_reasons = []
            
            # 1. RSI Overbought Reversal
            if current['RSI'] > 70 and current['RSI'] < prev['RSI']:
                bearish_score += 20
                bearish_reasons.append(f"RSI overbought reversal ({current['RSI']:.1f})")
            elif 50 < current['RSI'] < 70 and current['RSI'] < prev['RSI']:
                bearish_score += 10
                bearish_reasons.append(f"RSI bearish ({current['RSI']:.1f})")
            
            # 2. MACD Crossover
            if current['MACD'] < current['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                bearish_score += 25
                bearish_reasons.append("MACD bearish crossover")
            elif current['MACD'] < current['MACD_Signal']:
                bearish_score += 10
                bearish_reasons.append("MACD below signal")
            
            # 3. Price below EMAs
            if current['Close'] < current['EMA_9'] < current['EMA_21']:
                bearish_score += 15
                bearish_reasons.append("Price below EMAs (trending down)")
            
            # 4. Bollinger Bands
            if current['Close'] > current['BB_High'] and current['Close'] < prev['Close']:
                bearish_score += 20
                bearish_reasons.append("Rejection from upper Bollinger Band")
            
            # 5. Stochastic
            if current['Stoch_K'] > 80 and current['Stoch_K'] < prev['Stoch_K']:
                bearish_score += 15
                bearish_reasons.append("Stochastic overbought reversal")
            
            # === DETERMINE SIGNAL ===
            if bullish_score > bearish_score and bullish_score >= 40:
                signal_type = "BUY CALL"
                confidence = min(bullish_score, 100)
                reasons = bullish_reasons
            elif bearish_score > bullish_score and bearish_score >= 40:
                signal_type = "BUY PUT"
                confidence = min(bearish_score, 100)
                reasons = bearish_reasons
            else:
                signal_type = "NEUTRAL"
                confidence = 0
                reasons = ["No strong signal - wait for better setup"]
            
            # Calculate target and stop loss
            atr = current['ATR']
            current_price = current['Close']
            
            if signal_type == "BUY CALL":
                target = current_price + (2 * atr)
                stop_loss = current_price - atr
            elif signal_type == "BUY PUT":
                target = current_price - (2 * atr)
                stop_loss = current_price + atr
            else:
                target = current_price
                stop_loss = current_price
            
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": self.symbol,
                "current_price": float(current_price),
                "signal": signal_type,
                "confidence": confidence,
                "reasons": reasons,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "target": float(target),
                "stop_loss": float(stop_loss),
                "risk_reward": abs((target - current_price) / (current_price - stop_loss)) if signal_type != "NEUTRAL" else 0,
                "indicators": {
                    "RSI": float(current['RSI']),
                    "MACD": float(current['MACD']),
                    "MACD_Signal": float(current['MACD_Signal']),
                    "Stoch_K": float(current['Stoch_K']),
                    "EMA_9": float(current['EMA_9']),
                    "EMA_21": float(current['EMA_21']),
                    "ATR": float(current['ATR'])
                }
            }
        
        except Exception as e:
            return {"error": str(e)}


def get_nifty_signal():
    """Get Nifty options signal"""
    generator = OptionsSignalGenerator("^NSEI")
    return generator.generate_signal()


def get_banknifty_signal():
    """Get Bank Nifty options signal"""
    generator = OptionsSignalGenerator("^NSEBANK")
    return generator.generate_signal()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OPTIONS TRADING SIGNAL GENERATOR")
    print("="*60)
    
    # Nifty Signal
    print("\n📊 NIFTY 50 SIGNAL:")
    nifty_signal = get_nifty_signal()
    
    if "error" in nifty_signal:
        print(f"Error: {nifty_signal['error']}")
    else:
        print(f"\nTime: {nifty_signal['timestamp']}")
        print(f"Current Price: {nifty_signal['current_price']:.2f}")
        print(f"\n🎯 SIGNAL: {nifty_signal['signal']}")
        print(f"Confidence: {nifty_signal['confidence']}%")
        print(f"\nReasons:")
        for reason in nifty_signal['reasons']:
            print(f"  ✓ {reason}")
        
        if nifty_signal['signal'] != "NEUTRAL":
            print(f"\nTarget: {nifty_signal['target']:.2f}")
            print(f"Stop Loss: {nifty_signal['stop_loss']:.2f}")
            print(f"Risk:Reward = 1:{nifty_signal['risk_reward']:.2f}")
        
        print(f"\nKey Indicators:")
        print(f"  RSI: {nifty_signal['indicators']['RSI']:.1f}")
        print(f"  MACD: {nifty_signal['indicators']['MACD']:.2f}")
        print(f"  Stochastic: {nifty_signal['indicators']['Stoch_K']:.1f}")
    
    print("\n" + "="*60)
    
    # Bank Nifty Signal
    print("\n📊 BANK NIFTY SIGNAL:")
    bn_signal = get_banknifty_signal()
    
    if "error" in bn_signal:
        print(f"Error: {bn_signal['error']}")
    else:
        print(f"\nTime: {bn_signal['timestamp']}")
        print(f"Current Price: {bn_signal['current_price']:.2f}")
        print(f"\n🎯 SIGNAL: {bn_signal['signal']}")
        print(f"Confidence: {bn_signal['confidence']}%")
        print(f"\nReasons:")
        for reason in bn_signal['reasons']:
            print(f"  ✓ {reason}")
        
        if bn_signal['signal'] != "NEUTRAL":
            print(f"\nTarget: {bn_signal['target']:.2f}")
            print(f"Stop Loss: {bn_signal['stop_loss']:.2f}")
            print(f"Risk:Reward = 1:{bn_signal['risk_reward']:.2f}")
    
    print("\n" + "="*60)
    print("\n⚠️ DISCLAIMER: For educational purposes only. Not financial advice.")
    print("="*60 + "\n")
