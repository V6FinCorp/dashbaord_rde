"""
Flask Web Server for RSI, DMA & EMA Dashboard
Serves the HTML dashboard and provides API endpoints for real-time data
"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import sys
from flask_cors import CORS

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from api_backend import api
except ImportError as e:
    print(f"Warning: Could not import api_backend: {e}")
    print("Dashboard will run with mock data only")
    api = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return send_from_directory(current_dir, 'dashboard.html')

@app.route('/api/symbols')
def get_symbols():
    """Get available symbols"""
    try:
        if api:
            symbols = api.get_available_symbols()
            return jsonify({'symbols': symbols, 'status': 'success'})
        else:
            # Fallback to hardcoded symbols
            symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
            return jsonify({'symbols': symbols, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/data/<symbol>')
def get_symbol_data(symbol):
    """Get complete data for a symbol"""
    try:
        if api:
            data = api.get_symbol_data(symbol.upper())
            if data:
                return jsonify({'data': data, 'status': 'success'})
            else:
                return jsonify({'error': f'No data available for {symbol}', 'status': 'error'}), 404
        else:
            # Return mock data when API is not available
            mock_data = generate_mock_data(symbol.upper())
            return jsonify({'data': mock_data, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def generate_mock_data(symbol):
    """Generate mock data for testing"""
    import random
    
    base_price = {
        'RELIANCE': 1409.90,
        'TCS': 4145.25,
        'HDFCBANK': 1742.60,
        'INFY': 1845.30,
        'ICICIBANK': 1295.75
    }

    price = base_price.get(symbol, 1500.0)
    
    # Generate realistic RSI value
    rsi_val = random.uniform(25, 75)
    rsi_signal = 'Overbought' if rsi_val > 70 else 'Oversold' if rsi_val < 30 else 'Neutral'
    
    # Generate realistic DMA values
    dma_10_val = price * random.uniform(0.985, 1.015)
    dma_20_val = price * random.uniform(0.980, 1.020)
    dma_50_val = price * random.uniform(0.970, 1.030)
    
    # Generate realistic EMA values
    ema_9_val = price * random.uniform(0.995, 1.005)
    ema_15_val = price * random.uniform(0.990, 1.010)
    
    # Determine EMA trend
    ema_trend = 'Bullish' if ema_9_val > ema_15_val else 'Bearish'
    
    return {
        'symbol': symbol,
        'current_price': price,
        'data_points': 64,
        'rsi': {
            'rsi_14': {
                'value': rsi_val,
                'signal': rsi_signal
            }
        },
        'dma': {
            'dma_10': {
                'value': dma_10_val,
                'difference': price - dma_10_val,
                'difference_pct': ((price - dma_10_val) / dma_10_val) * 100,
                'signal': 'Above' if price > dma_10_val else 'Below'
            },
            'dma_20': {
                'value': dma_20_val,
                'difference': price - dma_20_val,
                'difference_pct': ((price - dma_20_val) / dma_20_val) * 100,
                'signal': 'Above' if price > dma_20_val else 'Below'
            },
            'dma_50': {
                'value': dma_50_val,
                'difference': price - dma_50_val,
                'difference_pct': ((price - dma_50_val) / dma_50_val) * 100,
                'signal': 'Above' if price > dma_50_val else 'Below'
            }
        },
        'ema': {
            'ema_9': {
                'value': ema_9_val,
                'difference': price - ema_9_val,
                'difference_pct': ((price - ema_9_val) / ema_9_val) * 100,
                'signal': 'Above' if price > ema_9_val else 'Below'
            },
            'ema_15': {
                'value': ema_15_val,
                'difference': price - ema_15_val,
                'difference_pct': ((price - ema_15_val) / ema_15_val) * 100,
                'signal': 'Above' if price > ema_15_val else 'Below'
            },
            'trend': ema_trend
        }
    }

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'api_available': api is not None})

if __name__ == '__main__':
    print("🚀 Starting RSI, DMA & EMA Dashboard Server...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("🔗 API Endpoints:")
    print("   - GET /api/symbols - Get available symbols")
    print("   - GET /api/data/<symbol> - Get symbol data")
    print("   - GET /health - Health check")
    print("\n" + "="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)