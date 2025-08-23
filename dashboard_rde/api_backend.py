"""
Backend API for RSI, DMA, and EMA Dashboard
Provides exact calculations from the individual scripts
"""

import requests
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)
test_zone_dir = os.path.join(parent_dir, 'test_zone')
sys.path.append(test_zone_dir)

try:
    from rsi_config import CONFIG
except ImportError:
    # Fallback configuration
    CONFIG = {
        'upstox_token': 'Bearer YOUR_TOKEN_HERE',
        'symbols': {
            'RELIANCE': 'NSE_EQ|INE002A01018',
            'TCS': 'NSE_EQ|INE467B01029',
            'HDFCBANK': 'NSE_EQ|INE040A01034',
            'INFY': 'NSE_EQ|INE009A01021',
            'ICICIBANK': 'NSE_EQ|INE090A01021'
        }
    }

class DashboardAPI:
    def __init__(self):
        self.symbols = CONFIG['symbols']
        self.headers = {
            'Accept': 'application/json',
            'Api-Version': '3.0',
            'Authorization': CONFIG['upstox_token']
        }
    
    def get_available_symbols(self):
        """Get list of available symbols"""
        return list(self.symbols.keys())
    
    def get_historical_data(self, instrument_key):
        """Get historical data for calculations - same as tradingview_dma.py"""
        safe_key = instrument_key.replace('|', '%7C')
        all_candles = []
        
        # Method 1: Get recent data with 15-minute intervals (last 30 days)
        today = datetime.now()
        end_date = today.strftime('%Y-%m-%d')
        start_date_recent = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        hist_url = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/15/{end_date}/{start_date_recent}?size=1000'
        
        try:
            response = requests.get(hist_url, headers=self.headers)
            if response.status_code == 200:
                hist_candles = response.json().get('data', {}).get('candles', [])
                if hist_candles:
                    all_candles.extend(hist_candles)
        except Exception as e:
            print(f"Error fetching recent data: {e}")
        
        # Method 2: Get older data with 4-hour intervals for more history
        start_date_old = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        start_date_mid = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        hist_url_old = f'https://api.upstox.com/v3/historical-candle/{safe_key}/minutes/240/{start_date_mid}/{start_date_old}?size=1000'
        
        try:
            response = requests.get(hist_url_old, headers=self.headers)
            if response.status_code == 200:
                old_candles = response.json().get('data', {}).get('candles', [])
                if old_candles:
                    all_candles.extend(old_candles)
        except Exception as e:
            print(f"Error fetching older data: {e}")
        
        # Get today's data (intraday)
        intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/15'
        try:
            response = requests.get(intra_url, headers=self.headers)
            if response.status_code == 200:
                today_candles = response.json().get('data', {}).get('candles', [])
                if today_candles:
                    all_candles.extend(today_candles)
        except Exception as e:
            print(f"Error fetching today's data: {e}")
        
        if not all_candles:
            return None
        
        # Sort by timestamp
        all_candles.sort(key=lambda x: x[0])
        return all_candles
    
    def get_daily_data_from_existing(self, candles):
        """Extract daily closing prices - same as tradingview_dma.py"""
        if not candles:
            return []
        
        daily_data = {}
        
        for candle in candles:
            timestamp = datetime.fromisoformat(candle[0].replace('+05:30', ''))
            date_key = timestamp.date()
            
            # Skip non-trading hours
            if timestamp.hour < 9 or (timestamp.hour == 9 and timestamp.minute < 15) or timestamp.hour >= 16:
                continue
            
            close_price = float(candle[4])
            
            # Keep the latest close for each day (closest to market close)
            if date_key not in daily_data or timestamp.time() > daily_data[date_key]['time']:
                daily_data[date_key] = {
                    'close': close_price,
                    'time': timestamp.time(),
                    'date': date_key
                }
        
        # Convert to sorted list
        daily_closes = []
        for date_key in sorted(daily_data.keys()):
            daily_closes.append(daily_data[date_key]['close'])
        
        return daily_closes
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI - same as rsi_scanner_final.py"""
        if len(prices) < period + 1:
            return None
        
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        # Calculate initial average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate RSI for each subsequent period
        rsi_values = []
        
        for i in range(period, len(gains)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
            
            # Update averages using Wilder's smoothing
            if i < len(gains):
                avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
                avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
        
        return rsi_values[-1] if rsi_values else None
    
    def calculate_dma(self, prices, period):
        """Calculate DMA (Simple Moving Average) - same as tradingview_dma.py"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices, period):
        """Calculate EMA - same as ema_calculator.py"""
        if len(prices) < period:
            return None
        
        multiplier = 2.0 / (period + 1)
        
        # First EMA value is the SMA of the first 'period' values
        first_sma = sum(prices[:period]) / period
        ema = first_sma
        
        # Calculate subsequent EMA values
        for i in range(period, len(prices)):
            current_price = prices[i]
            ema = (current_price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def get_current_price(self, instrument_key):
        """Get current market price"""
        safe_key = instrument_key.replace('|', '%7C')
        
        # Try to get current price from intraday data
        intra_url = f'https://api.upstox.com/v3/historical-candle/intraday/{safe_key}/minutes/1'
        try:
            response = requests.get(intra_url, headers=self.headers)
            if response.status_code == 200:
                candles = response.json().get('data', {}).get('candles', [])
                if candles:
                    return float(candles[0][4])  # Latest close price
        except Exception as e:
            print(f"Error fetching current price: {e}")
        
        return None
    
    def get_symbol_data(self, symbol):
        """Get complete data for a symbol"""
        if symbol not in self.symbols:
            return None
        
        instrument_key = self.symbols[symbol]
        
        # Get historical data
        historical_candles = self.get_historical_data(instrument_key)
        if not historical_candles:
            return None
        
        # Extract daily closing prices
        daily_closes = self.get_daily_data_from_existing(historical_candles)
        if len(daily_closes) < 20:  # Need minimum data
            return None
        
        # Get current price
        current_price = self.get_current_price(instrument_key)
        if not current_price:
            current_price = daily_closes[-1]  # Use last close if current not available
        
        # Calculate all indicators
        result = {
            'symbol': symbol,
            'current_price': current_price,
            'data_points': len(daily_closes),
            'rsi': {},
            'dma': {},
            'ema': {}
        }
        
        # RSI Calculation (using all available data for 15-minute RSI)
        all_closes = [float(candle[4]) for candle in historical_candles]
        rsi_14 = self.calculate_rsi(all_closes, 14)
        if rsi_14:
            result['rsi']['rsi_14'] = {
                'value': round(rsi_14, 2),
                'signal': 'Overbought' if rsi_14 > 70 else 'Oversold' if rsi_14 < 30 else 'Neutral'
            }
        
        # DMA Calculations (using daily closes)
        dma_periods = [10, 20, 50]
        for period in dma_periods:
            dma_value = self.calculate_dma(daily_closes, period)
            if dma_value:
                diff = current_price - dma_value
                diff_pct = (diff / dma_value) * 100
                result['dma'][f'dma_{period}'] = {
                    'value': round(dma_value, 2),
                    'difference': round(diff, 2),
                    'difference_pct': round(diff_pct, 2),
                    'signal': 'Above' if diff > 0 else 'Below'
                }
        
        # EMA Calculations (using daily closes)
        ema_periods = [9, 15]
        for period in ema_periods:
            ema_value = self.calculate_ema(daily_closes, period)
            if ema_value:
                diff = current_price - ema_value
                diff_pct = (diff / ema_value) * 100
                result['ema'][f'ema_{period}'] = {
                    'value': round(ema_value, 2),
                    'difference': round(diff, 2),
                    'difference_pct': round(diff_pct, 2),
                    'signal': 'Above' if diff > 0 else 'Below'
                }
        
        # EMA Trend Analysis
        if 'ema_9' in result['ema'] and 'ema_15' in result['ema']:
            ema_9_val = result['ema']['ema_9']['value']
            ema_15_val = result['ema']['ema_15']['value']
            
            if ema_9_val > ema_15_val:
                trend = 'Bullish'
            elif ema_9_val < ema_15_val:
                trend = 'Bearish'
            else:
                trend = 'Neutral'
            
            result['ema']['trend'] = trend
        
        return result

# Create global API instance
api = DashboardAPI()