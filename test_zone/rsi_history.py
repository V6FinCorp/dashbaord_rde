#!/usr/bin/env python3
"""
Display complete day's RSI values for a single stock
"""
import os
import sys
import requests
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate

# Add parent dir to path for config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from rsi_config import CONFIG

def calculate_rsi(closes, period=14):
    """Calculate RSI using numpy."""
    closes = np.array(closes)
    deltas = np.diff(closes)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Initialize RSI list
    rsi_values = []
    
    # Calculate first RSI using simple averages
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        first_rsi = 100
    else:
        rs = avg_gain / avg_loss
        first_rsi = 100 - (100 / (1 + rs))
    
    rsi_values.append(first_rsi)
    
    # Use Wilder's smoothing for subsequent values
    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    
    return rsi_values

def get_candle_data(instrument_key, timeframe=15):
    """Get combined historical and intraday data for proper RSI calculation."""
    safe_key = instrument_key.replace('|', '%7C')
    
    # Calculate dates
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get historical data from yesterday (for proper RSI calculation)
    hist_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/{timeframe}/{yesterday}/{yesterday}'
    intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/{timeframe}'
    
    all_candles = []
    
    # Get yesterday's data
    try:
        response = requests.get(hist_url)
        if response.status_code == 200:
            hist_candles = response.json().get('data', {}).get('candles', [])
            if hist_candles:
                # Take only end of day candles for RSI calculation
                all_candles.extend(hist_candles[-CONFIG['rsi_period']:])
                print(f"Got {len(hist_candles[-CONFIG['rsi_period']:])} historical candles for RSI calculation")
    except Exception as e:
        print(f"Error fetching historical data: {e}")
    
    # Get today's data
    try:
        response = requests.get(intra_url)
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
    
    return all_candles

def format_price_change(current, previous, open_price):
    """Format price change with color and arrow and day change percentage."""
    day_change_pct = ((current - open_price) / open_price) * 100
    
    # Add ANSI colors
    if current > previous:
        price_str = f"{Colors.GREEN}↑ {current:.2f}"
    elif current < previous:
        price_str = f"{Colors.RED}↓ {current:.2f}"
    else:
        price_str = f"- {current:.2f}"
    
    # Add day change percentage
    if day_change_pct > 0:
        price_str += f" (+{day_change_pct:.2f}%){Colors.ENDC}"
    else:
        price_str += f" ({day_change_pct:.2f}%){Colors.ENDC}"
    
    return price_str

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    # Get Reliance data
    instrument_key = CONFIG['symbols']['RELIANCE']
    candles = get_candle_data(instrument_key)
    
    if not candles:
        print("No data available")
        return
    
    # Split historical and today's data
    today = datetime.now().strftime('%Y-%m-%d')
    today_candles = [c for c in candles if today in c[0]]
    hist_candles = [c for c in candles if today not in c[0]]
    
    # Put today's candles in chronological order (9:15 first)
    today_candles.reverse()
    
    print(f"\nHistorical candles: {len(hist_candles)}")
    print(f"Today's candles: {len(today_candles)}")
    
    # Print first few candles for verification
    print("\nFirst few candles (Time, Open, High, Low, Close, Volume):")
    for i, candle in enumerate(today_candles[:3]):
        time = datetime.fromisoformat(candle[0]).strftime("%H:%M")
        print(f"{time}: {candle[1]}, {candle[2]}, {candle[3]}, {candle[4]}, {candle[5]}")
    
    # Get all close prices for RSI calculation (historical + today's)
    hist_prices = [float(candle[4]) for candle in hist_candles]
    today_prices = [float(candle[4]) for candle in today_candles]  # Already in chronological order
    
    # Today's display data
    timestamps = [datetime.fromisoformat(candle[0]).strftime("%H:%M") for candle in today_candles]
    volumes = [int(candle[5]) for candle in today_candles]
    
    # Calculate RSI using historical + today's data
    all_prices = hist_prices + today_prices
    
    # Calculate RSI values
    rsi_values = calculate_rsi(all_prices, CONFIG['rsi_period'])
    
    # Create result table with padding for initial RSI calculation period
    results = []
    rsi_values = calculate_rsi(all_prices, CONFIG['rsi_period'])
    
    # Get today's opening price (last candle from reversed today's data)
    open_price = float(today_candles[-1][4])  # Opening price from first candle of the day
    
    # Process today's candles in chronological order
    for i, candle in enumerate(today_candles):
        current_price = float(candle[4])
        prev_price = float(today_candles[i-1][4]) if i > 0 else current_price
        
        # Format price with change indicator and day change percentage
        price_str = format_price_change(
            current_price,
            prev_price,
            open_price
        )
        
        # Get corresponding RSI value
        # Since RSI is calculated with historical + chronological today's data,
        # we need to map the index correctly
        rsi_idx = len(rsi_values) - len(today_candles) + i
        
        if rsi_idx >= 0:
            rsi_str = f"{rsi_values[rsi_idx]:.2f}"
            if rsi_values[rsi_idx] >= 70:
                rsi_str = f"{Colors.RED}{rsi_str} [OVERBOUGHT]{Colors.ENDC}"
            elif rsi_values[rsi_idx] <= 30:
                rsi_str = f"{Colors.GREEN}{rsi_str} [OVERSOLD]{Colors.ENDC}"
        else:
            rsi_str = f"{Colors.YELLOW}Calculating...{Colors.ENDC}"
        
        results.append([
            timestamps[i],
            price_str,
            rsi_str,
            f"{volumes[i]:,}",
            "⚫ CURRENT" if i == len(today_candles)-1 else "→"  # Current is last candle
        ])
    
    # Display results
    print(f"\n{Colors.HEADER}Reliance (NSE) - {datetime.now().strftime('%Y-%m-%d')}{Colors.ENDC}")
    print(f"Timeframe: 15 minutes | RSI Period: {CONFIG['rsi_period']}\n")
    
    headers = ["Time", "Price (% Change)", "RSI", "Volume", ""]
    print(tabulate(results, headers=headers, tablefmt="grid", stralign="center"))
    
    # Show summary
    latest_price = all_prices[-1]
    day_change = ((latest_price - open_price) / open_price) * 100
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"Open: ₹{open_price:.2f}")
    print(f"Current: ₹{latest_price:.2f} ({day_change:+.2f}%)")
    
    if len(rsi_values) > 0:
        print(f"\nRSI Statistics:")
        print(f"Current RSI: {rsi_values[-1]:.2f}")
        print(f"Day's Range: {min(rsi_values):.2f} - {max(rsi_values):.2f}")
        
        # Add RSI trend analysis
        last_5_rsi = rsi_values[-5:] if len(rsi_values) >= 5 else rsi_values
        rsi_trend = "↗️ RISING" if all(a < b for a, b in zip(last_5_rsi[:-1], last_5_rsi[1:])) else \
                    "↘️ FALLING" if all(a > b for a, b in zip(last_5_rsi[:-1], last_5_rsi[1:])) else \
                    "↔️ SIDEWAYS"
        print(f"RSI Trend: {rsi_trend}")

if __name__ == '__main__':
    import os
    main()