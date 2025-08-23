"""
Demo Dashboard with Real Data Sample
Shows exact output format as would appear from the actual scripts
"""

import webbrowser
from pathlib import Path

def create_demo_dashboard():
    """Create demo dashboard with sample real data"""
    
    # Sample data that matches actual script outputs
    sample_data = {
        'RELIANCE': {
            'current_price': 1409.90,
            'rsi_14': 52.34,
            'dma_10': 1393.72,
            'dma_20': 1394.48,
            'dma_50': 1444.25,
            'ema_9': 1411.75,
            'ema_15': 1413.07,
            'ema_trend': 'Bearish'
        }
    }
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSI, DMA & EMA Dashboard - Real Data Sample</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }}

        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
            color: white;
            padding: 15px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 1.6rem;
            margin-bottom: 5px;
            font-weight: 600;
        }}

        .header p {{
            font-size: 0.85rem;
            opacity: 0.9;
        }}

        .symbol-info {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
        }}

        .symbol-info h2 {{
            font-size: 1.4rem;
            margin-bottom: 5px;
        }}

        .current-price {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .data-info {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}

        .tables-container {{
            padding: 15px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }}

        .table-section {{
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            overflow: hidden;
        }}

        .table-header {{
            background: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 2px solid #dee2e6;
        }}

        .table-title {{
            font-size: 1rem;
            font-weight: 700;
            color: #343a40;
        }}

        .table-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 10px;
        }}

        .badge-rsi {{ background: #e3f2fd; color: #1976d2; }}
        .badge-dma {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-ema {{ background: #e8f5e8; color: #2e7d32; }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.75rem;
        }}

        .data-table th {{
            background: #f8f9fa;
            padding: 6px 4px;
            text-align: center;
            font-weight: 600;
            border: 1px solid #dee2e6;
            font-size: 0.7rem;
        }}

        .data-table td {{
            padding: 5px 3px;
            text-align: center;
            border: 1px solid #dee2e6;
            font-size: 0.7rem;
        }}

        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .positive {{ color: #28a745; font-weight: 600; }}
        .negative {{ color: #dc3545; font-weight: 600; }}
        .neutral {{ color: #6c757d; font-weight: 600; }}

        .rsi-normal {{ background: #fff3e0; color: #ef6c00; font-weight: bold; }}

        .timestamp {{
            text-align: center;
            padding: 10px;
            color: #6c757d;
            font-style: italic;
            border-top: 1px solid #e9ecef;
            font-size: 0.75rem;
        }}

        .demo-banner {{
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: 600;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 RSI, DMA & EMA Dashboard</h1>
            <p>Exact Table Format with Real Script Output</p>
        </div>

        <div class="demo-banner">
            🔥 DEMO: Showing exact format as would appear from rsi_scanner_final.py, tradingview_dma.py, and ema_calculator.py
        </div>

        <div class="symbol-info">
            <h2>RELIANCE</h2>
            <div class="current-price">₹{sample_data['RELIANCE']['current_price']:.2f}</div>
            <div class="data-info">Real data from August 22, 2025 (64 trading days)</div>
        </div>

        <div class="tables-container">
            <!-- RSI Table -->
            <div class="table-section">
                <div class="table-header">
                    <span class="table-title">📈 RSI Analysis</span>
                    <span class="table-badge badge-rsi">rsi_scanner_final.py</span>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Indicator</th>
                            <th>Current Value</th>
                            <th>Signal</th>
                            <th>Interpretation</th>
                            <th>Script Method</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>RSI-14</strong></td>
                            <td class="rsi-normal">{sample_data['RELIANCE']['rsi_14']:.2f}</td>
                            <td class="neutral">NEUTRAL</td>
                            <td>✅ Normal Range (30-70)</td>
                            <td>Wilder's Smoothing (14-period)</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- DMA Table -->
            <div class="table-section">
                <div class="table-header">
                    <span class="table-title">📊 DMA Analysis</span>
                    <span class="table-badge badge-dma">tradingview_dma.py</span>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Period</th>
                            <th>DMA Value</th>
                            <th>Price Diff (₹)</th>
                            <th>Price Diff (%)</th>
                            <th>Signal</th>
                            <th>TradingView Method</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>DMA-10</strong></td>
                            <td>₹{sample_data['RELIANCE']['dma_10']:.2f}</td>
                            <td class="positive">+₹{(sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_10']):.2f}</td>
                            <td class="positive">+{((sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_10']) / sample_data['RELIANCE']['dma_10'] * 100):.2f}%</td>
                            <td class="positive">ABOVE</td>
                            <td>Daily Closes (10 days)</td>
                        </tr>
                        <tr>
                            <td><strong>DMA-20</strong></td>
                            <td>₹{sample_data['RELIANCE']['dma_20']:.2f}</td>
                            <td class="positive">+₹{(sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_20']):.2f}</td>
                            <td class="positive">+{((sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_20']) / sample_data['RELIANCE']['dma_20'] * 100):.2f}%</td>
                            <td class="positive">ABOVE</td>
                            <td>Daily Closes (20 days)</td>
                        </tr>
                        <tr>
                            <td><strong>DMA-50</strong></td>
                            <td>₹{sample_data['RELIANCE']['dma_50']:.2f}</td>
                            <td class="negative">₹{(sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_50']):.2f}</td>
                            <td class="negative">{((sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['dma_50']) / sample_data['RELIANCE']['dma_50'] * 100):.2f}%</td>
                            <td class="negative">BELOW</td>
                            <td>Daily Closes (50 days)</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- EMA Table -->
            <div class="table-section">
                <div class="table-header">
                    <span class="table-title">⚡ EMA Analysis</span>
                    <span class="table-badge badge-ema">ema_calculator.py</span>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Period</th>
                            <th>EMA Value</th>
                            <th>Price Diff (₹)</th>
                            <th>Price Diff (%)</th>
                            <th>Signal</th>
                            <th>Exponential Method</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>EMA-9</strong></td>
                            <td>₹{sample_data['RELIANCE']['ema_9']:.2f}</td>
                            <td class="negative">₹{(sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['ema_9']):.2f}</td>
                            <td class="negative">{((sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['ema_9']) / sample_data['RELIANCE']['ema_9'] * 100):.2f}%</td>
                            <td class="negative">BELOW</td>
                            <td>2/(9+1) multiplier</td>
                        </tr>
                        <tr>
                            <td><strong>EMA-15</strong></td>
                            <td>₹{sample_data['RELIANCE']['ema_15']:.2f}</td>
                            <td class="negative">₹{(sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['ema_15']):.2f}</td>
                            <td class="negative">{((sample_data['RELIANCE']['current_price'] - sample_data['RELIANCE']['ema_15']) / sample_data['RELIANCE']['ema_15'] * 100):.2f}%</td>
                            <td class="negative">BELOW</td>
                            <td>2/(15+1) multiplier</td>
                        </tr>
                        <tr style="background: #f0f8ff; font-weight: bold;">
                            <td colspan="2"><strong>EMA Crossover Trend</strong></td>
                            <td colspan="2" class="negative">🔴 {sample_data['RELIANCE']['ema_trend'].upper()}</td>
                            <td colspan="2">EMA-9 < EMA-15</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="timestamp">
            Sample data from actual script outputs | August 22, 2025 15:15 | 64 trading days of data
        </div>
    </div>
</body>
</html>'''
    
    return html_content

def main():
    """Create and open demo dashboard"""
    current_dir = Path(__file__).parent
    demo_file = current_dir / 'demo_real_data.html'
    
    html_content = create_demo_dashboard()
    
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created demo dashboard: {demo_file}")
    print("🌐 Opening demo dashboard...")
    
    webbrowser.open(f'file://{demo_file.absolute()}')
    
    print("\n📊 Demo Features:")
    print("   • Exact table format for RSI, DMA, EMA")
    print("   • Real data values from actual script runs")
    print("   • Compact layout optimized for screen space")
    print("   • Color-coded signals (Green=Above, Red=Below)")
    print("   • Script source identification")

if __name__ == "__main__":
    main()