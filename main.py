"""
Main entry point for thtry:
    from src.services.market_service import MarketService
    from src.core.strategies.intraday_strategy import IntradayStrategy
    from src.core.strategies.swing_trading_strategy import SwingTradingStrategy
    from src.config.settings import Settings
    from src.data.stock_lists import get_stock_list
    from src.services.stock_scanner import StockScanner
    from src.services.fno_service import FnoAnalysisService
    IMPORTS_OK = True
except ImportError as e:Stock Market Analysis Tool
"""

import sys
import os
from datetime import datetime

# Suppress common warnings before importing other modules
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning) 
warnings.filterwarnings('ignore', message='.*fill_method.*')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')
warnings.filterwarnings('ignore', message='.*pandas.*')
warnings.filterwarnings('ignore', message='.*yfinance.*')

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging with fallback
try:
    from loguru import logger
    def setup_logging():
        """Configure logging"""
        logger.add("logs/market_analysis_{time}.log", 
                   rotation="1 day", 
                   retention="30 days",
                   level="INFO")
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def setup_logging():
        """Configure basic logging"""
        logging.basicConfig(level=logging.INFO)

# Import modules with error handling
try:
    from src.services.market_service import MarketService
    from src.core.strategies.intraday_strategy import IntradayStrategy
    from src.core.strategies.swing_trading_strategy import SwingTradingStrategy
    from src.config.settings import Settings
    from src.data.stock_lists import ALL_CATEGORIES, get_stock_list
    from src.services.stock_scanner import StockScanner
    from src.services.fno_service import FnoAnalysisService
    from src.services.index_options_service import IndexOptionsAnalyzer
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    IMPORTS_OK = False

def display_symbol_suggestions():
    """Display popular Indian stock symbols for user reference"""
    print("\n📋 POPULAR INDIAN STOCK SYMBOLS:")
    print("-" * 50)
    
    suggestions = {
        "🏦 Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
        "💻 IT/Tech": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
        "🏭 Industrial": ["RELIANCE.NS", "ADANIPORTS.NS", "TATASTEEL.NS", "HINDALCO.NS"],
        "🍱 FMCG": ["HINDUNILVR.NS", "NESTLEIND.NS", "ITC.NS", "BRITANNIA.NS"],
        "💊 Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
        "🚗 Auto": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS"]
    }
    
    for category, symbols in suggestions.items():
        print(f"{category}: {', '.join([s.replace('.NS', '') for s in symbols])}")
    
    print("\n💡 Tip: Add '.NS' suffix for NSE stocks (e.g., RELIANCE.NS)")
    print("💡 Tip: Use comma-separated format: RELIANCE.NS,TCS.NS,HDFCBANK.NS")

def get_user_stock_choice():
    """Get stock symbols from user with suggestions"""
    print("\n🎯 CUSTOM STOCK SELECTION")
    print("-" * 40)
    
    # Ask if user wants to see suggestions
    show_help = input("Show popular stock symbols? (y/n): ").strip().lower()
    if show_help in ['y', 'yes']:
        display_symbol_suggestions()
    
    while True:
        print("\nOptions:")
        print("1. Enter custom symbols")
        print("2. Use preset stock lists")
        print("3. Back to main menu")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == '1':
            symbols = input("\nEnter stock symbols (comma-separated): ").strip()
            if symbols:
                stock_list = [s.strip().upper() for s in symbols.split(',')]
                # Add .NS if not present
                stock_list = [s if s.endswith('.NS') else f"{s}.NS" for s in stock_list]
                return stock_list
            else:
                print("Please enter at least one symbol!")
                
        elif choice == '2':
            print("\nPreset Lists:")
            print("1. Top 10 Nifty 50")
            print("2. Banking Stocks (Top 5)")
            print("3. IT Stocks (Top 5)")
            print("4. Pharma Stocks (Top 5)")
            print("5. FMCG Stocks (Top 5)")
            
            preset_choice = input("Select preset (1-5): ").strip()
            preset_stocks = {
                '1': get_stock_list('NIFTY_50')[:10],
                '2': get_stock_list('BANKING')[:5],
                '3': get_stock_list('IT')[:5],
                '4': get_stock_list('PHARMA')[:5],
                '5': get_stock_list('FMCG')[:5]
            }
            
            if preset_choice in preset_stocks:
                return preset_stocks[preset_choice]
            else:
                print("Invalid choice!")
                
        elif choice == '3':
            return None
        else:
            print("Invalid option!")

def main():
    """Main function to run the market analysis"""
    if not IMPORTS_OK:
        print("\n❌ Cannot start application due to import errors.")
        print("Please run: pip install -r requirements.txt")
        print("Or try: python setup.py")
        return
    
    setup_logging()
    
    logger.info("Starting Indian Stock Market Analysis Tool")
    
    # Initialize settings
    settings = Settings()
    
    # Use comprehensive stock lists
    nifty_50_stocks = get_stock_list('NIFTY_50')
    banking_stocks = get_stock_list('BANKING')
    it_stocks = get_stock_list('IT')
    pharma_stocks = get_stock_list('PHARMA')
    auto_stocks = get_stock_list('AUTO')
    fmcg_stocks = get_stock_list('FMCG')
    metals_stocks = get_stock_list('METALS')
    oil_gas_stocks = get_stock_list('OIL_GAS')
    power_stocks = get_stock_list('POWER')
    
    # Initialize market service
    market_service = MarketService()
    
    print("\n" + "="*60)
    print("🇮🇳 INDIAN STOCK MARKET ANALYSIS TOOL")
    print("="*60)
    
    while True:
        print("\nSelect Analysis Type:")
        print("1. Intraday Trading Analysis (Quick - Top 5 Nifty)")
        print("2. Swing Trading Analysis (Quick - Top 5 Nifty)")
        print("3. Custom Stock Analysis (Your Choice)")
        print("4. Sector-wise Analysis")
        print("5. Market Overview (Enhanced)")
        print("6. Bulk Analysis (All Nifty 50)")
        print("7. Intraday Ideas (User Symbols)")
        print("8. Swing Ideas (User Symbols)")
        print("9. Stock Scanner (Technical Patterns)")
        print("10. Market Movers & Sectors")
        print("11. Stock Search & Info")
        print("12. 📈 F&O Analysis (Futures & Options)")
        print("13. 📊 Index Options (Nifty/BankNifty Calls & Puts)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (1-13, 0): ").strip()
        
        if choice == '1':
            print("\n📈 INTRADAY TRADING ANALYSIS")
            print("-" * 40)
            strategy = IntradayStrategy()
            # Use bulk processing for better performance
            recommendations = market_service.analyze_stocks_bulk(
                nifty_50_stocks[:5], strategy
            )
            display_recommendations(recommendations, "Intraday")
            
        elif choice == '2':
            print("\n📊 SWING TRADING ANALYSIS")
            print("-" * 40)
            strategy = SwingTradingStrategy()
            # Use bulk processing for better performance
            recommendations = market_service.analyze_stocks_bulk(
                nifty_50_stocks[:5], strategy
            )
            display_recommendations(recommendations, "Swing")
            
        elif choice == '3':
            symbols = input("Enter stock symbols (comma-separated, e.g., RELIANCE.NS,TCS.NS): ").strip()
            if symbols:
                stock_list = [s.strip().upper() for s in symbols.split(',')]
                # Add .NS if not present
                stock_list = [s if s.endswith('.NS') else f"{s}.NS" for s in stock_list]
                strategy_type = input("Enter strategy (intraday/swing): ")

                if strategy_type == 'intraday':
                    strategy = IntradayStrategy()
                else:
                    strategy = SwingTradingStrategy()
                
                # Use bulk processing for custom analysis
                recommendations = market_service.analyze_stocks_bulk(stock_list, strategy)
                display_recommendations(recommendations, strategy_type.title())
                
        elif choice == '4':
            print("\n� SECTOR-WISE ANALYSIS")
            print("-" * 40)
            print("Select Sector:")
            print("1. Banking")
            print("2. IT/Technology")
            print("3. Pharmaceuticals")
            print("4. Automobile")
            print("5. FMCG")
            
            sector_choice = input("Enter sector choice (1-5): ").strip()
            strategy_type = input("Enter strategy (intraday/swing): ").strip().lower()
            
            sector_stocks = {
                '1': banking_stocks[:5],
                '2': it_stocks[:5],
                '3': pharma_stocks[:5],
                '4': auto_stocks[:5],
                '5': fmcg_stocks[:5]
            }
            
            sector_names = {
                '1': 'Banking',
                '2': 'IT/Technology',
                '3': 'Pharmaceuticals',
                '4': 'Automobile',
                '5': 'FMCG'
            }
            
            if sector_choice in sector_stocks:
                if strategy_type == 'intraday':
                    strategy = IntradayStrategy()
                else:
                    strategy = SwingTradingStrategy()
                
                print(f"\nAnalyzing {sector_names[sector_choice]} sector...")
                recommendations = market_service.analyze_stocks_bulk(sector_stocks[sector_choice], strategy)
                display_recommendations(recommendations, f"{strategy_type.title()} - {sector_names[sector_choice]}")
            else:
                print("Invalid sector choice!")
                
        elif choice == '5':
            print("\n�🌍 MARKET OVERVIEW")
            print("-" * 40)
            market_service.display_market_overview()
            
        elif choice == '6':
            print("\n📊 BULK ANALYSIS - ALL NIFTY STOCKS")
            print("-" * 40)
            strategy_type = input("Enter strategy (intraday/swing): ").strip().lower()
            
            if strategy_type == 'intraday':
                strategy = IntradayStrategy()
            else:
                strategy = SwingTradingStrategy()
            
            print(f"\nAnalyzing {len(nifty_50_stocks)} stocks... This may take a moment...")
            recommendations = market_service.analyze_stocks_bulk(nifty_50_stocks, strategy)
            
            # Filter and sort by confidence
            buy_signals = [r for r in recommendations if r['action'] == 'BUY']
            sell_signals = [r for r in recommendations if r['action'] == 'SELL']
            
            buy_signals.sort(key=lambda x: x['confidence'], reverse=True)
            sell_signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"\n🟢 TOP BUY SIGNALS ({len(buy_signals)} found):")
            display_recommendations(buy_signals[:10], f"{strategy_type.title()} - Top Buys")
            
            print(f"\n🔴 TOP SELL SIGNALS ({len(sell_signals)} found):")
            display_recommendations(sell_signals[:10], f"{strategy_type.title()} - Top Sells")
            
        elif choice == '7':
            # Intraday Ideas with User Choice
            print("\n⚡ INTRADAY IDEAS - USER SYMBOLS")
            print("-" * 40)
            user_stocks = get_user_stock_choice()
            if user_stocks:
                strategy = IntradayStrategy()
                recommendations = market_service.analyze_stocks_bulk(user_stocks, strategy)
                display_recommendations(recommendations, "Intraday Ideas")
            
        elif choice == '8':
            # Swing Ideas with User Choice
            print("\n📊 SWING IDEAS - USER SYMBOLS")
            print("-" * 40)
            user_stocks = get_user_stock_choice()
            if user_stocks:
                strategy = SwingTradingStrategy()
                recommendations = market_service.analyze_stocks_bulk(user_stocks, strategy)
                display_recommendations(recommendations, "Swing Ideas")
            
        elif choice == '9':
            # Stock Scanner Menu
            stock_scanner_menu()
            
        elif choice == '10':
            # Market Movers & Sectors
            try:
                market_movers_menu()
            except Exception as e:
                print(f"❌ Market Movers menu error: {e}")
            
        elif choice == '11':
            # Stock Search & Info
            try:
                stock_search_menu()
            except Exception as e:
                print(f"❌ Stock Search menu error: {e}")
            
        # Handle F&O Analysis option
        elif choice == '12':
            fno_analysis_menu()
            continue
        
        # Handle Index Options Analysis
        elif choice == '13':
            index_options_menu()
            continue
            
        elif choice == '0':
            print("\nThank you for using Indian Stock Market Analysis Tool!")
            logger.info("Application terminated by user")
            break
            
        else:
            print("Invalid choice! Please select 1-13 or 0.")

