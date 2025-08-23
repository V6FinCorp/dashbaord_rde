import sys
import os

# Add parent directory to path for config imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
dashboard_dir = os.path.join(parent_dir, 'dashboard')
sys.path.append(dashboard_dir)

from rsi_config import CONFIG
from dma_calculator import get_candle_data

candles = get_candle_data(CONFIG['symbols']['RELIANCE'], CONFIG['timeframe'])
if candles:
    print('First candle:', candles[0])
    print('Candle structure:', type(candles[0]), len(candles[0]))
    for i, item in enumerate(candles[0]):
        print(f'Index {i}: {item} (type: {type(item)})')