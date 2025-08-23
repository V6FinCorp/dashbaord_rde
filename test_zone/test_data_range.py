"""
Test script to check maximum historical data range we can fetch
"""

import requests
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)

from rsi_config import CONFIG

def test_data_range(instrument_key, days_back):
    """Test how much historical data we can fetch"""
    safe_key = instrument_key.replace('|', '%7C')
    
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    start_date = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    headers = {
        'Accept': 'application/json',
        'Api-Version': '3.0',
        'Authorization': CONFIG['upstox_token']
    }
    
    # Try different timeframes
    timeframes = ['15', '60', '240']  # 15min, 1hour, 4hour
    
    for tf in timeframes:
        url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/{tf}/{end_date}/{start_date}?size=2000'
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                candles = response.json().get('data', {}).get('candles', [])
                print(f"Timeframe {tf}min, {days_back} days back: {len(candles)} candles")
            else:
                print(f"Timeframe {tf}min, {days_back} days back: ERROR {response.status_code}")
        except Exception as e:
            print(f"Timeframe {tf}min, {days_back} days back: EXCEPTION {e}")

# Test different date ranges
symbol = 'RELIANCE'
instrument_key = CONFIG['symbols'][symbol]

print("Testing data availability for different date ranges:")
print("=" * 60)

for days in [30, 60, 90, 180, 365, 500]:
    print(f"\n--- Testing {days} days back ---")
    test_data_range(instrument_key, days)