"""
Exponential Moving Average (EMA) Calculator
Calculates EMA for periods 9 and 15 using TradingView-compatible formula
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

def get_historical_data(instrument_key):
    """Get historical data for EMA calculation"""
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
    
    # Method 2: Get older data with hourly intervals for more history
    start_date_old = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    start_date_mid = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    
    hist_url_old = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/60/{start_date_mid}/{start_date_old}?size=1000'
    
    try:
        response = requests.get(hist_url_old, headers=headers)
        if response.status_code == 200:
            old_candles = response.json().get('data', {}).get('candles', [])
            if old_candles:
                all_candles.extend(old_candles)
                print(f"Got {len(old_candles)} older candles (60min)")
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
        return None
    
    # Sort by timestamp
    all_candles.sort(key=lambda x: x[0])
    print(f"Total candles for EMA calculation: {len(all_candles)}")
    
    return all_candles

def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average (EMA) using TradingView formula
    EMA = (Current Price * (2 / (Period + 1))) + (Previous EMA * (1 - (2 / (Period + 1))))
    """
    if len(prices) < period:
        return [None] * len(prices)
    
    ema_values = []
    multiplier = 2.0 / (period + 1)
    
    # First EMA value is the SMA of the first 'period' values
    first_sma = sum(prices[:period]) / period
    ema_values.append(first_sma)
    
    # Calculate subsequent EMA values
    for i in range(1, len(prices)):
        if i < period:
            ema_values.append(None)
        else:
            current_price = prices[i]
            previous_ema = ema_values[i - 1] if ema_values[i - 1] is not None else first_sma
            current_ema = (current_price * multiplier) + (previous_ema * (1 - multiplier))
            ema_values.append(current_ema)
    
    return ema_values

def get_hourly_data_for_display(instrument_key):
    """Get hourly data for display purposes"""
    safe_key = instrument_key.replace('|', '%7C')
    
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    # Get hourly data
    hourly_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/60/{end_date}/{start_date}?size=200'
    
    hourly_candles = []
    
    try:
        response = requests.get(hourly_url, headers=headers)
        if response.status_code == 200:
            hourly_candles = response.json().get('data', {}).get('candles', [])
            if hourly_candles:
                print(f"Got {len(hourly_candles)} hourly candles for display")
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
    except Exception as e:
        print(f"Error fetching today's hourly data: {e}")
    
    if not hourly_candles:
        print("No hourly data available")
        return None
    
    # Sort by timestamp
    hourly_candles.sort(key=lambda x: x[0])
    
    return hourly_candles

def get_ema_for_timestamp(historical_candles, target_timestamp, period):
    """Get EMA value for a specific timestamp"""
    # Find candles up to the target timestamp
    relevant_candles = []
    target_dt = target_timestamp
    
    for candle in historical_candles:
        candle_dt = datetime.fromisoformat(candle[0].replace('+05:30', ''))
        if candle_dt <= target_dt:
            relevant_candles.append(candle)
        else:
            break
    
    if len(relevant_candles) < period:
        return None
    
    # Extract closing prices
    closes = [float(candle[4]) for candle in relevant_candles]
    
    # Calculate EMA
    ema_values = calculate_ema(closes, period)
    
    # Return the last EMA value
    return ema_values[-1] if ema_values and ema_values[-1] is not None else None

