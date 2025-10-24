# Indian Stock Market Analysis Tool

A comprehensive, modular tool for Indian stock market analysis with predictions for intraday and swing trading strategies.

## Features

- **Multi-Strategy Analysis**: Supports both intraday and swing trading strategies
- **Modular Architecture**: Clean, extensible design using Strategy and Factory patterns
- **Indian Market Focus**: Optimized for NSE/BSE stocks with Indian market specifics
- **Technical Analysis**: Multiple technical indicators and chart patterns
- **Risk Management**: Built-in risk assessment and position sizing
- **Real-time Data**: Integration with market data providers
- **Backtesting**: Historical performance analysis


## Project Structure

```
src/
├── core/                   # Core business logic
│   ├── strategies/         # Trading strategies
│   ├── indicators/         # Technical indicators
│   ├── analyzers/          # Market analyzers
│   └── patterns/           # Chart patterns
├── data/                   # Data layer
│   ├── providers/          # Data source providers
│   ├── repositories/       # Data repositories
│   └── models/             # Data models
├── services/               # Business services
├── utils/                  # Utility functions
└── config/                 # Configuration
```

## Installation
Prerequisite:
Install Python

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Alternatively for virtualenv of python
   ```bash
   virtualenv venv --python=python3.10
   .\venv\Scripts\pip.exe install -r .\requirements.txt
   ```
3. Configure your data sources in `config/settings.py`
4. Run the application:
   ```bash
   python main.py
   ```
   
   Alternatively for virtualenv of python:
   ```bash
   .\venv\Scripts\python .\main.py
   ```


## Configuration

Edit `config/settings.py` to configure:
- Data providers (Yahoo Finance, NSE API, etc.)
- Trading parameters
- Risk management settings
- Strategy parameters

## Usage Examples

### Intraday Analysis
```python
from src.core.strategies import IntradayStrategy
from src.services.market_service import MarketService

strategy = IntradayStrategy()
service = MarketService()
recommendations = service.analyze_stocks(['RELIANCE', 'TCS', 'INFY'], strategy)
```

### Swing Trading Analysis
```python
from src.core.strategies import SwingTradingStrategy
from src.services.market_service import MarketService

strategy = SwingTradingStrategy()
service = MarketService()
recommendations = service.analyze_stocks(['HDFC', 'ICICIBANK'], strategy)
```

## Supported Indicators

- Moving Averages (SMA, EMA, WMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Volume indicators
- Support/Resistance levels

## Risk Management

- Position sizing based on portfolio percentage
- Stop-loss recommendations
- Risk-reward ratio calculations
- Maximum drawdown limits

## Data Sources

- Yahoo Finance (Free)
- NSE Official API
- BSE API
- Alpha Vantage
- Custom data providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Disclaimer

This tool is for educational and research purposes only. Past performance does not guarantee future results. Always consult with a financial advisor before making investment decisions.

## License

MIT License