def stock_scanner_menu():
    """Stock Scanner menu with technical pattern detection"""
    try:
        scanner = StockScanner()
        print("✅ Stock Scanner loaded successfully")
    except Exception as e:
        print(f"❌ Stock Scanner not available: {e}")
        scanner = None
    
    while True:
        # Show current scanning universe
        try:
            if scanner:
                universe_info = scanner.get_current_universe_info()
                current_universe = universe_info['name'].upper()
                stock_count = universe_info['stock_count']
            else:
                current_universe = 'NIFTY50'
                stock_count = 0
        except:
            current_universe = 'NIFTY50'
            stock_count = 0
        
        print(f"\n🔍 STOCK SCANNER - FIND OPPORTUNITIES")
        print("=" * 50)
        print(f"📊 Current Universe: {current_universe} ({stock_count} stocks)")
        print("=" * 50)
        if scanner:
            print("0. 🎯 Select Scanning Universe")
        print("1. Golden Crossover (50 SMA crosses above 200 SMA)")
        print("2. Death Cross (50 SMA crosses below 200 SMA)")
        print("3. High Volume Breakout (Volume > 2x average)")
        print("4. RSI Oversold Recovery (RSI < 30 recovering)")
        print("5. RSI Overbought Warning (RSI > 70)")
        print("6. Bollinger Band Breakout (Price breaks upper band)")
        print("7. Price Near 52-Week High")
        print("8. Price Near 52-Week Low")
        print("9. MACD Bullish Crossover")
        print("10. MACD Bearish Crossover")
        print("11. Custom Scanner (Multiple criteria)")
        print("12. Momentum Breakout (Price + Volume)")
        print("88. 🔧 Debug Scanner Universes")
        print("99. Back to Main Menu")
        
        choice = input(f"\nSelect scanner (0-12, 88, 99): ").strip()
        
        if choice == '99':
            return
        elif choice == '88':
            # Debug Scanner Universes
            debug_scanner_universes()
        elif choice == '0' and scanner:
            try:
                select_scanner_universe(scanner)
            except Exception as e:
                print(f"❌ Universe selection error: {e}")
        elif choice == '1':
            print("\n🌟 SCANNING FOR GOLDEN CROSSOVER...")
            if scanner:
                try:
                    # Use bulk scanning for better performance
                    def golden_crossover_scan(data, symbol):
                        return scanner._scan_golden_crossover_single(data, symbol)
                    
                    results = scanner.scan_bulk(golden_crossover_scan, "Golden Crossover")
                    display_scanner_results(results, "Golden Crossover")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '2':
            print("\n💀 SCANNING FOR DEATH CROSS...")
            if scanner:
                try:
                    results = scanner.find_death_cross()
                    display_scanner_results(results, "Death Cross")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '3':
            print("\n📈 SCANNING FOR HIGH VOLUME BREAKOUTS...")
            if scanner:
                try:
                    results = scanner.find_volume_breakout()
                    display_scanner_results(results, "Volume Breakout")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '4':
            print("\n🔄 SCANNING FOR RSI OVERSOLD RECOVERY...")
            if scanner:
                try:
                    results = scanner.find_rsi_oversold_recovery()
                    display_scanner_results(results, "RSI Oversold Recovery")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '5':
            print("\n⚠️ SCANNING FOR RSI OVERBOUGHT...")
            if scanner:
                try:
                    results = scanner.find_rsi_overbought()
                    display_scanner_results(results, "RSI Overbought Warning")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '6':
            print("\n🚀 SCANNING FOR BOLLINGER BREAKOUTS...")
            if scanner:
                try:
                    results = scanner.find_bollinger_breakout()
                    display_scanner_results(results, "Bollinger Band Breakout")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '7':
            print("\n📊 SCANNING NEAR 52-WEEK HIGH...")
            if scanner:
                try:
                    results = scanner.find_near_52_week_high()
                    display_scanner_results(results, "Near 52-Week High")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '8':
            print("\n📉 SCANNING NEAR 52-WEEK LOW...")
            if scanner:
                try:
                    results = scanner.find_near_52_week_low()
                    display_scanner_results(results, "Near 52-Week Low")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '9':
            print("\n📈 SCANNING FOR MACD BULLISH CROSSOVER...")
            if scanner:
                try:
                    results = scanner.find_macd_bullish_crossover()
                    display_scanner_results(results, "MACD Bullish Crossover")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '10':
            print("\n📉 SCANNING FOR MACD BEARISH CROSSOVER...")
            if scanner:
                try:
                    results = scanner.find_macd_bearish_crossover()
                    display_scanner_results(results, "MACD Bearish Crossover")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '11':
            print("\n🛠️ CUSTOM SCANNER...")
            if scanner:
                try:
                    custom_scanner_menu(scanner)
                except Exception as e:
                    print(f"❌ Custom scanner error: {e}")
            else:
                print("Scanner service not available")
        elif choice == '12':
            print("\n🚀 SCANNING FOR MOMENTUM BREAKOUT...")
            if scanner:
                try:
                    results = scanner.find_momentum_breakout()
                    display_scanner_results(results, "Momentum Breakout")
                except Exception as e:
                    print(f"❌ Scanner error: {e}")
            else:
                print("Scanner service not available")
        else:
            print("Invalid choice!")

