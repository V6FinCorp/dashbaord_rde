"""
Daily Moving Average (DMA) Calculator - TradingView Compatible
Calculates DMA using daily closing prices (like TradingView)
Displays hourly data for last 5 working days
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

def get_daily_data_from_existing(instrument_key):
    """Extract daily closing prices from existing data - enhanced for longer periods"""
    safe_key = instrument_key.replace('|', '%7C')
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    all_candles = []
    
    # Method 1: Get recent data with 15-minute intervals (last 30 days)
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date_recent = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    
    hist_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/15/{end_date}/{start_date_recent}?size=1000'
    
    try:
        response = requests.get(hist_url, headers=headers)
        if response.status_code == 200:
            hist_candles = response.json().get('data', {}).get('candles', [])
            if hist_candles:
                all_candles.extend(hist_candles)
                print(f"Got {len(hist_candles)} recent candles (15min)")
    except Exception as e:
        print(f"Error fetching recent data: {e}")
    
    # Method 2: Get older data with 4-hour intervals (30-90 days back)
    start_date_old = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    start_date_mid = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    
    hist_url_old = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/240/{start_date_mid}/{start_date_old}?size=500'
    
    try:
        response = requests.get(hist_url_old, headers=headers)
        if response.status_code == 200:
            old_candles = response.json().get('data', {}).get('candles', [])
            if old_candles:
                all_candles.extend(old_candles)
                print(f"Got {len(old_candles)} older candles (240min)")
    except Exception as e:
        print(f"Error fetching older data: {e}")
    
    # Get today's data (intraday)
    intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/15'
    try:
        response = requests.get(intra_url, headers=headers)
        if response.status_code == 200:
            today_candles = response.json().get('data', {}).get('candles', [])
            if today_candles:
                all_candles.extend(today_candles)
                print(f"Got {len(today_candles)} candles for today")
    except Exception as e:
        print(f"Error fetching today's data: {e}")
    
    if not all_candles:
        print("No data available")
        return None, None
    
    # Sort by timestamp
    all_candles.sort(key=lambda x: x[0])
    print(f"Total candles before processing: {len(all_candles)}")
    
    # Extract daily closing prices (last candle of each trading day)
    daily_closes = []
    daily_dates = []
    current_date = None
    last_candle_of_day = None
    
    for candle in all_candles:
        timestamp = datetime.fromisoformat(candle[0].replace('+05:30', ''))
        candle_date = timestamp.date()
        
        # Skip weekends
        if candle_date.weekday() >= 5:
            continue
        
        # If it's a new trading day
        if current_date != candle_date:
            # Save the previous day's closing price
            if current_date is not None and last_candle_of_day is not None:
                daily_closes.append(float(last_candle_of_day[4]))  # Close price
                daily_dates.append(current_date.strftime('%Y-%m-%d'))
            
            # Start tracking the new day
            current_date = candle_date
            last_candle_of_day = candle
        else:
            # Keep updating with the latest candle of the day (prefer market close time)
            if timestamp.hour >= 15:  # Prefer candles closer to market close (3:30 PM)
                last_candle_of_day = candle
            elif last_candle_of_day is None:
                last_candle_of_day = candle
    
    # Don't forget the last day
    if current_date is not None and last_candle_of_day is not None:
        daily_closes.append(float(last_candle_of_day[4]))
        daily_dates.append(current_date.strftime('%Y-%m-%d'))
    
    print(f"Extracted {len(daily_closes)} daily closing prices")
    
    # Show date range
    if daily_dates:
        print(f"Date range: {daily_dates[0]} to {daily_dates[-1]}")
    
    return daily_closes, daily_dates

def get_hourly_data_from_existing(instrument_key):
    """Get hourly data using the same method as RSI script"""
    safe_key = instrument_key.replace('|', '%7C')
    
    # Get last 7 days of data to ensure 5 working days
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    # Get 60-minute data
    hourly_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/60/{end_date}/{start_date}?size=200'
    
    hourly_candles = []
    
    try:
        response = requests.get(hourly_url, headers=headers)
        if response.status_code == 200:
            hourly_candles = response.json().get('data', {}).get('candles', [])
            if hourly_candles:
                print(f"Got {len(hourly_candles)} hourly candles")
        else:
            print(f"Error fetching hourly data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching hourly data: {e}")
    
    # Get today's hourly data
    intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/60'
    try:
        response = requests.get(intra_url, headers=headers)
        if response.status_code == 200:
            today_hourly = response.json().get('data', {}).get('candles', [])
            if today_hourly:
                hourly_candles.extend(today_hourly)
                print(f"Got {len(today_hourly)} hourly candles for today")
        else:
            print(f"Error fetching today's hourly data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching today's hourly data: {e}")
    
    if not hourly_candles:
        print("No hourly data available")
        return None
    
    # Sort by timestamp
    hourly_candles.sort(key=lambda x: x[0])
    
    return hourly_candles

def calculate_sma(prices, period):
    """Calculate Simple Moving Average (SMA) - same as TradingView"""
    if len(prices) < period:
        return [None] * len(prices)
    
    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(None)
        else:
            sma.append(sum(prices[i-period+1:i+1]) / period)
    
    return sma

def get_dma_for_date(daily_closes, daily_dates, target_date, period):
    """Get DMA value for a specific date using daily data"""
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    # Find the index of the target date or the closest previous date
    target_index = None
    for i, date_str in enumerate(daily_dates):
        if date_str <= target_date_str:
            target_index = i
        else:
            break
    
    if target_index is None or target_index < period - 1:
        return None
    
    # Calculate SMA for the target date
    return sum(daily_closes[target_index-period+1:target_index+1]) / period

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

def analyze_tradingview_dma():
    """Main function to analyze DMA like TradingView"""
    print("Loading data for TradingView-compatible DMA analysis...")
    
    # Get symbol configuration
    symbol = 'RELIANCE'
    instrument_key = CONFIG['symbols'][symbol]
    
    # Get daily data for DMA calculation
    daily_closes, daily_dates = get_daily_data_from_existing(instrument_key)
    if not daily_closes:
        print(f"No daily data available for {symbol}")
        return
    
    # Get hourly data for display
    hourly_candles = get_hourly_data_from_existing(instrument_key)
    if not hourly_candles:
        print(f"No hourly data available for {symbol}")
        return
    
    # Extract daily closing prices and dates
    print(f"Using {len(daily_closes)} daily closing prices for DMA calculation")
    print(f"Displaying {len(hourly_candles)} hourly candles")
    
    # Prepare table data with simplified format - include DMA-50 if available
    table_data = []
    
    # Determine which DMAs we can calculate
    available_dmas = []
    if len(daily_closes) >= 10:
        available_dmas.append(10)
    if len(daily_closes) >= 20:
        available_dmas.append(20)
    if len(daily_closes) >= 50:
        available_dmas.append(50)
    if len(daily_closes) >= 100:
        available_dmas.append(100)
    if len(daily_closes) >= 200:
        available_dmas.append(200)
    
    print(f"Available DMAs with {len(daily_closes)} days of data: {available_dmas}")
    
    # Build headers dynamically
    headers = ["Timestamp", "Code", "Last Price"]
    for dma in available_dmas:
        headers.extend([f"DMA-{dma}", f"DMA-{dma} Diff"])
    
    # Filter hourly data to last 5 working days
    current_date = datetime.now()
    five_days_ago = current_date - timedelta(days=7)  # 7 days to ensure 5 working days
    
    filtered_hourly = []
    for candle in hourly_candles:
        candle_date = datetime.fromisoformat(candle[0].replace('+05:30', ''))
        if candle_date >= five_days_ago:
            filtered_hourly.append(candle)
    
    # Sort hourly data
    filtered_hourly.sort(key=lambda x: x[0])
    
    for i, candle in enumerate(filtered_hourly):
        timestamp_str = candle[0]
        timestamp = datetime.fromisoformat(timestamp_str.replace('+05:30', ''))
        price = float(candle[4])  # Close price
        
        # Skip non-trading hours (before 9:15 AM or after 3:30 PM)
        if timestamp.hour < 9 or (timestamp.hour == 9 and timestamp.minute < 15) or timestamp.hour >= 16:
            continue
        
        # Format timestamp
        timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M")
        
        # Start building row
        row = [timestamp_formatted, symbol, f"₹{price:.2f}"]
        
        # Calculate DMA values and differences for available periods
        for period in available_dmas:
            dma_val = get_dma_for_date(daily_closes, daily_dates, timestamp, period)
            
            if dma_val is not None:
                dma_str = f"{dma_val:.2f}"
                diff = price - dma_val
                diff_pct = (diff / dma_val) * 100
                if diff > 0:
                    diff_str = f"+{diff:.2f} (+{diff_pct:.2f}%)"
                elif diff < 0:
                    diff_str = f"{diff:.2f} ({diff_pct:.2f}%)"
                else:
                    diff_str = "0.00 (0.00%)"
            else:
                dma_str = "-"
                diff_str = "-"
            
            row.extend([dma_str, diff_str])
        
        table_data.append(row)
    
    # Display results
    print(f"\n{symbol} DMA Analysis - Last 5 Working Days")
    print("DMA calculated using Daily closing prices (TradingView compatible)")
    print(f"Total records: {len(table_data)}")
    
    # Print table
    print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="center", stralign="center"))
    
    # Current summary
    if table_data:
        latest_row = table_data[-1]
        print(f"\nLatest Data:")
        print(f"Timestamp: {latest_row[0]}")
        print(f"Code: {latest_row[1]}")
        print(f"Last Price: {latest_row[2]}")
        
        # Display available DMA values and differences
        col_index = 3
        for dma in available_dmas:
            if col_index < len(latest_row) - 1:
                print(f"DMA-{dma}: {latest_row[col_index]} | Difference: {latest_row[col_index + 1]}")
                col_index += 2

if __name__ == "__main__":
    analyze_tradingview_dma()