def analyze_ema():
    """Main function to analyze EMA for the configured symbol"""
    print("Loading data for EMA analysis...")
    
    # Get symbol configuration
    symbol = 'RELIANCE'
    instrument_key = CONFIG['symbols'][symbol]
    
    # Get historical data for EMA calculation
    historical_candles = get_historical_data(instrument_key)
    if not historical_candles:
        print(f"No historical data available for {symbol}")
        return
    
    # Get hourly data for display
    hourly_candles = get_hourly_data_for_display(instrument_key)
    if not hourly_candles:
        print(f"No hourly data available for {symbol}")
        return
    
    # Prepare table data
    table_data = []
    headers = ["Timestamp", "Code", "Last Price", "EMA-9", "EMA-9 Diff", "EMA-15", "EMA-15 Diff"]
    
    # Filter hourly data to last 5 working days
    current_date = datetime.now()
    five_days_ago = current_date - timedelta(days=7)
    
    filtered_hourly = []
    for candle in hourly_candles:
        candle_date = datetime.fromisoformat(candle[0].replace('+05:30', ''))
        if candle_date >= five_days_ago:
            filtered_hourly.append(candle)
    
    # Sort hourly data
    filtered_hourly.sort(key=lambda x: x[0])
    
    print(f"Processing {len(filtered_hourly)} hourly candles for EMA display")
    
    for i, candle in enumerate(filtered_hourly):
        timestamp_str = candle[0]
        timestamp = datetime.fromisoformat(timestamp_str.replace('+05:30', ''))
        price = float(candle[4])  # Close price
        
        # Skip non-trading hours
        if timestamp.hour < 9 or (timestamp.hour == 9 and timestamp.minute < 15) or timestamp.hour >= 16:
            continue
        
        # Calculate EMA values for this timestamp
        ema_9 = get_ema_for_timestamp(historical_candles, timestamp, 9)
        ema_15 = get_ema_for_timestamp(historical_candles, timestamp, 15)
        
        # Format timestamp
        timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M")
        
        # Format EMA-9 and calculate difference
        if ema_9 is not None:
            ema_9_str = f"{ema_9:.2f}"
            diff_9 = price - ema_9
            diff_9_pct = (diff_9 / ema_9) * 100
            if diff_9 > 0:
                ema_9_diff_str = f"+{diff_9:.2f} (+{diff_9_pct:.2f}%)"
            elif diff_9 < 0:
                ema_9_diff_str = f"{diff_9:.2f} ({diff_9_pct:.2f}%)"
            else:
                ema_9_diff_str = "0.00 (0.00%)"
        else:
            ema_9_str = "-"
            ema_9_diff_str = "-"
        
        # Format EMA-15 and calculate difference
        if ema_15 is not None:
            ema_15_str = f"{ema_15:.2f}"
            diff_15 = price - ema_15
            diff_15_pct = (diff_15 / ema_15) * 100
            if diff_15 > 0:
                ema_15_diff_str = f"+{diff_15:.2f} (+{diff_15_pct:.2f}%)"
            elif diff_15 < 0:
                ema_15_diff_str = f"{diff_15:.2f} ({diff_15_pct:.2f}%)"
            else:
                ema_15_diff_str = "0.00 (0.00%)"
        else:
            ema_15_str = "-"
            ema_15_diff_str = "-"
        
        row = [timestamp_formatted, symbol, f"₹{price:.2f}", ema_9_str, ema_9_diff_str, ema_15_str, ema_15_diff_str]
        table_data.append(row)
    
    # Display results
    print(f"\n{symbol} EMA Analysis - Last 5 Working Days")
    print("EMA calculated using exponential weighting (TradingView compatible)")
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
        print(f"EMA-9: {latest_row[3]} | Difference: {latest_row[4]}")
        print(f"EMA-15: {latest_row[5]} | Difference: {latest_row[6]}")
        
        # EMA trend analysis
        if latest_row[3] != "-" and latest_row[5] != "-":
            ema_9_val = float(latest_row[3])
            ema_15_val = float(latest_row[5])
            
            print(f"\nEMA Trend Analysis:")
            if ema_9_val > ema_15_val:
                trend = "🟢 BULLISH (EMA-9 > EMA-15)"
            elif ema_9_val < ema_15_val:
                trend = "🔴 BEARISH (EMA-9 < EMA-15)"
            else:
                trend = "🟡 NEUTRAL (EMA-9 = EMA-15)"
            
            print(f"EMA Crossover: {trend}")
            print(f"EMA-9 vs EMA-15: {ema_9_val:.2f} vs {ema_15_val:.2f}")

if __name__ == "__main__":
    analyze_ema()