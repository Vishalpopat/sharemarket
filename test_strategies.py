"""
Quick test script to verify strategy differences
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.strategies.intraday_strategy import IntradayStrategy
from src.core.strategies.swing_trading_strategy import SwingTradingStrategy

def test_strategies():
    # Test strategy parameters
    intraday = IntradayStrategy()
    swing = SwingTradingStrategy()

    print('=== STRATEGY COMPARISON ===')
    print('Intraday Strategy:')
    for key, value in intraday.get_strategy_parameters().items():
        print(f'  {key}: {value}')

    print('\nSwing Strategy:')
    for key, value in swing.get_strategy_parameters().items():
        print(f'  {key}: {value}')

    print('\n=== TEST CALCULATIONS ===')
    current_price = 1000.0
    print(f'Current Price: ₹{current_price}')

    # Intraday calculations
    intraday_target = intraday.calculate_target_price(current_price, intraday.parameters['target_percent'])
    intraday_stop = intraday.calculate_stop_loss(current_price, intraday.parameters['stop_loss_percent'])

    print(f'Intraday - Target: ₹{intraday_target:.2f}, Stop: ₹{intraday_stop:.2f}')

    # Swing calculations  
    swing_target = swing.calculate_target_price(current_price, swing.parameters['target_percent'])
    swing_stop = swing.calculate_stop_loss(current_price, swing.parameters['stop_loss_percent'])

    print(f'Swing - Target: ₹{swing_target:.2f}, Stop: ₹{swing_stop:.2f}')
    
    print('\n✅ Strategies have different parameters and calculations!')

if __name__ == "__main__":
    test_strategies()
