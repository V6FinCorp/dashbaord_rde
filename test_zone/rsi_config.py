# RSI Scanner Configuration

CONFIG = {
    # Symbols to scan with their instrument keys
    'symbols': {
        'RELIANCE': 'NSE_EQ|INE002A01018',
        'TCS': 'NSE_EQ|INE467B01029',
        'HDFCBANK': 'NSE_EQ|INE040A01034',
        'INFY': 'NSE_EQ|INE009A01021',
        'ICICIBANK': 'NSE_EQ|INE090A01021'
    },
    
    # Timeframe in minutes (1, 3, 5, 10, 15, 30, 60)
    'timeframe': 15,
    
    # RSI parameters
    'rsi_period': 14,        # RSI lookback period
    'rsi_threshold': 70,     # Alert when RSI crosses above this value
    
    # Scanner settings
    'use_intraday': True,    # True to use intraday data, False for historical
    'scan_interval': 30      # Seconds between each scan
}