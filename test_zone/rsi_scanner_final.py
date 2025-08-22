#!/usr/bin/env python3
"""
RSI Scanner using Upstox API V3
Uses intraday or historical candle data
"""
import os
import sys
import json
import time
from datetime import datetime, timedelta
import requests
import numpy as np
from tabulate import tabulate

# Add parent dir to path for config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from dashboard.config_local import UPSTOX_ACCESS_TOKEN
from rsi_config import CONFIG

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def calculate_rsi(closes, period=14):
    """Calculate RSI using numpy."""
    closes = np.array(closes)
    deltas = np.diff(closes)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # Use Wilder's smoothing method
    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_intraday_data(instrument_key, timeframe):
    """Get intraday candle data from Upstox."""
    # Format instrument key for URL
    safe_key = instrument_key.replace('|', '%7C')
    url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/{timeframe}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data', {}).get('candles', [])
            return data
        else:
            print(f"Error getting data for {instrument_key}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception getting data for {instrument_key}: {e}")
        return None
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get('data', {}).get('candles', [])
            
            # Debug: Print raw response for the first symbol
            if instrument_key == list(CONFIG['symbols'].values())[0]:
                print(f"\nDEBUG Response for {instrument_key}:")
                print(f"Status Code: {response.status_code}")
                print(f"Raw Response: {response.text[:500]}...")  # Print first 500 chars
                if data:
                    print(f"First candle: {data[0]}")
                    print(f"Last candle: {data[-1]}")
                print(f"Number of candles: {len(data)}")
            
            if not data:
                print(f"No candle data received for {instrument_key}")
            return data
        else:
            print(f"Error getting intraday data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception getting intraday data: {e}")
    return None

def get_historical_data(instrument_key, timeframe):
    """Get historical candle data from Upstox."""
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {UPSTOX_ACCESS_TOKEN}'
    }
    
    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Format dates and instrument key
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')
    safe_key = instrument_key.replace('|', '%7C')
    
    url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/{timeframe}/{from_date}/{to_date}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', {}).get('candles', [])
            return data
        else:
            print(f"Error getting historical data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception getting historical data: {e}")
    return None

def scan_symbols():
    """Scan configured symbols for RSI conditions."""
    all_results = []
    alerts = []
    
    for symbol, instrument_key in CONFIG['symbols'].items():
        # Get candle data
        candles = get_intraday_data(instrument_key, CONFIG['timeframe'])
        
        if not candles:
            all_results.append(["N/A", instrument_key, symbol, "N/A", "N/A"])
            continue
        
        try:
            # Extract closing prices and timestamp from candles
            # Note: API returns newest candles first, we need to reverse for RSI calculation
            closes = [float(candle[4]) for candle in reversed(candles)]  # 5th element is close price
            # Get latest time from first candle (newest)
            latest_time = datetime.fromisoformat(candles[0][0]).strftime("%H:%M:%S")
            
            if len(closes) >= CONFIG['rsi_period']:
                # Calculate RSI
                rsi = calculate_rsi(closes, CONFIG['rsi_period'])
                current_price = float(candles[0][4])  # Get price from newest candle
                
                # Format the status based on RSI
                if rsi >= 70:
                    status = f"{Colors.RED}OVERBOUGHT{Colors.ENDC}"
                elif rsi <= 30:
                    status = f"{Colors.GREEN}OVERSOLD{Colors.ENDC}"
                else:
                    status = "NEUTRAL"
                
                # Add to results table
                all_results.append([
                    latest_time,
                    instrument_key,
                    symbol,
                    f"₹{current_price:.2f}",
                    f"{rsi:.2f}"
                ])
                
                # Check if RSI crosses threshold for alerts
                if rsi >= CONFIG['rsi_threshold']:
                    alerts.append({
                        'symbol': symbol,
                        'instrument_key': instrument_key,
                        'rsi': rsi,
                        'price': current_price,
                        'timeframe': f"{CONFIG['timeframe']}min",
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                all_results.append([symbol, "N/A", "N/A", "Insufficient data", "N/A"])
        except Exception as e:
            all_results.append([symbol, "N/A", "N/A", f"Error: {str(e)}", "N/A"])
    
    # Clear screen and show results table
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Colors.HEADER}Live Market RSI Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"Timeframe: {CONFIG['timeframe']}min | RSI Period: {CONFIG['rsi_period']} | Threshold: {CONFIG['rsi_threshold']}\n")
    
    # Sort results by timestamp (latest first)
    all_results.sort(key=lambda x: x[0] if x[0] != "N/A" and x[0] != "ERROR" else "00:00:00", reverse=True)
    
    # Display results in table format
    headers = ["Time", "Instrument", "Symbol", "Price", "RSI"]
    print(tabulate(all_results, headers=headers, tablefmt="grid", stralign="center"))
    
    return alerts

def save_results(results):
    """Save scan results to a file."""
    if not results:
        return
    
    # Create filename with timestamp
    filename = f"rsi_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    print(f"\n{Colors.BOLD}Live Market RSI Scanner{Colors.ENDC}")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        scan_count = 0
        while True:
            # Clear screen for fresh data
            os.system('cls' if os.name == 'nt' else 'clear')
            scan_count += 1
            
            # Show header with current time
            print(f"\n{Colors.HEADER}Live Market RSI Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
            print(f"Timeframe: {CONFIG['timeframe']}min | RSI Period: {CONFIG['rsi_period']} | Threshold: {CONFIG['rsi_threshold']}\n")
            
            # Scan symbols
            alerts = scan_symbols()
            
            # Save alerts if any symbols cross threshold
            if alerts:
                save_results(alerts)
                print(f"\n{Colors.YELLOW}Alert: {len(alerts)} symbol(s) crossed RSI threshold!{Colors.ENDC}")
            
            # Show next update countdown
            for i in range(CONFIG['scan_interval'], 0, -1):
                sys.stdout.write(f"\r{Colors.BLUE}Next update in {i} seconds... (Scan #{scan_count}){Colors.ENDC}")
                sys.stdout.flush()
                time.sleep(1)
            print("\r" + " " * 80 + "\r", end="")  # Clear the countdown line
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Scanner stopped by user.{Colors.ENDC}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error: {e}{Colors.ENDC}")

if __name__ == '__main__':
    main()