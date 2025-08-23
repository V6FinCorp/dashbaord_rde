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

# Add paths for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)

from rsi_config import CONFIG
from config_local import UPSTOX_ACCESS_TOKEN

def rma(x, n, y0):
    """
    Implementation of TradingView's ta.rma (Relative Moving Average/Wilder's Smoothing)
    """
    a = 1.0 / n
    y = np.zeros(len(x))
    y[0] = y0  # Initialize first value
    
    for i in range(1, len(y)):
        y[i] = a * x[i] + (1 - a) * y[i-1]
    
    return y

def calculate_rsi(closes, period=14):
    """
    Calculate RSI exactly as TradingView does:
    1. Calculate change
    2. Split into gain (positive change) and loss (negative change)
    3. Calculate relative moving average (Wilder's Smoothing) of gains and losses
    4. Calculate RS and RSI
    """
    closes = np.array(closes)
    change = np.diff(closes)  # Same as ta.change(close)
    
    # Split change into gain and loss
    gain = np.where(change > 0, change, 0)
    loss = np.where(change < 0, -change, 0)
    
    # Calculate initial averages
    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])
    
    # Use RMA (Wilder's Smoothing) for gains and losses
    gains_rma = rma(gain[period-1:], period, avg_gain)
    losses_rma = rma(loss[period-1:], period, avg_loss)
    
    # Calculate RSI
    rsi_values = []
    for i in range(len(gains_rma)):
        if losses_rma[i] == 0:
            rsi = 100
        elif gains_rma[i] == 0:
            rsi = 0
        else:
            rs = gains_rma[i] / losses_rma[i]
            rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    
    return rsi_values