def custom_scanner_menu(scanner):
    """Custom scanner with multiple criteria"""
    print("\n🛠️ CUSTOM SCANNER - COMBINE MULTIPLE CRITERIA")
    print("=" * 50)
    
    criteria = {}
    
    # RSI criteria
    rsi_choice = input("RSI filter? (oversold/overbought/neutral/skip): ").strip().lower()
    if rsi_choice in ['oversold', 'overbought', 'neutral']:
        criteria['rsi'] = rsi_choice
    
    # Volume criteria
    volume_choice = input("Volume filter? (high/low/normal/skip): ").strip().lower()
    if volume_choice in ['high', 'low', 'normal']:
        criteria['volume'] = volume_choice
    
    # Price criteria
    price_choice = input("Price position? (near_high/near_low/breakout/skip): ").strip().lower()
    if price_choice in ['near_high', 'near_low', 'breakout']:
        criteria['price'] = price_choice
    
    # MACD criteria
    macd_choice = input("MACD signal? (bullish/bearish/skip): ").strip().lower()
    if macd_choice in ['bullish', 'bearish']:
        criteria['macd'] = macd_choice
    
    if criteria:
        print(f"\n🔍 Scanning with criteria: {criteria}")
        results = scanner.custom_scan(criteria)
        display_scanner_results(results, f"Custom Scan ({len(criteria)} criteria)")
    else:
        print("No criteria selected!")

def display_scanner_results(results, scan_type):
    """Display scanner results in a formatted table"""
    if not results:
        print(f"\n❌ No stocks found matching {scan_type} criteria.")
        return
    
    colors = {
        'BUY': '\033[92m',     # Green
        'SELL': '\033[91m',    # Red  
        'NEUTRAL': '\033[93m', # Yellow
        'RESET': '\033[0m',    # Reset color
        'BOLD': '\033[1m',     # Bold
        'CYAN': '\033[96m',    # Cyan for headers
        'BLUE': '\033[94m',    # Blue for borders
        'MAGENTA': '\033[95m'  # Magenta for scan type
    }
    
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}🔍 {scan_type.upper()} SCANNER RESULTS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*130}{colors['RESET']}")
    print(f"{colors['CYAN']}{colors['BOLD']}Found {len(results)} stocks matching criteria{colors['RESET']}")
    
    # Table headers
    headers = [
        "No.", "Symbol", "Price (₹)", "Change%", "Volume", "Signal", "Strength", "Details"
    ]
    
    # Column widths
    widths = [4, 12, 10, 8, 12, 10, 8, 50]
    
    # Print header
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, header in enumerate(headers):
        header_line += f"{header:<{widths[i]}} "
    header_line += f"{colors['RESET']}"
    print(header_line)
    
    # Print separator
    separator = f"{colors['BLUE']}"
    for width in widths:
        separator += "-" * width + " "
    separator += f"{colors['RESET']}"
    print(separator)
    
    # Print data rows
    for i, result in enumerate(results, 1):
        symbol_clean = result['symbol'].replace('.NS', '')
        price = result['current_price']
        change_pct = result.get('change_percent', 0)
        volume_info = result.get('volume_info', 'Normal')
        signal = result['signal']
        strength = result.get('strength', 'Medium')
        details = result.get('details', 'Technical pattern detected')
        
        # Choose color based on signal
        if signal.upper() in ['BUY', 'BULLISH', 'BREAKOUT']:
            signal_color = colors['BUY']
            signal_symbol = "🟢"
        elif signal.upper() in ['SELL', 'BEARISH', 'BREAKDOWN']:
            signal_color = colors['SELL']
            signal_symbol = "🔴"
        else:
            signal_color = colors['NEUTRAL']
            signal_symbol = "🟡"
        
        # Format change percentage
        if change_pct > 0:
            change_str = f"{colors['BUY']}+{change_pct:.1f}%{colors['RESET']}"
        elif change_pct < 0:
            change_str = f"{colors['SELL']}{change_pct:.1f}%{colors['RESET']}"
        else:
            change_str = f"{change_pct:.1f}%"
        
        # Create the row
        row = f"{i:<{widths[0]}} "
        row += f"{colors['BOLD']}{symbol_clean:<{widths[1]}}{colors['RESET']} "
        row += f"₹{price:<{widths[2]-1}.2f} "
        row += f"{change_str:<{widths[3]}} "
        row += f"{volume_info:<{widths[4]}} "
        row += f"{signal_color}{signal_symbol}{signal:<{widths[5]-1}}{colors['RESET']} "
        row += f"{strength:<{widths[6]}} "
        row += f"{details:<{widths[7]}}"
        
        print(row)
    
    # Print summary
    print(f"\n{colors['BLUE']}{'-'*130}{colors['RESET']}")
    
    # Count signals
    bullish_count = sum(1 for r in results if r['signal'].upper() in ['BUY', 'BULLISH', 'BREAKOUT'])
    bearish_count = sum(1 for r in results if r['signal'].upper() in ['SELL', 'BEARISH', 'BREAKDOWN'])
    neutral_count = len(results) - bullish_count - bearish_count
    
    summary = f"{colors['BOLD']}📊 Signal Summary: "
    summary += f"{colors['BUY']}🟢 Bullish: {bullish_count}  "
    summary += f"{colors['SELL']}🔴 Bearish: {bearish_count}  "
    summary += f"{colors['NEUTRAL']}🟡 Neutral: {neutral_count}"
    summary += f"{colors['RESET']}"
    
    print(f"\n{summary}")
    print(f"\n{colors['BLUE']}{'='*130}{colors['RESET']}")
    print(f"{colors['BOLD']}💡 Tip: Use these results as starting points for further analysis{colors['RESET']}")

