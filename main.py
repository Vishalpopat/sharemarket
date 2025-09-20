"""
Main entry point for the Indian Stock Market Analysis Tool
"""

import sys
import os
from datetime import datetime

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
        print("5. Market Overview")
        print("6. Bulk Analysis (All Nifty 50)")
        print("7. Intraday Ideas (User Symbols)")
        print("8. Swing Ideas (User Symbols)")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            print("\n📈 INTRADAY TRADING ANALYSIS")
            print("-" * 40)
            strategy = IntradayStrategy()
            recommendations = market_service.analyze_stocks(
                nifty_50_stocks[:5], strategy
            )
            display_recommendations(recommendations, "Intraday")
            
        elif choice == '2':
            print("\n📊 SWING TRADING ANALYSIS")
            print("-" * 40)
            strategy = SwingTradingStrategy()
            recommendations = market_service.analyze_stocks(
                nifty_50_stocks[:5], strategy
            )
            display_recommendations(recommendations, "Swing")
            
        elif choice == '3':
            symbols = input("Enter stock symbols (comma-separated, e.g., RELIANCE.NS,TCS.NS): ").strip()
            if symbols:
                stock_list = [s.strip().upper() for s in symbols.split(',')]
                # Add .NS if not present
                stock_list = [s if s.endswith('.NS') else f"{s}.NS" for s in stock_list]
                strategy_type = input("Enter strategy (intraday/swing): ").strip().lower()
                
                if strategy_type == 'intraday':
                    strategy = IntradayStrategy()
                else:
                    strategy = SwingTradingStrategy()
                
                recommendations = market_service.analyze_stocks(stock_list, strategy)
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
                recommendations = market_service.analyze_stocks(sector_stocks[sector_choice], strategy)
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
            recommendations = market_service.analyze_stocks(nifty_50_stocks, strategy)
            
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
                recommendations = market_service.analyze_stocks(user_stocks, strategy)
                display_recommendations(recommendations, "Intraday Ideas")
            
        elif choice == '8':
            # Swing Ideas with User Choice
            print("\n📊 SWING IDEAS - USER SYMBOLS")
            print("-" * 40)
            user_stocks = get_user_stock_choice()
            if user_stocks:
                strategy = SwingTradingStrategy()
                recommendations = market_service.analyze_stocks(user_stocks, strategy)
                display_recommendations(recommendations, "Swing Ideas")
            
        elif choice == '9':
            print("\nThank you for using Indian Stock Market Analysis Tool!")
            logger.info("Application terminated by user")
            break
            
        else:
            print("Invalid choice! Please select 1-9.")

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

if __name__ == "__main__":
    main()
