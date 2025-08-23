"""
Flask Web Server for RSI, DMA & EMA Dashboard
Optimized for Railway.app deployment
"""

from flask import Flask, jsonify, send_from_directory
import os
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get port from environment variable (Railway sets this)
PORT = int(os.environ.get('PORT', 5000))

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/symbols')
def get_symbols():
    """Get available symbols"""
    try:
        symbols = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 
            'KOTAKBANK', 'HINDUNILVR', 'BHARTIARTL', 'SBIN', 
            'BAJFINANCE', 'MARUTI', 'ASIANPAINT', 'NESTLEIND',
            'AXISBANK', 'BAJAJFINSV', 'WIPRO'
        ]
        return jsonify({'symbols': symbols, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/data/<symbol>')
def get_symbol_data(symbol):
    """Get complete data for a symbol"""
    try:
        mock_data = generate_mock_data(symbol.upper())
        return jsonify({'data': mock_data, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def generate_mock_data(symbol):
    """Generate realistic mock data for testing"""
    
    # Base prices for different symbols
    base_prices = {
        'RELIANCE': 1409.90, 'TCS': 4145.25, 'HDFCBANK': 1742.60,
        'INFY': 1845.30, 'ICICIBANK': 1295.75, 'KOTAKBANK': 1765.20,
        'HINDUNILVR': 2543.75, 'BHARTIARTL': 1598.45, 'SBIN': 834.15,
        'BAJFINANCE': 7234.60, 'MARUTI': 13245.75, 'ASIANPAINT': 2845.30,
        'NESTLEIND': 2387.40, 'AXISBANK': 1287.65, 'BAJAJFINSV': 1654.80,
        'WIPRO': 543.20
    }

    price = base_prices.get(symbol, 1500.0)
    
    # Add some realistic price variation (±2%)
    price_variation = random.uniform(-0.02, 0.02)
    current_price = price * (1 + price_variation)
    
    # Generate realistic RSI value (weighted towards normal range)
    rsi_weights = [30, 40, 50, 60, 70]  # More likely to be in middle ranges
    rsi_val = random.choices(rsi_weights, weights=[10, 25, 30, 25, 10])[0] + random.uniform(-10, 10)
    rsi_val = max(0, min(100, rsi_val))  # Clamp between 0-100
    
    if rsi_val > 70:
        rsi_signal = 'Overbought'
    elif rsi_val < 30:
        rsi_signal = 'Oversold'
    else:
        rsi_signal = 'Neutral'
    
    # Generate realistic DMA values (DMAs should be close to current price)
    dma_10_val = current_price * random.uniform(0.995, 1.005)  # Very close to price
    dma_20_val = current_price * random.uniform(0.990, 1.010)  # Slightly more spread
    dma_50_val = current_price * random.uniform(0.980, 1.020)  # More spread for longer period
    
    # Generate realistic EMA values (EMAs react faster than DMAs)
    ema_9_val = current_price * random.uniform(0.998, 1.002)   # Very close to price
    ema_15_val = current_price * random.uniform(0.995, 1.005)  # Slightly more spread
    
    # Determine EMA trend based on crossover
    ema_trend = 'Bullish' if ema_9_val > ema_15_val else 'Bearish'
    
    return {
        'symbol': symbol,
        'current_price': round(current_price, 2),
        'data_points': random.randint(60, 68),  # Realistic data range
        'timestamp': '2025-08-24 15:30:00',
        'rsi': {
            'rsi_14': {
                'value': round(rsi_val, 2),
                'signal': rsi_signal,
                'interpretation': get_rsi_interpretation(rsi_val),
                'calculation': 'Wilder\'s Smoothing (14 periods)'
            }
        },
        'dma': {
            'dma_10': {
                'value': round(dma_10_val, 2),
                'difference': round(current_price - dma_10_val, 2),
                'difference_pct': round(((current_price - dma_10_val) / dma_10_val) * 100, 2),
                'signal': 'Above' if current_price > dma_10_val else 'Below',
                'calculation': 'Daily Closes (10 days)'
            },
            'dma_20': {
                'value': round(dma_20_val, 2),
                'difference': round(current_price - dma_20_val, 2),
                'difference_pct': round(((current_price - dma_20_val) / dma_20_val) * 100, 2),
                'signal': 'Above' if current_price > dma_20_val else 'Below',
                'calculation': 'Daily Closes (20 days)'
            },
            'dma_50': {
                'value': round(dma_50_val, 2),
                'difference': round(current_price - dma_50_val, 2),
                'difference_pct': round(((current_price - dma_50_val) / dma_50_val) * 100, 2),
                'signal': 'Above' if current_price > dma_50_val else 'Below',
                'calculation': 'Daily Closes (50 days)'
            }
        },
        'ema': {
            'ema_9': {
                'value': round(ema_9_val, 2),
                'difference': round(current_price - ema_9_val, 2),
                'difference_pct': round(((current_price - ema_9_val) / ema_9_val) * 100, 2),
                'signal': 'Above' if current_price > ema_9_val else 'Below',
                'calculation': 'Exponential Weighting (9 periods)'
            },
            'ema_15': {
                'value': round(ema_15_val, 2),
                'difference': round(current_price - ema_15_val, 2),
                'difference_pct': round(((current_price - ema_15_val) / ema_15_val) * 100, 2),
                'signal': 'Above' if current_price > ema_15_val else 'Below',
                'calculation': 'Exponential Weighting (15 periods)'
            },
            'trend': ema_trend,
            'crossover_signal': f'EMA-9 {">" if ema_trend == "Bullish" else "<"} EMA-15'
        }
    }

def get_rsi_interpretation(rsi_val):
    """Get RSI interpretation based on value"""
    if rsi_val > 80:
        return 'Strongly Overbought'
    elif rsi_val > 70:
        return 'Overbought'
    elif rsi_val > 60:
        return 'Bullish'
    elif rsi_val > 40:
        return 'Neutral'
    elif rsi_val > 30:
        return 'Bearish'
    elif rsi_val > 20:
        return 'Oversold'
    else:
        return 'Strongly Oversold'

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy', 
        'service': 'Technical Analysis Dashboard',
        'version': '1.0.0',
        'environment': 'production'
    })

@app.route('/api/health')
def api_health():
    """API health check"""
    return jsonify({'api_status': 'operational', 'data_source': 'mock_data'})

if __name__ == '__main__':
    print("🚀 Starting Technical Analysis Dashboard for Railway...")
    print(f"🌐 Running on port: {PORT}")
    print("📊 Dashboard Features:")
    print("   ✅ RSI Analysis (14-period)")
    print("   ✅ DMA Analysis (10/20/50 periods)")
    print("   ✅ EMA Analysis (9/15 periods)")
    print("   ✅ Real-time mock data")
    print("   ✅ Responsive design")
    print("\n" + "="*50)
    
    # Use Gunicorn-compatible settings for Railway
    app.run(host='0.0.0.0', port=PORT, debug=False)