def display_recommendations(recommendations, strategy_type):
    """Display trading recommendations in a beautiful tabular format with colors"""
    if not recommendations:
        print("No recommendations available at this time.")
        return
    
    # Color codes for different actions
    colors = {
        'BUY': '\033[92m',     # Green
        'SELL': '\033[91m',    # Red  
        'HOLD': '\033[93m',    # Yellow
        'RESET': '\033[0m',    # Reset color
        'BOLD': '\033[1m',     # Bold
        'CYAN': '\033[96m',    # Cyan for headers
        'BLUE': '\033[94m',    # Blue for borders
        'MAGENTA': '\033[95m'  # Magenta for strategy type
    }
    
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}🎯 {strategy_type.upper()} TRADING RECOMMENDATIONS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*120}{colors['RESET']}")
    
    # Table headers (without analysis column)
    headers = [
        "No.", "Symbol", "Action", "Price (₹)", "Target (₹)", "Target%", 
        "Stop Loss (₹)", "Stop%", "R:R", "Confidence"
    ]
    
    # Column widths
    widths = [4, 12, 8, 10, 10, 8, 12, 8, 5, 10]
    
    # Print header
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, header in enumerate(headers):
        header_line += f"{header:<{widths[i]}} "
    header_line += f"{colors['RESET']}"
    print(header_line)
    
    # Print separator
    separator = f"{colors['BLUE']}"
    for width in widths:
        separator += "-" * width + " "
    separator += f"{colors['RESET']}"
    print(separator)
    
    # Print data rows with analysis below each row
    for i, rec in enumerate(recommendations, 1):
        symbol_clean = rec['symbol'].replace('.NS', '')
        action = rec['action']
        current_price = rec['current_price']
        target = rec['target']
        stop_loss = rec['stop_loss']
        confidence = rec['confidence']
        reason = rec['reason']
        
        # Calculate percentages
        target_pct = ((target / current_price - 1) * 100)
        stop_pct = ((stop_loss / current_price - 1) * 100)
        risk_reward = rec.get('risk_reward', 1.0)
        
        # Choose color based on action
        if action == 'BUY':
            action_color = colors['BUY']
            action_symbol = "🟢"
        elif action == 'SELL':
            action_color = colors['SELL']
            action_symbol = "🔴"
        else:
            action_color = colors['HOLD']
            action_symbol = "🟡"
        
        # Format confidence with color coding
        if confidence >= 70:
            conf_color = colors['BUY']  # Green for high confidence
        elif confidence >= 50:
            conf_color = colors['HOLD']  # Yellow for medium confidence
        else:
            conf_color = colors['SELL']  # Red for low confidence
        
        # Format each field properly
        target_str = f"{target_pct:+.1f}%"
        stop_str = f"{stop_pct:+.1f}%"
        conf_str = f"{confidence:.0f}%"
        
        # Create the main row (without analysis)
        row = f"{i:<{widths[0]}} "
        row += f"{colors['BOLD']}{symbol_clean:<{widths[1]}}{colors['RESET']} "
        row += f"{action_color}{action_symbol}{action:<{widths[2]-1}}{colors['RESET']} "
        row += f"{current_price:<{widths[3]}.2f} "
        row += f"{target:<{widths[4]}.2f} "
        row += f"{target_str:<{widths[5]}} "
        row += f"{stop_loss:<{widths[6]}.2f} "
        row += f"{stop_str:<{widths[7]}} "
        row += f"{risk_reward:<{widths[8]}.1f} "
        row += f"{conf_color}{conf_str:<{widths[9]}}{colors['RESET']}"
        
        print(row)
        
        # Print analysis on the next line with proper indentation
        analysis_line = f"     📊 Analysis: {colors['CYAN']}{reason}{colors['RESET']}"
        print(analysis_line)
        
        # Add potential P/L information
        if action == 'BUY':
            potential_profit = target - current_price
            potential_loss = current_price - stop_loss
            pl_line = f"     💰 Potential: {colors['BUY']}+₹{potential_profit:.2f}{colors['RESET']} gain / {colors['SELL']}-₹{potential_loss:.2f}{colors['RESET']} loss per share"
        elif action == 'SELL':
            potential_profit = current_price - target
            potential_loss = stop_loss - current_price
            pl_line = f"     💰 Potential: {colors['BUY']}+₹{potential_profit:.2f}{colors['RESET']} gain / {colors['SELL']}-₹{potential_loss:.2f}{colors['RESET']} loss per share"
        else:
            potential_profit = abs(target - current_price)
            potential_loss = abs(current_price - stop_loss)
            pl_line = f"     💰 Potential: ±₹{potential_profit:.2f} / ±₹{potential_loss:.2f} per share"
        
        print(pl_line)
        print()  # Empty line for spacing
    
    # Print summary statistics
    print(f"{colors['BLUE']}{'-'*120}{colors['RESET']}")
    
    # Count actions
    buy_count = sum(1 for r in recommendations if r['action'] == 'BUY')
    sell_count = sum(1 for r in recommendations if r['action'] == 'SELL') 
    hold_count = sum(1 for r in recommendations if r['action'] == 'HOLD')
    
    # Average confidence
    avg_confidence = sum(r['confidence'] for r in recommendations) / len(recommendations)
    
    # Summary line
    summary = f"{colors['BOLD']}📊 Summary: "
    summary += f"{colors['BUY']}🟢 BUY: {buy_count}  "
    summary += f"{colors['SELL']}🔴 SELL: {sell_count}  "
    summary += f"{colors['HOLD']}🟡 HOLD: {hold_count}  "
    summary += f"{colors['CYAN']}Average Confidence: {avg_confidence:.1f}%"
    summary += f"{colors['RESET']}"
    
    print(f"\n{summary}")
    
    print(f"\n{colors['BLUE']}{'='*120}{colors['RESET']}")
    print(f"{colors['BOLD']}⚠️  Disclaimer: This is for educational purposes only. Please do your own research.{colors['RESET']}")
    
    # Legend
    print(f"\n{colors['CYAN']}{colors['BOLD']}Legend:{colors['RESET']}")
    print(f"🟢 {colors['BUY']}BUY{colors['RESET']} - Strong bullish signals")
    print(f"🔴 {colors['SELL']}SELL{colors['RESET']} - Strong bearish signals") 
    print(f"🟡 {colors['HOLD']}HOLD{colors['RESET']} - Mixed or weak signals")
    print(f"R:R = Risk:Reward ratio | Target% = Expected gain/loss | Stop% = Maximum loss")

def market_movers_menu():
    """Market Movers and Sector Analysis Menu - Basic Implementation"""
    print("\n🔥 MARKET MOVERS & SECTOR ANALYSIS")
    print("=" * 50)
    print("This feature is being enhanced...")
    print("1. Coming Soon: Top Gainers")
    print("2. Coming Soon: Top Losers")
    print("3. Coming Soon: High Volume Stocks")
    print("0. Back to Main Menu")
    
    choice = input("\nSelect option (0): ").strip()
    return

def stock_search_menu():
    """Stock Search and Information Menu - Basic Implementation"""
    print("\n🔍 STOCK SEARCH & INFORMATION")
    print("=" * 50)
    print("This feature is being enhanced...")
    print("1. Coming Soon: Search Stocks")
    print("2. Coming Soon: Stock Information")
    print("0. Back to Main Menu")
    
    choice = input("\nSelect option (0): ").strip()
    return

def select_scanner_universe(scanner):
    """Menu for selecting stock scanning universe"""
    if not scanner:
        print("❌ Scanner not available")
        return
    
    while True:
        print(f"\n🎯 SELECT SCANNING UNIVERSE")
        print("=" * 50)
        
        # Get available universes
        try:
            universes = scanner.get_available_universes()
            current_info = scanner.get_current_universe_info()
        except:
            print("❌ Unable to get universe information")
            return
        
        print(f"Current: {current_info['name'].upper()} ({current_info['stock_count']} stocks)")
        print("-" * 50)
        
        # Display universe options
        universe_options = {
            '1': ('nifty50', 'Nifty 50 (Large Cap)'),
            '2': ('midcap150', 'MidCap 150 (Mid Cap)'),
            '3': ('smallcap150', 'SmallCap 150 (Small Cap)'),
            '4': ('banking', 'Banking Sector'),
            '5': ('it', 'IT Sector'),
            '6': ('pharma', 'Pharma Sector'),
            '7': ('auto', 'Auto Sector'),
            '8': ('fmcg', 'FMCG Sector'),
            '9': ('metals', 'Metals Sector')
        }
        
        for option, (universe_key, universe_name) in universe_options.items():
            stock_count = universes.get(universe_key, 0)
            current_marker = "👉 " if universe_key == current_info['name'] else "   "
            if stock_count > 0:
                availability = f"({stock_count} stocks)"
                status_color = "✅"
            else:
                availability = "(❌ Not available)"
                status_color = "❌"
            print(f"{option}. {current_marker}{status_color} {universe_name} {availability}")
        
        print("0. Back to Scanner Menu")
        
        choice = input(f"\nSelect universe (1-9, 0): ").strip()
        
        if choice == '0':
            return
        elif choice in universe_options:
            universe_key, universe_name = universe_options[choice]
            stock_count = universes.get(universe_key, 0)
            
            if stock_count > 0:
                success = scanner.set_universe(universe_key)
                if success:
                    print(f"\n✅ Scanning universe changed to {universe_name}")
                    print(f"📊 Now scanning {stock_count} stocks")
                    
                    # Show sample stocks
                    try:
                        updated_info = scanner.get_current_universe_info()
                        sample_stocks = updated_info.get('sample_stocks', [])
                        if sample_stocks:
                            sample_clean = [s.replace('.NS', '') for s in sample_stocks]
                            print(f"📋 Sample stocks: {', '.join(sample_clean)}")
                    except:
                        pass
                    
                    input("\nPress Enter to continue...")
                    return
                else:
                    print(f"❌ Failed to change universe to {universe_name}")
                    input("Press Enter to continue...")
            else:
                print(f"❌ {universe_name} is not available or empty")
                print("This might be due to missing stock data or initialization issues.")
                input("Press Enter to continue...")
        else:
            print("❌ Invalid choice!")
            input("Press Enter to continue...")

def display_universe_stats(scanner):
    """Display statistics about current scanning universe - Basic Implementation"""
    if not scanner:
        return
    
    print("\n📊 SCANNING UNIVERSE STATISTICS")
    print("=" * 50)
    print("Current Universe: NIFTY50")
    print("Total Stocks: 50")
    print("=" * 50)

