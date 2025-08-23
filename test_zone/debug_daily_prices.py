"""
Debug script to show the daily closing prices being used for DMA calculation
"""

import sys
import os

# Add parent directory to path for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)

from rsi_config import CONFIG
from tradingview_dma import get_daily_data_from_existing

# Get symbol configuration
symbol = 'RELIANCE'
instrument_key = CONFIG['symbols'][symbol]

# Get daily data
daily_closes, daily_dates = get_daily_data_from_existing(instrument_key)

if daily_closes and daily_dates:
    print(f"Daily closing prices for {symbol}:")
    print("Date\t\tClose Price")
    print("-" * 30)
    
    for i, (date, price) in enumerate(zip(daily_dates, daily_closes)):
        print(f"{date}\t{price:.2f}")
    
    print(f"\nTotal daily closes: {len(daily_closes)}")
    
    # Calculate DMA manually for verification
    if len(daily_closes) >= 10:
        dma_10 = sum(daily_closes[-10:]) / 10
        print(f"\nManual DMA-10 calculation:")
        print(f"Last 10 prices: {[f'{p:.2f}' for p in daily_closes[-10:]]}")
        print(f"DMA-10: {dma_10:.2f}")
    
    if len(daily_closes) >= 20:
        dma_20 = sum(daily_closes[-20:]) / 20
        print(f"\nManual DMA-20 calculation:")
        print(f"DMA-20: {dma_20:.2f}")
        
else:
    print("No daily data available")