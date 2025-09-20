"""
Colorful tabular display utility for Windows terminals
"""
import os
import platform

def enable_windows_colors():
    """Enable ANSI color support in Windows terminal"""
    if platform.system() == "Windows":
        try:
            # Enable ANSI escape sequences in Windows 10+
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            return False
    return True

def get_colors():
    """Get color codes with fallback for unsupported terminals"""
    if enable_windows_colors():
        return {
            'BUY': '\033[92m',     # Green
            'SELL': '\033[91m',    # Red  
            'HOLD': '\033[93m',    # Yellow
            'RESET': '\033[0m',    # Reset color
            'BOLD': '\033[1m',     # Bold
            'CYAN': '\033[96m',    # Cyan for headers
            'BLUE': '\033[94m',    # Blue for borders
            'MAGENTA': '\033[95m'  # Magenta for strategy type
        }
    else:
        # Fallback to no colors
        return {
            'BUY': '', 'SELL': '', 'HOLD': '', 'RESET': '',
            'BOLD': '', 'CYAN': '', 'BLUE': '', 'MAGENTA': ''
        }

def create_table_display(recommendations, strategy_type):
    """Create a beautiful table display with colors"""
    colors = get_colors()
    
    if not recommendations:
        print("No recommendations available at this time.")
        return
    
    print(f"\n{colors['MAGENTA']}{colors['BOLD']}🎯 {strategy_type.upper()} TRADING RECOMMENDATIONS{colors['RESET']}")
    print(f"{colors['BLUE']}{'='*130}{colors['RESET']}")
    
    # Enhanced table with profit/loss calculations
    headers = [
        "No.", "Symbol", "Action", "Price", "Target", "Target%", 
        "Stop Loss", "Stop%", "R:R", "Confidence", "Potential P/L", "Signals"
    ]
    
    # Column widths
    widths = [3, 10, 6, 8, 8, 7, 9, 7, 4, 9, 12, 30]
    
    # Print header
    header_line = f"{colors['CYAN']}{colors['BOLD']}"
    for i, header in enumerate(headers):
        header_line += f"{header:<{widths[i]}} "
    header_line += f"{colors['RESET']}"
    print(header_line)
    
    # Print separator
    separator = f"{colors['BLUE']}"
    for width in widths:
        separator += "─" * width + " "
    separator += f"{colors['RESET']}"
    print(separator)
    
    # Track summary stats
    total_potential_profit = 0
    total_potential_loss = 0
    
    # Print data rows
    for i, rec in enumerate(recommendations, 1):
        symbol_clean = rec['symbol'].replace('.NS', '')
        action = rec['action']
        current_price = rec['current_price']
        target = rec['target']
        stop_loss = rec['stop_loss']
        confidence = rec['confidence']
        reason = rec['reason'][:27] + "..." if len(rec['reason']) > 30 else rec['reason']
        
        # Calculate percentages and P/L
        target_pct = ((target / current_price - 1) * 100)
        stop_pct = ((stop_loss / current_price - 1) * 100)
        risk_reward = rec.get('risk_reward', 1.0)
        
        # Calculate potential profit/loss per share
        if action == 'BUY':
            potential_profit = target - current_price
            potential_loss = current_price - stop_loss
            pl_text = f"+{potential_profit:.0f}/-{potential_loss:.0f}"
        elif action == 'SELL':
            potential_profit = current_price - target
            potential_loss = stop_loss - current_price
            pl_text = f"+{potential_profit:.0f}/-{potential_loss:.0f}"
        else:
            potential_profit = abs(target - current_price)
            potential_loss = abs(current_price - stop_loss)
            pl_text = f"±{potential_profit:.0f}/±{potential_loss:.0f}"
        
        total_potential_profit += potential_profit
        total_potential_loss += potential_loss
        
        # Choose colors and symbols
        if action == 'BUY':
            action_color = colors['BUY']
            action_symbol = "🟢"
        elif action == 'SELL':
            action_color = colors['SELL'] 
            action_symbol = "🔴"
        else:
            action_color = colors['HOLD']
            action_symbol = "🟡"
        
        # Confidence color coding
        if confidence >= 70:
            conf_color = colors['BUY']
        elif confidence >= 50:
            conf_color = colors['HOLD']
        else:
            conf_color = colors['SELL']
        
        # Create row with proper formatting
        row_data = [
            f"{i}",
            f"{colors['BOLD']}{symbol_clean}{colors['RESET']}",
            f"{action_color}{action_symbol}{action}{colors['RESET']}",
            f"₹{current_price:.0f}",
            f"₹{target:.0f}",
            f"{target_pct:+.1f}%",
            f"₹{stop_loss:.0f}",
            f"{stop_pct:+.1f}%", 
            f"{risk_reward:.1f}",
            f"{conf_color}{confidence:.0f}%{colors['RESET']}",
            f"{action_color}{pl_text}{colors['RESET']}",
            f"{reason}"
        ]
        
        # Print formatted row
        row_line = ""
        for j, data in enumerate(row_data):
            # Handle ANSI codes in width calculation
            display_width = len(data.encode().decode('unicode_escape')) if '\033' not in data else len(data.replace('\033[92m', '').replace('\033[91m', '').replace('\033[93m', '').replace('\033[0m', '').replace('\033[1m', '').replace('\033[96m', ''))
            row_line += f"{data:<{widths[j]}} "
        print(row_line)
    
    # Print footer with summary
    print(f"{colors['BLUE']}{'-'*130}{colors['RESET']}")
    
    # Action counts
    buy_count = sum(1 for r in recommendations if r['action'] == 'BUY')
    sell_count = sum(1 for r in recommendations if r['action'] == 'SELL')
    hold_count = sum(1 for r in recommendations if r['action'] == 'HOLD')
    avg_confidence = sum(r['confidence'] for r in recommendations) / len(recommendations)
    
    summary_stats = f"{colors['BOLD']}📊 Summary: "
    summary_stats += f"{colors['BUY']}BUY: {buy_count} "
    summary_stats += f"{colors['SELL']}SELL: {sell_count} "
    summary_stats += f"{colors['HOLD']}HOLD: {hold_count} "
    summary_stats += f"{colors['CYAN']}| Avg Confidence: {avg_confidence:.1f}% "
    summary_stats += f"| Total P/L Range: +₹{total_potential_profit:.0f}/-₹{total_potential_loss:.0f}"
    summary_stats += f"{colors['RESET']}"
    
    print(f"\n{summary_stats}")
    
    print(f"\n{colors['BLUE']}{'='*130}{colors['RESET']}")
    print(f"{colors['BOLD']}⚠️  Educational purposes only. Do your own research before trading.{colors['RESET']}")

if __name__ == "__main__":
    # Test the color functionality
    colors = get_colors()
    print(f"{colors['BUY']}Green text test{colors['RESET']}")
    print(f"{colors['SELL']}Red text test{colors['RESET']}")
    print(f"{colors['HOLD']}Yellow text test{colors['RESET']}")
    print("Color test completed!")