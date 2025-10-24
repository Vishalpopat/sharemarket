"""
F&O Scanner Menu System
Interactive menu for scanning F&O instruments for technical breakout patterns
"""

import sys
from typing import List, Optional
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fno_breakout_detector import (
    FNOBreakoutDetector, 
    BreakoutType, 
    BreakoutSignal,
    format_breakout_report
)
from data.fno_stocks_fetcher import FNOStocksFetcher


class FNOScannerMenu:
    """Interactive menu for F&O breakout scanning"""
    
    def __init__(self):
        self.detector = FNOBreakoutDetector()
        self.fetcher = FNOStocksFetcher()
        self.fno_symbols = []
        
        # Try to load existing FNO list
        self.load_fno_stocks()
    
    def load_fno_stocks(self):
        """Load F&O stocks from file or fetch fresh"""
        stocks = self.fetcher.load_from_file()
        if stocks:
            self.fno_symbols = stocks
        else:
            print("\nNo cached F&O list found. Fetching fresh data...")
            self.update_fno_stocks()
    
    def update_fno_stocks(self):
        """Fetch and update F&O stocks list"""
        print("\nUpdating F&O stocks list from 5paisa...")
        stocks = self.fetcher.fetch_fno_stocks()
        if stocks:
            self.fetcher.save_to_file()
            self.fno_symbols = stocks
            print(f"✓ Updated F&O list: {len(stocks)} stocks")
        else:
            print("✗ Failed to update F&O list")
    
    def display_main_menu(self):
        """Display main scanner menu"""
        print("\n" + "="*80)
        print("F&O TECHNICAL PATTERN SCANNER")
        print("="*80)
        print("\n1. Bollinger Bands Breakout")
        print("   a. Bullish Breakout")
        print("   b. Bearish Breakout")
        print("\n2. Momentum Breakout")
        print("   a. Bullish Momentum")
        print("   b. Bearish Momentum")
        print("\n3. MACD Signals")
        print("   a. Bullish Crossover")
        print("   b. Bearish Crossover")
        print("\n4. Scan All Patterns")
        print("5. Configure Scanner Settings")
        print("6. Set Symbol Watchlist")
        print("0. Exit")
        print("\n" + "="*80)
    
    def bollinger_breakout_menu(self):
        """Bollinger Bands breakout submenu"""
        print("\n" + "-"*60)
        print("BOLLINGER BANDS BREAKOUT SCANNER")
        print("-"*60)
        print("\n1. Bullish Breakout (Price breaks above upper band)")
        print("2. Bearish Breakout (Price breaks below lower band)")
        print("3. Both Bullish and Bearish")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return [BreakoutType.BOLLINGER_BULLISH]
        elif choice == '2':
            return [BreakoutType.BOLLINGER_BEARISH]
        elif choice == '3':
            return [BreakoutType.BOLLINGER_BULLISH, BreakoutType.BOLLINGER_BEARISH]
        return None
    
    def momentum_breakout_menu(self):
        """Momentum breakout submenu"""
        print("\n" + "-"*60)
        print("MOMENTUM BREAKOUT SCANNER")
        print("-"*60)
        print("\n1. Bullish Momentum Breakout")
        print("2. Bearish Momentum Breakout")
        print("3. Both Bullish and Bearish")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return [BreakoutType.MOMENTUM_BULLISH]
        elif choice == '2':
            return [BreakoutType.MOMENTUM_BEARISH]
        elif choice == '3':
            return [BreakoutType.MOMENTUM_BULLISH, BreakoutType.MOMENTUM_BEARISH]
        return None
    
    def macd_signal_menu(self):
        """MACD signal submenu"""
        print("\n" + "-"*60)
        print("MACD CROSSOVER SCANNER")
        print("-"*60)
        print("\n1. Bullish Crossover (MACD crosses above signal)")
        print("2. Bearish Crossover (MACD crosses below signal)")
        print("3. Both Bullish and Bearish")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return [BreakoutType.MACD_BULLISH]
        elif choice == '2':
            return [BreakoutType.MACD_BEARISH]
        elif choice == '3':
            return [BreakoutType.MACD_BULLISH, BreakoutType.MACD_BEARISH]
        return None
    
    def configure_settings_menu(self):
        """Configure scanner settings"""
        print("\n" + "-"*60)
        print("SCANNER CONFIGURATION")
        print("-"*60)
        print(f"\nCurrent Settings:")
        print(f"1. Bollinger Bands Period: {self.detector.bb_period}")
        print(f"2. Bollinger Bands Std Dev: {self.detector.bb_std}")
        print(f"3. Momentum Period: {self.detector.momentum_period}")
        print(f"4. MACD Fast: {self.detector.macd_fast}")
        print(f"5. MACD Slow: {self.detector.macd_slow}")
        print(f"6. MACD Signal: {self.detector.macd_signal}")
        print("7. Reset to Defaults")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect setting to modify (0 to go back): ").strip()
        
        if choice == '1':
            period = int(input("Enter Bollinger Bands period: "))
            self.detector.bb_period = period
        elif choice == '2':
            std = float(input("Enter Bollinger Bands std dev: "))
            self.detector.bb_std = std
        elif choice == '3':
            period = int(input("Enter Momentum period: "))
            self.detector.momentum_period = period
        elif choice == '4':
            fast = int(input("Enter MACD fast period: "))
            self.detector.macd_fast = fast
        elif choice == '5':
            slow = int(input("Enter MACD slow period: "))
            self.detector.macd_slow = slow
        elif choice == '6':
            signal = int(input("Enter MACD signal period: "))
            self.detector.macd_signal = signal
        elif choice == '7':
            self.detector = FNOBreakoutDetector()
            print("Settings reset to defaults.")
    
    def set_watchlist_menu(self):
        """Set symbol watchlist"""
        print("\n" + "-"*60)
        print("SYMBOL WATCHLIST")
        print("-"*60)
        print("\nCurrent watchlist:")
        if self.fno_symbols:
            for i, symbol in enumerate(self.fno_symbols[:20], 1):
                print(f"{i:2d}. {symbol}")
            if len(self.fno_symbols) > 20:
                print(f"... and {len(self.fno_symbols) - 20} more ({len(self.fno_symbols)} total)")
        else:
            print("No symbols in watchlist")
        
        print("\nOptions:")
        print("1. Add symbols")
        print("2. Remove symbols")
        print("3. Clear watchlist")
        print("4. Load all F&O stocks")
        print("5. Update F&O stocks from web")
        print("6. Load from file")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            symbols = input("Enter symbols (comma-separated): ").strip()
            new_symbols = [s.strip().upper() for s in symbols.split(',')]
            self.fno_symbols.extend(new_symbols)
            self.fno_symbols = sorted(list(set(self.fno_symbols)))
            print(f"✓ Added {len(new_symbols)} symbols")
        elif choice == '2':
            symbol = input("Enter symbol to remove: ").strip().upper()
            if symbol in self.fno_symbols:
                self.fno_symbols.remove(symbol)
                print(f"✓ Removed {symbol}")
        elif choice == '3':
            self.fno_symbols.clear()
            print("✓ Watchlist cleared")
        elif choice == '4':
            self.load_fno_stocks()
            print(f"✓ Loaded {len(self.fno_symbols)} F&O stocks")
        elif choice == '5':
            self.update_fno_stocks()
        elif choice == '6':
            filename = input("Enter filename: ").strip()
            stocks = self.fetcher.load_from_file(filename)
            if stocks:
                self.fno_symbols = stocks
    
    def scan_patterns(self, pattern_types: Optional[List[BreakoutType]] = None):
        """Execute pattern scan"""
        if not self.fno_symbols:
            print("\nNo symbols in watchlist. Please add symbols first.")
            return
        
        print(f"\nScanning {len(self.fno_symbols)} symbols...")
        all_signals = []
        
        # This is where you'd integrate with your data fetching service
        # For now, showing the structure
        for symbol in self.fno_symbols:
            try:
                # df = fetch_historical_data(symbol)  # Your data fetching function
                # signals = self.detector.scan_all_patterns(df, symbol)
                # if pattern_types:
                #     signals = self.detector.filter_by_type(signals, pattern_types)
                # all_signals.extend(signals)
                pass
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        # Display results
        if all_signals:
            print(format_breakout_report(all_signals))
            
            # Option to export
            export = input("\nExport results to file? (y/n): ").strip().lower()
            if export == 'y':
                filename = input("Enter filename: ").strip()
                with open(filename, 'w') as f:
                    f.write(format_breakout_report(all_signals))
                print(f"Results exported to {filename}")
        else:
            print("\nNo breakout signals detected.")
    
    def run(self):
        """Main menu loop"""
        while True:
            self.display_main_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '0':
                print("\nExiting F&O Scanner. Goodbye!")
                break
            elif choice == '1':
                patterns = self.bollinger_breakout_menu()
                if patterns:
                    self.scan_patterns(patterns)
            elif choice == '2':
                patterns = self.momentum_breakout_menu()
                if patterns:
                    self.scan_patterns(patterns)
            elif choice == '3':
                patterns = self.macd_signal_menu()
                if patterns:
                    self.scan_patterns(patterns)
            elif choice == '4':
                self.scan_patterns()  # Scan all patterns
            elif choice == '5':
                self.configure_settings_menu()
            elif choice == '6':
                self.set_watchlist_menu()
            else:
                print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    scanner = FNOScannerMenu()
    scanner.run()
