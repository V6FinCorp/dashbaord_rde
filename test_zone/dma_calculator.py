"""
Displaced Moving Average (DMA) Calculator
Calculates DMA for periods 10, 20, 50, 100, and 200
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
import sys
import os

# Add parent directory to path for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)

from rsi_config import CONFIG

def get_candle_data(instrument_key, timeframe=15):
    """Get combined historical and intraday data for DMA calculation."""
    safe_key = instrument_key.replace('|', '%7C')
    
    # Calculate dates - get last 30 days to ensure we have enough data for 200-period DMA
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    # Get more historical data for DMA calculation (especially for DMA-200)
    hist_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/{timeframe}/{end_date}/{start_date}?size=1000'
    
    all_candles = []
    
    # Get historical data
    try:
        response = requests.get(hist_url, headers=headers)
        if response.status_code == 200:
            hist_candles = response.json().get('data', {}).get('candles', [])
            if hist_candles:
                all_candles.extend(hist_candles)
                print(f"Got {len(hist_candles)} historical candles for DMA calculation")
        else:
            print(f"Error fetching historical data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching historical data: {e}")
    
    # Get today's data (intraday)
    intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/{timeframe}'
    try:
        response = requests.get(intra_url, headers=headers)
        if response.status_code == 200:
            today_candles = response.json().get('data', {}).get('candles', [])
            if today_candles:
                all_candles.extend(today_candles)
                print(f"Got {len(today_candles)} candles for today")
        else:
            print(f"Error fetching today's data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching today's data: {e}")
    
    if not all_candles:
        print("No data available")
        return None
    
    # Sort by timestamp to ensure chronological order
    all_candles.sort(key=lambda x: x[0])
    
    return all_candles

def calculate_dma(prices, period, displacement=1):
    """
    Calculate Displaced Moving Average
    
    Args:
        prices: List of closing prices
        period: Moving average period
        displacement: Number of periods to displace (default 1)
    
    Returns:
        List of DMA values
    """
    if len(prices) < period:
        return [None] * len(prices)
    
    # Calculate simple moving average
    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(None)
        else:
            sma.append(sum(prices[i-period+1:i+1]) / period)
    
    # Displace the moving average
    dma = [None] * displacement + sma[:-displacement] if displacement > 0 else sma
    
    return dma

def format_price_change(current, previous):
    """Format price change with percentage and direction"""
    if previous is None or previous == 0:
        return f"{current:.2f} (0.00%)", "→"
    
    change = current - previous
    change_pct = (change / previous) * 100
    
    if change > 0:
        return f"{current:.2f} (+{change_pct:.2f}%)", "↑"
    elif change < 0:
        return f"{current:.2f} ({change_pct:.2f}%)", "↓"
    else:
        return f"{current:.2f} (0.00%)", "→"

def get_trend_signal(price, dma_values):
    """Get trend signal based on price vs DMA levels"""
    if not dma_values or price is None:
        return "→"
    
    above_count = sum(1 for dma in dma_values if dma and price > dma)
    total_dma = sum(1 for dma in dma_values if dma is not None)
    
    if total_dma == 0:
        return "→"
    
    ratio = above_count / total_dma
    
    if ratio >= 0.8:
        return "🟢 STRONG BULLISH"
    elif ratio >= 0.6:
        return "🔵 BULLISH"
    elif ratio >= 0.4:
        return "🟡 NEUTRAL"
    elif ratio >= 0.2:
        return "🔴 BEARISH"
    else:
        return "🔴 STRONG BEARISH"

def analyze_dma():
    """Main function to analyze DMA for the configured symbol"""
    print("Loading historical data...")
    
    # Get symbol configuration
    symbol = 'RELIANCE'  # Default symbol
    instrument_key = CONFIG['symbols'][symbol]
    
    # Get candle data
    candles = get_candle_data(instrument_key, CONFIG['timeframe'])
    if not candles:
        print(f"No data available for {symbol}")
        return
    
    print(f"Got {len(candles)} total candles for DMA calculation")
    
    # Extract closing prices and timestamps
    timestamps = [datetime.fromisoformat(candle[0].replace('+05:30', '')) for candle in candles]
    closes = [float(candle[4]) for candle in candles]  # Close price is at index 4
    volumes = [int(candle[5]) for candle in candles]   # Volume is at index 5
    
    # Calculate DMAs for different periods
    dma_periods = [10, 20, 50, 100, 200]
    dma_results = {}
    
    for period in dma_periods:
        dma_results[period] = calculate_dma(closes, period)
    
    # Get today's data for display
    today = datetime.now().date()
    today_indices = [i for i, ts in enumerate(timestamps) if ts.date() == today]
    
    if not today_indices:
        print("No data available for today, showing latest available data")
        # Show last available trading day
        latest_date = timestamps[-1].date()
        today_indices = [i for i, ts in enumerate(timestamps) if ts.date() == latest_date]
        today = latest_date
    
    # Prepare table data
    table_data = []
    headers = ["Time", "Price (% Change)", "DMA-10", "DMA-20", "DMA-50", "DMA-100", "DMA-200", "Volume", "Trend"]
    
    # Show data from start of the day or last 20 candles, whichever is less
    start_idx = max(0, today_indices[0] if today_indices else len(timestamps) - 20)
    
    for i in range(start_idx, len(timestamps)):
        ts = timestamps[i]
        price = closes[i]
        volume = volumes[i]
        
        # Format price change
        prev_price = closes[i-1] if i > 0 else None
        price_str, direction = format_price_change(price, prev_price)
        
        # Get DMA values
        dma_vals = []
        current_dma_values = []
        for period in dma_periods:
            dma_val = dma_results[period][i]
            if dma_val is not None:
                dma_vals.append(f"{dma_val:.2f}")
                current_dma_values.append(dma_val)
            else:
                dma_vals.append("-")
        
        # Get trend signal
        trend = get_trend_signal(price, current_dma_values)
        
        # Mark current time
        time_str = ts.strftime("%H:%M")
        if i == len(timestamps) - 1:
            time_str += " 🔵"
        
        # Format volume
        volume_str = f"{volume:,}"
        
        row = [time_str, f"{direction} {price_str}"] + dma_vals + [volume_str, trend]
        table_data.append(row)
    
    # Display results
    print(f"\n{symbol} (NSE) - DMA Analysis - {today}")
    print(f"Timeframe: {CONFIG['timeframe']} minutes | Session: 9:15 AM - 3:30 PM")
    print("\nDisplaced Moving Averages (DMA):")
    
    # Print table
    print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="center", stralign="center"))
    
    # Summary
    current_price = closes[-1]
    current_dma_vals = [dma_results[period][-1] for period in dma_periods if dma_results[period][-1] is not None]
    
    print(f"\nSummary:")
    print(f"Current Price: ₹{current_price:.2f}")
    print(f"Overall Trend: {get_trend_signal(current_price, current_dma_vals)}")
    
    # DMA levels
    print(f"\nCurrent DMA Levels:")
    for period in dma_periods:
        dma_val = dma_results[period][-1]
        if dma_val is not None:
            diff = current_price - dma_val
            diff_pct = (diff / dma_val) * 100
            status = "Above" if diff > 0 else "Below" if diff < 0 else "At"
            print(f"DMA-{period}: ₹{dma_val:.2f} ({status} by {abs(diff_pct):.2f}%)")
        else:
            print(f"DMA-{period}: Not enough data")

if __name__ == "__main__":
    analyze_dma()