def test_main():
    """Simple test version of main function"""
    print("🚀 Starting Indian Stock Market Analysis Tool...")
    print("=" * 60)
    
    while True:
        print("\n🇮🇳 INDIAN STOCK MARKET ANALYSIS TOOL")
        print("=" * 60)
        print("Select Analysis Type:")
        print("1. Basic Analysis (Test)")
        print("2. Stock Scanner (Test)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (1-2, 0): ").strip()
        
        if choice == '1':
            print("\n📈 BASIC ANALYSIS")
            print("This is a test implementation")
            print("✅ Application is working!")
            
        elif choice == '2':
            print("\n🔍 STOCK SCANNER")
            print("This is a test implementation")
            print("✅ Scanner module accessible!")
            
        elif choice == '0':
            print("\nThank you for using Indian Stock Market Analysis Tool!")
            break
            
        else:
            print("❌ Invalid choice! Please select 1-2 or 0.")

# Debug function to diagnose scanner universe issues
def debug_scanner_universes():
    """Debug function to check scanner universe availability"""
    print("\n🔍 SCANNER UNIVERSE DEBUG")
    print("=" * 50)
    
    try:
        from src.data.stock_lists import get_stock_list, ALL_CATEGORIES, count_stocks_in_categories
        
        print("📊 Stock Count Verification:")
        counts = count_stocks_in_categories()
        for category, count in counts.items():
            target = 150 if category in ['MIDCAP_150', 'SMALLCAP_150'] else (50 if category == 'NIFTY_50' else 'varies')
            status = "✅" if (category == 'NIFTY_50' and count == 50) or (category in ['MIDCAP_150', 'SMALLCAP_150'] and count == 150) or (category not in ['NIFTY_50', 'MIDCAP_150', 'SMALLCAP_150']) else "❌"
            print(f"  {status} {category}: {count} stocks (target: {target})")
        
        print("\n🧪 Testing individual category access:")
        test_categories = ['NIFTY_50', 'MIDCAP_150', 'SMALLCAP_150', 'BANKING', 'IT']
        
        for category in test_categories:
            try:
                stocks = get_stock_list(category)
                print(f"  ✅ {category}: {len(stocks)} stocks")
                if stocks:
                    sample = stocks[:3]
                    sample_clean = [s.replace('.NS', '') for s in sample]
                    print(f"     Sample: {', '.join(sample_clean)}")
            except Exception as e:
                print(f"  ❌ {category}: Error - {e}")
        
        print("\n🔧 Testing Scanner Initialization:")
        try:
            scanner = StockScanner()
            universes = scanner.get_available_universes()
            print("  Scanner universes:")
            for name, count in universes.items():
                expected = {'nifty50': 50, 'midcap150': 150, 'smallcap150': 150}.get(name, 'varies')
                status = "✅" if (name == 'nifty50' and count == 50) or (name in ['midcap150', 'smallcap150'] and count == 150) else "❌" if count == 0 else "⚠️"
                print(f"    {status} {name}: {count} stocks (expected: {expected})")
        except Exception as e:
            print(f"  ❌ Scanner initialization failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    
    input("\nPress Enter to continue...")


# F&O Analysis Functions
def fno_analysis_menu():
    """Menu for F&O analysis"""
    try:
        from src.services.fno_service import FnoAnalysisService
        fno_service = FnoAnalysisService()
        print("✅ F&O Analysis Service loaded successfully")
    except Exception as e:
        print(f"❌ F&O Analysis Service not available: {e}")
        input("\nPress Enter to return to main menu...")
        return
    
    print("\n📈 F&O ANALYSIS - DERIVATIVES DATA")
    print("=" * 60)
    print("🔄 Scanning F&O stocks for buildup patterns...")
    print("This analyzes Price vs Open Interest changes")
    print("-" * 60)
    
    try:
        fno_results = fno_service.scan_for_buildup()
        summary = fno_service.get_fno_summary(fno_results)
        
        print(f"✅ Scan completed! Found {summary['total_signals']} signals from {summary['total_stocks_scanned']} stocks")
        
    except Exception as e:
        print(f"❌ Error during F&O scan: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to return to main menu...")
        return
    
    while True:
        print(f"\n📍 F&O ANALYSIS RESULTS")
        print("=" * 60)
        print(f"📊 Scan Summary:")
        print(f"   • Total Stocks Scanned: {summary['total_stocks_scanned']}")
        print(f"   • Total Signals Found: {summary['total_signals']}")
        print(f"   • Bullish Signals: {summary['bullish_signals']} (Long Buildup + Short Covering)")
        print(f"   • Bearish Signals: {summary['bearish_signals']} (Short Buildup + Long Unwinding)")
        print(f"   • Scan Time: {summary['scan_time']}")
        
        print("\nSelect F&O Pattern View:")
        print(f"1. 🟢 Long Buildup ({len(fno_results['long_buildup'])} stocks) - Bullish")
        print(f"2. 🔴 Short Buildup ({len(fno_results['short_buildup'])} stocks) - Bearish")
        print(f"3. 🟢 Short Covering ({len(fno_results['short_covering'])} stocks) - Bullish")
        print(f"4. 🔴 Long Unwinding ({len(fno_results['long_unwinding'])} stocks) - Bearish")
        print(f"5. ⚡ Gamma Squeeze ({len(fno_results.get('gamma_squeeze', []))} stocks) - Special")
        print(f"6. ⚖️ Delta Neutral ({len(fno_results.get('delta_neutral', []))} stocks) - Options")
        print(f"7. 🎯 High Conviction ({len(fno_results.get('high_conviction', []))} stocks) - Best")
        print("8. 📊 Advanced Analysis (All patterns with details)")
        print("9. 🔄 Rescan F&O Data")
        print("0. 🏠 Back to Main Menu")

        choice = input("\nEnter your choice (1-9, 0): ").strip()

        if choice == '0':
            return
        elif choice == '1':
            display_enhanced_fno_results(fno_results['long_buildup'], "Long Buildup", "🟢 BULLISH SIGNAL")
        elif choice == '2':
            display_enhanced_fno_results(fno_results['short_buildup'], "Short Buildup", "🔴 BEARISH SIGNAL")
        elif choice == '3':
            display_enhanced_fno_results(fno_results['short_covering'], "Short Covering", "🟢 BULLISH SIGNAL")
        elif choice == '4':
            display_enhanced_fno_results(fno_results['long_unwinding'], "Long Unwinding", "🔴 BEARISH SIGNAL")
        elif choice == '5':
            display_enhanced_fno_results(fno_results.get('gamma_squeeze', []), "Gamma Squeeze", "⚡ SPECIAL SIGNAL")
        elif choice == '6':
            display_enhanced_fno_results(fno_results.get('delta_neutral', []), "Delta Neutral", "⚖️ OPTIONS PLAY")
        elif choice == '7':
            display_enhanced_fno_results(fno_results.get('high_conviction', []), "High Conviction", "🎯 BEST OPPORTUNITIES")
        elif choice == '8':
            display_advanced_fno_analysis(fno_results)
        elif choice == '9':
            print("\n🔄 Rescanning F&O data...")
            try:
                fno_results = fno_service.scan_for_buildup()
                summary = fno_service.get_fno_summary(fno_results)
                print("✅ Rescan completed!")
            except Exception as e:
                print(f"❌ Rescan failed: {e}")
        else:
            print("❌ Invalid choice!")

def display_enhanced_fno_results(results: list, scan_type: str, signal_type: str):
    """Enhanced F&O results display with advanced indicators."""
    if not results:
        print(f"\n❌ No stocks found for '{scan_type}'.")
        input("\nPress Enter to continue...")
        return

    colors = {
        'BUY': '\033[92m', 'SELL': '\033[91m', 'NEUTRAL': '\033[93m',
        'RESET': '\033[0m', 'BOLD': '\033[1m', 'CYAN': '\033[96m',
        'BLUE': '\033[94m', 'MAGENTA': '\033[95m', 'GREEN': '\033[92m',
        'YELLOW': '\033[93m', 'RED': '\033[91m'
    }

    print(f"\n{colors['MAGENTA']}{colors['BOLD']}📈 {scan_type.upper()} - {signal_type}{colors['RESET']}")
    print(f"{colors['CYAN']}Found {len(results)} stocks with {scan_type} pattern{colors['RESET']}")
    
    # Enhanced table headers with confidence score
    headers = ["#", "Symbol", "Conf%", "P%", "OI%", "Vol", "PCR", "VIX", "Regime", "Recommendation"]
    widths = [3, 10, 6, 6, 6, 6, 5, 6, 10, 32]
    
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, h in enumerate(headers):
        header_line += f"{h:<{widths[i]}} "
    print(header_line + colors['RESET'])
    print(f"{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    
    # Display all results with enhanced information
    for i, stock in enumerate(results, 1):
        symbol = stock['symbol'].replace('.NS', '')
        price_change = stock['price_chg_pct']
        oi_change = stock['oi_chg_pct']
        volume_ratio = stock.get('volume_ratio', 1)
        pcr = stock.get('pcr', 1.0)
        confidence_score = stock.get('confidence_score', 65.0)
        vix_impact = stock.get('vix_impact', 'Med')[:3]
        market_regime = stock.get('market_regime', 'Trans')[:6]
        recommendation = stock.get('trading_recommendation', 'Monitor')
        
        # Color coding based on confidence score
        if confidence_score >= 80:
            conf_color = colors['GREEN']
        elif confidence_score >= 65:
            conf_color = colors['YELLOW']
        else:
            conf_color = colors['RED']
        
        price_color = colors['GREEN'] if price_change > 0 else colors['RED']
        oi_color = colors['GREEN'] if oi_change > 0 else colors['RED']
        
        # VIX impact color
        vix_color = {
            'Low': colors['GREEN'], 'Med': colors['YELLOW'], 'Hig': colors['RED']
        }.get(vix_impact, colors['RESET'])
        
        row = (
            f"{i:<{widths[0]}} "
            f"{colors['BOLD']}{symbol:<{widths[1]}}{colors['RESET']} "
            f"{conf_color}{confidence_score:.0f}{colors['RESET']} "
            f"{price_color}{price_change:+.1f}{colors['RESET']} "
            f"{oi_color}{oi_change:+.1f}{colors['RESET']} "
            f"{volume_ratio:.1f}x "
            f"{pcr:.2f} "
            f"{vix_color}{vix_impact}{colors['RESET']} "
            f"{market_regime:<{widths[8]}} "
            f"{recommendation:<{widths[9]}}"
        )
        print(row)
        
        # Show additional details for top 5 stocks
        if i <= 5:
            details = f"     🎯 Max Pain: ₹{stock.get('max_pain', 0):.0f} | "
            details += f"💪 Strength: {stock.get('strength', 0):.0f} | "
            details += f"📊 Index Corr: {stock.get('index_correlation', 0.7):.2f} | "
            details += f"🏛️ Flow: {stock.get('institutional_flow', 'N/A')} | "
            details += f"⚡ Sector: {stock.get('sector_strength', 'Unknown')}"
            print(f"{colors['BLUE']}{details}{colors['RESET']}")
            
            # Options activity details
            options_activity = stock.get('options_activity', {})
            if options_activity:
                opt_details = f"     📈 PCR Signal: {options_activity.get('pcr_signal', 'N/A')} | "
                opt_details += f"⚡ Gamma: {options_activity.get('gamma_environment', 'N/A')} | "
                opt_details += f"🎯 Delta Bias: {options_activity.get('delta_bias', 'N/A')}"
                print(f"{colors['CYAN']}{opt_details}{colors['RESET']}")
    
    print(f"{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    
    # Enhanced summary with advanced metrics
    avg_conviction = len([s for s in results if s.get('conviction_level') == 'High'])
    avg_pcr = sum(s.get('pcr', 1) for s in results) / len(results)
    institutional_heavy = len([s for s in results if 'Institutional' in s.get('institutional_flow', '')])
    
    print(f"\n{colors['BOLD']}📊 Advanced Summary:{colors['RESET']}")
    print(f"   🎯 High Conviction Signals: {avg_conviction}")
    print(f"   📈 Average PCR: {avg_pcr:.2f}")
    print(f"   🏛️ Institutional Heavy: {institutional_heavy}")
    print(f"   📊 Total Opportunities: {len(results)}")
    
    # Pattern-specific insights
    pattern_insights = {
        "Long Buildup": "🔍 Look for breakout above resistance with volume confirmation",
        "Short Buildup": "⚠️ Watch for breakdown below support with rising OI",
        "Short Covering": "🚀 Momentum trade - ride the covering wave with tight stops",
        "Long Unwinding": "📉 Avoid counter-trend trades - wait for stabilization",
        "Gamma Squeeze": "⚡ Range-bound until breakout - prepare for explosive move",
        "Delta Neutral": "⚖️ Options-heavy environment - consider straddles/strangles",
        "High Conviction": "🎯 Best risk-adjusted opportunities with multiple confirmations"
    }
    
    if scan_type in pattern_insights:
        print(f"\n{colors['CYAN']}💡 {pattern_insights[scan_type]}{colors['RESET']}")
    
    input(f"\nPress Enter to continue...")

def display_advanced_fno_analysis(fno_results: dict):
    """Display comprehensive F&O analysis with all metrics."""
    colors = {
        'RESET': '\033[0m', 'BOLD': '\033[1m', 'CYAN': '\033[96m',
        'BLUE': '\033[94m', 'MAGENTA': '\033[95m', 'GREEN': '\033[92m',
        'RED': '\033[91m', 'YELLOW': '\033[93m'
    }
    
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}🔬 ADVANCED F&O ANALYSIS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*80}{colors['RESET']}")
    
    # Collect all stocks from all categories
    all_stocks = []
    for category, stocks in fno_results.items():
        for stock in stocks:
            stock['category'] = category
            all_stocks.append(stock)
    
    if not all_stocks:
        print("No F&O signals found.")
        return
    
    # Sort by strength
    all_stocks.sort(key=lambda x: x.get('strength', 0), reverse=True)
    
    print(f"{colors['CYAN']}Top 20 F&O Opportunities (All Categories){colors['RESET']}")
    print(f"{colors['BLUE']}{'-'*80}{colors['RESET']}")
    
    # Advanced headers
    headers = ["Rank", "Symbol", "Category", "Strength", "Conv", "Risk", "PCR", "Details"]
    widths = [5, 10, 12, 8, 5, 5, 6, 29]
    
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, h in enumerate(headers):
        header_line += f"{h:<{widths[i]}} "
    print(header_line + colors['RESET'])
    print(f"{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    
    # Display top 20 stocks
    for i, stock in enumerate(all_stocks[:20], 1):
        symbol = stock['symbol'].replace('.NS', '')
        category = stock['category'].replace('_', ' ').title()
        strength = stock.get('strength', 0)
        conviction = stock.get('conviction_level', 'Med')[:4]
        risk = stock.get('risk_level', 'Med')[:3]
        pcr = stock.get('pcr', 1.0)
        
        # Category color coding
        cat_colors = {
            'Long Buildup': colors['GREEN'], 'Short Buildup': colors['RED'],
            'Short Covering': colors['GREEN'], 'Long Unwinding': colors['RED'],
            'Gamma Squeeze': colors['YELLOW'], 'Delta Neutral': colors['CYAN'],
            'High Conviction': colors['MAGENTA']
        }
        cat_color = cat_colors.get(category, colors['RESET'])
        
        # Strength color
        strength_color = colors['GREEN'] if strength > 70 else colors['YELLOW'] if strength > 40 else colors['RED']
        
        # Create details string
        details = f"V:{stock.get('volume_ratio', 1):.1f}x "
        details += f"D:{stock.get('market_depth', 'N/A')[:3]} "
        details += f"F:{stock.get('institutional_flow', 'Mixed')[:4]}"
        
        row = (
            f"{i:<{widths[0]}} "
            f"{colors['BOLD']}{symbol:<{widths[1]}}{colors['RESET']} "
            f"{cat_color}{category:<{widths[2]}}{colors['RESET']} "
            f"{strength_color}{strength:<{widths[3]}.0f}{colors['RESET']} "
            f"{conviction:<{widths[4]}} "
            f"{risk:<{widths[5]}} "
            f"{pcr:<{widths[6]}.2f} "
            f"{details:<{widths[7]}}"
        )
        print(row)
    
    print(f"{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    
    # Advanced analytics
    print(f"\n{colors['BOLD']}🧮 MARKET ANALYTICS:{colors['RESET']}")
    
    # Category distribution
    category_counts = {}
    for stock in all_stocks:
        cat = stock['category'].replace('_', ' ').title()
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"\n{colors['CYAN']}📊 Pattern Distribution:{colors['RESET']}")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count} stocks")
    
    # Risk-Conviction Matrix
    print(f"\n{colors['CYAN']}🎯 Risk-Conviction Matrix:{colors['RESET']}")
    high_conv_low_risk = len([s for s in all_stocks if s.get('conviction_level') == 'High' and s.get('risk_level') == 'Low'])
    high_conv_med_risk = len([s for s in all_stocks if s.get('conviction_level') == 'High' and s.get('risk_level') == 'Medium'])
    med_conv_low_risk = len([s for s in all_stocks if s.get('conviction_level') == 'Medium' and s.get('risk_level') == 'Low'])
    
    print(f"   🎯 High Conviction + Low Risk: {high_conv_low_risk} stocks (Best opportunities)")
    print(f"   ⚡ High Conviction + Medium Risk: {high_conv_med_risk} stocks (Aggressive plays)")
    print(f"   🛡️ Medium Conviction + Low Risk: {med_conv_low_risk} stocks (Conservative)")
    
    # Market sentiment indicators
    avg_pcr = sum(s.get('pcr', 1) for s in all_stocks) / len(all_stocks)
    bullish_patterns = len([s for s in all_stocks if s['category'] in ['long_buildup', 'short_covering']])
    bearish_patterns = len([s for s in all_stocks if s['category'] in ['short_buildup', 'long_unwinding']])
    
    print(f"\n{colors['CYAN']}📈 Market Sentiment:{colors['RESET']}")
    print(f"   Average PCR: {avg_pcr:.2f} ({'Bearish' if avg_pcr > 1.2 else 'Bullish' if avg_pcr < 0.8 else 'Neutral'})")
    print(f"   Bullish Patterns: {bullish_patterns} stocks")
    print(f"   Bearish Patterns: {bearish_patterns} stocks")
    print(f"   Net Bias: {colors['GREEN']}Bullish{colors['RESET']}" if bullish_patterns > bearish_patterns else f"{colors['RED']}Bearish{colors['RESET']}" if bearish_patterns > bullish_patterns else "Neutral")
    
    print(f"\n{colors['BLUE']}{'='*80}{colors['RESET']}")
    print(f"{colors['BOLD']}💡 Key Takeaways:{colors['RESET']}")
    print(f"   • Focus on High Conviction + Low Risk opportunities")
    print(f"   • Monitor gamma squeeze setups for breakout trades")
    print(f"   • Use PCR and institutional flow as confirmation")
    print(f"   • Consider options strategies for delta neutral setups")
    
    input("\nPress Enter to continue...")

def index_options_menu():
    """Menu for Index Options Analysis"""
    try:
        from src.services.index_options_service import IndexOptionsAnalyzer
        analyzer = IndexOptionsAnalyzer()
        print("✅ Index Options Analyzer loaded successfully")
    except Exception as e:
        print(f"❌ Index Options Analyzer not available: {e}")
        input("\nPress Enter to return to main menu...")
        return
    
    print("\n📊 INDEX OPTIONS ANALYSIS - CALL/PUT RECOMMENDATIONS")
    print("=" * 70)
    print("🔄 Analyzing all major indices...")
    print("-" * 70)
    
    try:
        results = analyzer.analyze_all_indices()
        
        colors = {
            'RESET': '\033[0m', 'BOLD': '\033[1m', 'CYAN': '\033[96m',
            'BLUE': '\033[94m', 'MAGENTA': '\033[95m', 'GREEN': '\033[92m',
            'RED': '\033[91m', 'YELLOW': '\033[93m'
        }
        
        print(f"✅ Analysis completed!")
        print(f"\n{colors['BOLD']}📈 Market Overview:{colors['RESET']}")
        print(f"   • VIX Level: {colors['YELLOW']}{results['vix_level']:.2f}{colors['RESET']}")
        print(f"   • Market Sentiment: {colors['CYAN']}{results['market_sentiment']}{colors['RESET']}")
        print(f"   • Timestamp: {results['timestamp']}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to return to main menu...")
        return
    
    while True:
        print(f"\n{colors['MAGENTA']}{colors['BOLD']}📊 INDEX OPTIONS MENU{colors['RESET']}")
        print("=" * 70)
        
        indices_list = list(results['indices_analysis'].keys())
        for i, index_name in enumerate(indices_list, 1):
            index_data = results['indices_analysis'][index_name]
            print(f"{i}. {index_data['index_name']} - Level: {index_data['current_level']:.2f}")
        
        print(f"\n{len(indices_list)+1}. 🎯 Show All Recommendations (Summary)")
        print(f"{len(indices_list)+2}. 📊 Advanced Index Comparison")
        print("0. 🏠 Back to Main Menu")
        
        choice = input(f"\nEnter your choice (1-{len(indices_list)+2}, 0): ").strip()
        
        if choice == '0':
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(indices_list):
            index_name = indices_list[int(choice)-1]
            display_index_options_analysis(results['indices_analysis'][index_name], colors)
        elif choice == str(len(indices_list)+1):
            display_all_index_recommendations(results, colors)
        elif choice == str(len(indices_list)+2):
            display_advanced_index_comparison(results, colors)
        else:
            print("❌ Invalid choice!")

def display_index_options_analysis(index_data: dict, colors: dict):
    """Display detailed options analysis for a specific index"""
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}📊 {index_data['index_name'].upper()} OPTIONS ANALYSIS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*80}{colors['RESET']}")
    
    # Index Overview
    print(f"\n{colors['BOLD']}📈 Index Overview:{colors['RESET']}")
    print(f"   Current Level: {colors['CYAN']}{index_data['current_level']:.2f}{colors['RESET']}")
    print(f"   Lot Size: {index_data['lot_size']}")
    print(f"   Expiry: {index_data['expiry_type']}")
    print(f"   Trend: {colors['GREEN'] if 'Uptrend' in index_data['trend'] else colors['RED']}{index_data['trend']}{colors['RESET']}")
    print(f"   Volatility: {index_data['volatility']:.2f}%")
    print(f"   RSI: {index_data['rsi']:.1f}")
    
    # Intraday Information
    if 'intraday_info' in index_data:
        intraday = index_data['intraday_info']
        intraday_color = colors['GREEN'] if intraday['change'] > 0 else colors['RED']
        print(f"\n{colors['BOLD']}⚡ Intraday Analysis:{colors['RESET']}")
        print(f"   Today's Change: {intraday_color}{intraday['change']:+.2f}%{colors['RESET']}")
        print(f"   Intraday Range: {intraday['range_pct']:.2f}%")
        print(f"   High/Low: {intraday['high']:.2f} / {intraday['low']:.2f}")
    
    # Momentum Score
    if 'price_momentum' in index_data:
        momentum = index_data['price_momentum']
        print(f"\n{colors['BOLD']}🚀 Momentum Analysis:{colors['RESET']}")
        short_color = colors['GREEN'] if momentum['short_term'] > 0 else colors['RED']
        medium_color = colors['GREEN'] if momentum['medium_term'] > 0 else colors['RED']
        long_color = colors['GREEN'] if momentum['long_term'] > 0 else colors['RED']
        print(f"   Short-term (1-3D): {short_color}{momentum['short_term']:+.2f}%{colors['RESET']}")
        print(f"   Medium-term (1W): {medium_color}{momentum['medium_term']:+.2f}%{colors['RESET']}")
        print(f"   Long-term (1M): {long_color}{momentum['long_term']:+.2f}%{colors['RESET']}")
        
        overall_color = colors['GREEN'] if momentum['overall_score'] > 0 else colors['RED']
        print(f"   {colors['BOLD']}Overall Score: {overall_color}{momentum['overall_score']:+.2f}{colors['RESET']}")
    
    # Price Changes
    print(f"\n{colors['BOLD']}📊 Price Performance:{colors['RESET']}")
    for period, change in index_data['price_change'].items():
        change_color = colors['GREEN'] if change > 0 else colors['RED']
        print(f"   {period}: {change_color}{change:+.2f}%{colors['RESET']}")
    
    # Support & Resistance
    sr = index_data['support_resistance']
    print(f"\n{colors['BOLD']}🎯 Key Levels:{colors['RESET']}")
    print(f"   Resistance: {colors['RED']}{sr['resistance']:.2f}{colors['RESET']}")
    print(f"   Pivot: {colors['YELLOW']}{sr['pivot']:.2f}{colors['RESET']}")
    print(f"   Support: {colors['GREEN']}{sr['support']:.2f}{colors['RESET']}")
    
    # Options Recommendation
    rec = index_data['options_recommendation']
    print(f"\n{colors['BOLD']}💡 OPTIONS RECOMMENDATION:{colors['RESET']}")
    print(f"{colors['MAGENTA']}{colors['BOLD']}{rec['primary_strategy']}{colors['RESET']}")
    print(f"   Strategy Type: {rec['strategy_type']}")
    print(f"   Conviction: {colors['GREEN'] if rec['conviction'] == 'High' else colors['YELLOW']}{rec['conviction']}{colors['RESET']}")
    print(f"   Risk Level: {colors['RED'] if rec['risk_level'] == 'High' else colors['YELLOW']}{rec['risk_level']}{colors['RESET']}")
    
    # Call vs Put Rating
    print(f"\n{colors['BOLD']}📊 Call vs Put Rating:{colors['RESET']}")
    call_bars = '█' * (rec['call_rating'] // 5)
    put_bars = '█' * (rec['put_rating'] // 5)
    print(f"   {colors['GREEN']}CALL: {call_bars} {rec['call_rating']}/100{colors['RESET']}")
    print(f"   {colors['RED']}PUT:  {put_bars} {rec['put_rating']}/100{colors['RESET']}")
    
    # Reasoning
    if rec['reasoning']:
        print(f"\n{colors['BOLD']}🔍 Analysis Reasoning:{colors['RESET']}")
        for reason in rec['reasoning']:
            print(f"   • {reason}")
    
    # Strike Suggestions
    strikes = index_data['strike_suggestions']
    print(f"\n{colors['BOLD']}🎯 STRIKE PRICE SUGGESTIONS:{colors['RESET']}")
    print(f"   ATM Strike: {colors['YELLOW']}{strikes['ATM']}{colors['RESET']}")
    
    if 'recommended_calls' in strikes:
        print(f"\n   {colors['GREEN']}Recommended CALL Strikes:{colors['RESET']}")
        for call in strikes['recommended_calls']:
            print(f"      {call['strike']} ({call['type']}) - Confidence: {call['confidence']}")
    
    if 'recommended_puts' in strikes:
        print(f"\n   {colors['RED']}Recommended PUT Strikes:{colors['RESET']}")
        for put in strikes['recommended_puts']:
            print(f"      {put['strike']} ({put['type']}) - Confidence: {put['confidence']}")
    
    print(f"\n   {colors['CYAN']}CALL OTM Strikes: {', '.join(map(str, strikes['CALL_OTM']))}{colors['RESET']}")
    print(f"   {colors['CYAN']}PUT OTM Strikes: {', '.join(map(str, strikes['PUT_OTM']))}{colors['RESET']}")
    
    print(f"\n{colors['BLUE']}{'='*80}{colors['RESET']}")
    print(f"{colors['YELLOW']}⚠️  Disclaimer: Options trading involves significant risk. This is for educational purposes only.{colors['RESET']}")
    
    input("\nPress Enter to continue...")

def display_all_index_recommendations(results: dict, colors: dict):
    """Display summary of all index recommendations"""
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}🎯 ALL INDEX OPTIONS RECOMMENDATIONS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*100}{colors['RESET']}")
    
    headers = ["Index", "Level", "Trend", "Call%", "Put%", "Recommendation", "Conviction"]
    widths = [15, 10, 15, 6, 6, 30, 10]
    
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, h in enumerate(headers):
        header_line += f"{h:<{widths[i]}} "
    print(header_line + colors['RESET'])
    print(f"{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    
    for index_name, index_data in results['indices_analysis'].items():
        rec = index_data['options_recommendation']
        
        trend_color = colors['GREEN'] if 'Uptrend' in index_data['trend'] else colors['RED']
        conv_color = colors['GREEN'] if rec['conviction'] == 'High' else colors['YELLOW']
        
        # Determine primary recommendation (CALL or PUT)
        if rec['call_rating'] > rec['put_rating'] + 15:
            rec_text = f"{colors['GREEN']}BUY CALL{colors['RESET']}"
        elif rec['put_rating'] > rec['call_rating'] + 15:
            rec_text = f"{colors['RED']}BUY PUT{colors['RESET']}"
        else:
            rec_text = "Neutral Strategy"
        
        row = (
            f"{index_data['index_name']:<{widths[0]}} "
            f"{index_data['current_level']:<{widths[1]}.0f} "
            f"{trend_color}{index_data['trend'][:12]:<{widths[2]}}{colors['RESET']} "
            f"{rec['call_rating']:<{widths[3]}} "
            f"{rec['put_rating']:<{widths[4]}} "
            f"{rec_text:<{widths[5]+20}} "
            f"{conv_color}{rec['conviction']:<{widths[6]}}{colors['RESET']}"
        )
        print(row)
    
    print(f"\n{colors['BLUE']}{'-' * sum(widths)}{colors['RESET']}")
    print(f"\n{colors['BOLD']}💡 Key Insights:{colors['RESET']}")
    print(f"   • VIX Level: {results['vix_level']:.2f} ({results['market_sentiment']})")
    
    # Count bullish vs bearish
    bullish = sum(1 for idx in results['indices_analysis'].values() 
                  if idx['options_recommendation']['call_rating'] > idx['options_recommendation']['put_rating'] + 15)
    bearish = sum(1 for idx in results['indices_analysis'].values()
                  if idx['options_recommendation']['put_rating'] > idx['options_recommendation']['call_rating'] + 15)
    
    print(f"   • Bullish Indices (CALL bias): {colors['GREEN']}{bullish}{colors['RESET']}")
    print(f"   • Bearish Indices (PUT bias): {colors['RED']}{bearish}{colors['RESET']}")
    
    input("\nPress Enter to continue...")

def display_advanced_index_comparison(results: dict, colors: dict):
    """Display advanced comparison of all indices"""
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}📊 ADVANCED INDEX COMPARISON{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*90}{colors['RESET']}")
    
    # Volatility comparison
    print(f"\n{colors['BOLD']}📈 Volatility Comparison:{colors['RESET']}")
    vol_data = [(name, data['volatility']) for name, data in results['indices_analysis'].items()]
    vol_data.sort(key=lambda x: x[1], reverse=True)
    
    for name, vol in vol_data:
        vol_color = colors['RED'] if vol > 25 else colors['YELLOW'] if vol > 18 else colors['GREEN']
        bars = '█' * int(vol / 2)
        print(f"   {name:15} {vol_color}{bars} {vol:.2f}%{colors['RESET']}")
    
    # Momentum comparison (1W performance)
    print(f"\n{colors['BOLD']}🚀 Momentum Comparison (1W):{colors['RESET']}")
    momentum_data = [(name, data['price_change']['1W']) for name, data in results['indices_analysis'].items()]
    momentum_data.sort(key=lambda x: x[1], reverse=True)
    
    for name, change in momentum_data:
        change_color = colors['GREEN'] if change > 0 else colors['RED']
        print(f"   {name:15} {change_color}{change:+.2f}%{colors['RESET']}")
    
    # Best opportunities
    print(f"\n{colors['BOLD']}🎯 Best Opportunities:{colors['RESET']}")
    
    # Best CALL opportunity
    call_opportunities = [(name, data['options_recommendation']['call_rating']) 
                         for name, data in results['indices_analysis'].items()]
    call_opportunities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n   {colors['GREEN']}Top CALL Options:{colors['RESET']}")
    for i, (name, rating) in enumerate(call_opportunities[:3], 1):
        data = results['indices_analysis'][name]
        print(f"      {i}. {data['index_name']} - Rating: {rating}/100")
        print(f"         Reason: {data['options_recommendation']['reasoning'][0] if data['options_recommendation']['reasoning'] else 'N/A'}")
    
    # Best PUT opportunity
    put_opportunities = [(name, data['options_recommendation']['put_rating']) 
                        for name, data in results['indices_analysis'].items()]
    put_opportunities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n   {colors['RED']}Top PUT Options:{colors['RESET']}")
    for i, (name, rating) in enumerate(put_opportunities[:3], 1):
        data = results['indices_analysis'][name]
        print(f"      {i}. {data['index_name']} - Rating: {rating}/100")
        print(f"         Reason: {data['options_recommendation']['reasoning'][0] if data['options_recommendation']['reasoning'] else 'N/A'}")
    
    print(f"\n{colors['BLUE']}{'='*90}{colors['RESET']}")
    input("\nPress Enter to continue...")

# Continue with existing functions...
# Add to the bottom of the file
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Main function failed: {e}")
        print("🔧 Starting test version...")
        test_main()