def get_candle_data(instrument_key, timeframe=15):
    """Get combined historical and intraday data for proper RSI calculation."""
    safe_key = instrument_key.replace('|', '%7C')
    
    # Calculate dates - get last 5 days to ensure we have enough trading days
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')  # Get 7 days to ensure enough trading days
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    # Get historical data for last few days - Note: API expects (to_date, from_date) order
    # We need more historical data for accurate RSI calculation
    hist_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/{timeframe}/{end_date}/{start_date}?size=200'
    
    all_candles = []
    
    # Get historical data
    try:
        response = requests.get(hist_url, headers=headers)
        if response.status_code == 200:
            hist_candles = response.json().get('data', {}).get('candles', [])
            if hist_candles:
                # Take all historical candles for proper RSI calculation
                all_candles.extend(hist_candles)
                print(f"Got {len(hist_candles)} historical candles for RSI calculation")
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
    instrument_key = CONFIG['symbols']['TCS']
    candles = get_candle_data(instrument_key)
    
    if not candles:
        print("No data available")
        return
    
    # Group candles by date and filter for market hours
    candle_by_date = {}
    for c in candles:
        candle_time = datetime.fromisoformat(c[0])
        date_str = candle_time.strftime('%Y-%m-%d')
        hour = candle_time.hour
        minute = candle_time.minute
        
        # Only include market hours (9:15 AM to 3:30 PM)
        if ((hour == 9 and minute >= 15) or 
            (hour > 9 and hour < 15) or 
            (hour == 15 and minute <= 30)):
            if date_str not in candle_by_date:
                candle_by_date[date_str] = []
            candle_by_date[date_str].append(c)
    
    # Sort dates in reverse order (newest first)
    sorted_dates = sorted(candle_by_date.keys(), reverse=True)
    
    if not sorted_dates:
        print("No data available for any trading day")
        return
        
    # Find last complete trading day (with enough candles)
    MIN_CANDLES_FOR_VALID_DAY = 20  # Minimum number of candles for a valid trading day
    valid_trading_day = None
    complete_trading_days = []
    
    for date_str in sorted_dates:
        if len(candle_by_date[date_str]) >= MIN_CANDLES_FOR_VALID_DAY:
            complete_trading_days.append(date_str)
            if not valid_trading_day:  # First complete day found
                valid_trading_day = date_str
    
    if not valid_trading_day:
        print("No complete trading day found in the data")
        return
        
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Use current day's data if available and complete, otherwise use last valid trading day
    if today in candle_by_date and len(candle_by_date[today]) >= MIN_CANDLES_FOR_VALID_DAY:
        today_candles = sorted(candle_by_date[today], key=lambda x: x[0])
    else:
        today_candles = sorted(candle_by_date[valid_trading_day], key=lambda x: x[0])
        
    # Get historical data from previous days
    hist_candles = []
    for date_str in complete_trading_days[1:]:  # Skip the day we're displaying
        hist_candles.extend(sorted(candle_by_date[date_str], key=lambda x: x[0]))

    if not hist_candles:
        print("No historical data available for RSI calculation")
        return
    
    if len(hist_candles) < CONFIG['rsi_period']:
        print(f"Insufficient historical data for RSI calculation. Need {CONFIG['rsi_period']} candles, got {len(hist_candles)}")
        return
        
    # Sort historical candles chronologically
    hist_candles.sort(key=lambda x: x[0])  # Sort by timestamp
    
    # Sort candles in chronological order (oldest to newest)
    hist_candles.sort(key=lambda x: x[0])
    today_candles.sort(key=lambda x: x[0])
    
    print(f"\nHistorical candles: {len(hist_candles)}")
    print(f"Today's candles: {len(today_candles)}")
    
    # Print first few candles for verification
    print("\nFirst few candles (Time, Open, High, Low, Close, Volume):")
    for i, candle in enumerate(today_candles[:3]):
        time = datetime.fromisoformat(candle[0]).strftime("%H:%M")
        print(f"{time}: {candle[1]}, {candle[2]}, {candle[3]}, {candle[4]}, {candle[5]}")
    
    # Get all close prices for RSI calculation (historical + today's)
    hist_prices = [float(candle[4]) for candle in hist_candles]
    today_prices = [float(candle[4]) for candle in today_candles]
    
    # Display data for current session (today or historical)
    timestamps = [datetime.fromisoformat(candle[0]).strftime("%H:%M") for candle in today_candles]
    volumes = [int(candle[5]) for candle in today_candles]
    today_prices = [float(candle[4]) for candle in today_candles]
    
    # Get all prices for RSI calculation
    all_prices = hist_prices + today_prices
    
    # Print some debug info
    print("\nRSI Calculation Info:")
    print(f"Total candles for RSI: {len(all_prices)}")
    print(f"Historical prices: {len(hist_prices)}")
    print(f"Today's prices: {len(today_prices)}")
    
    # Calculate RSI values once
    rsi_values = calculate_rsi(all_prices, CONFIG['rsi_period'])
    print(f"Generated RSI values: {len(rsi_values)}")
    
    # RSI values will start being valid after the initial period
    valid_rsi_start = CONFIG['rsi_period']
    
    # Create result table with padding for initial RSI calculation period
    results = []
    
    # Check if we have today's data
    if not today_candles:
        print(f"\n{Colors.YELLOW}╔══════════════════════════════════════════╗")
        print(f"║ No data available for today's session yet! ║")
        print(f"╚══════════════════════════════════════════╝{Colors.ENDC}\n")
        print(f"{Colors.BLUE}Showing last available trading session data:{Colors.ENDC}")
        
        # Find the last trading day's data (filter market hours: 9:15 AM to 3:30 PM)
        last_day_candles = []
        for candle in reversed(hist_candles):
            candle_time = datetime.fromisoformat(candle[0])
            hour = candle_time.hour
            minute = candle_time.minute
            
            # Check if candle is within market hours (9:15 AM to 3:30 PM)
            if ((hour == 9 and minute >= 15) or 
                (hour > 9 and hour < 15) or 
                (hour == 15 and minute <= 30)):
                if not last_day_candles or candle_time.date() == datetime.fromisoformat(last_day_candles[0][0]).date():
                    last_day_candles.insert(0, candle)  # Insert at beginning to maintain chronological order
                else:
                    break  # We've found all candles for the last trading day
                    
        today_candles = last_day_candles
        
        if len(today_candles) > 0:
            last_date = datetime.fromisoformat(today_candles[0][0]).strftime('%Y-%m-%d')
            print(f"{Colors.BOLD}Date: {last_date}{Colors.ENDC}\n")
            
    # Sort today's candles chronologically (9:15 first)
    today_candles.sort(key=lambda x: x[0])
    
    # Generate display data
    timestamps = [datetime.fromisoformat(candle[0]).strftime("%H:%M") for candle in today_candles]
    volumes = [int(candle[5]) for candle in today_candles]
    today_prices = [float(candle[4]) for candle in today_candles]

    # Get opening price (first candle of the session)
    open_price = float(today_candles[0][4])
    
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
        # RSI values start after the initial period
        rsi_idx = i  # Index in today's candles
        total_idx = len(hist_prices) + i  # Index in combined prices
        
        if total_idx >= CONFIG['rsi_period']:
            rsi_position = total_idx - CONFIG['rsi_period']
            if rsi_position < len(rsi_values):
                current_rsi = rsi_values[rsi_position]
                rsi_str = f"{current_rsi:.2f}"
                if current_rsi >= 70:
                    rsi_str = f"{Colors.RED}{rsi_str} [OVERBOUGHT]{Colors.ENDC}"
                elif current_rsi <= 30:
                    rsi_str = f"{Colors.GREEN}{rsi_str} [OVERSOLD]{Colors.ENDC}"
            else:
                rsi_str = f"{Colors.YELLOW}Calculating...{Colors.ENDC}"
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
    display_date = datetime.now().strftime('%Y-%m-%d') if len(today_candles) > 0 else datetime.fromisoformat(today_candles[0][0]).strftime('%Y-%m-%d')
    print(f"\n{Colors.HEADER}Reliance (NSE) - {display_date}{Colors.ENDC}")
    print(f"Timeframe: 15 minutes | RSI Period: {CONFIG['rsi_period']} | Session: 9:15 AM - 3:30 PM\n")
    
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
        valid_rsi_values = [v for v in rsi_values if not isinstance(v, str)]
        if len(valid_rsi_values) >= 2:
            last_5_rsi = valid_rsi_values[-5:] if len(valid_rsi_values) >= 5 else valid_rsi_values
            rsi_trend = "↗️ RISING" if all(a < b for a, b in zip(last_5_rsi[:-1], last_5_rsi[1:])) else \
                        "↘️ FALLING" if all(a > b for a, b in zip(last_5_rsi[:-1], last_5_rsi[1:])) else \
                        "↔️ SIDEWAYS"
        else:
            rsi_trend = "➖ INSUFFICIENT DATA"
        print(f"RSI Trend: {rsi_trend}")

if __name__ == '__main__':
    import os
    main()