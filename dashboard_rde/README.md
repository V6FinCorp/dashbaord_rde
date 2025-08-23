# RSI, DMA & EMA Dashboard

## Overview
This dashboard combines the exact calculations from:
- RSI Scanner (rsi_scanner_final.py)
- TradingView-compatible DMA Calculator (tradingview_dma.py)  
- EMA Calculator (ema_calculator.py)

## Files Created (No Original Scripts Modified)

### dashboard_rde/ folder:
1. **dashboard.html** - Main dashboard interface
2. **app.py** - Flask web server (requires Flask installation)
3. **api_backend.py** - Backend API with exact calculations
4. **run_dashboard.py** - Auto-installer and runner
5. **standalone_dashboard.html** - No-dependency version
6. **README.md** - This file

## Quick Start

### Option 1: Standalone Dashboard (No Dependencies)
```bash
# Open the standalone HTML file in your browser
python standalone_runner.py
```

### Option 2: Full Web Dashboard (Requires Flask)
```bash
# Install dependencies and run
python run_dashboard.py
```

### Option 3: Manual Setup
```bash
# Install required packages
pip install flask flask-cors requests numpy tabulate

# Run the web server
python app.py

# Open browser to http://localhost:5000
```

## Features

### RSI Analysis
- Exact calculation from rsi_scanner_final.py
- 14-period RSI using Wilder's smoothing
- Overbought/Oversold signals

### DMA Analysis  
- Exact calculation from tradingview_dma.py
- DMA-10, DMA-20, DMA-50 periods
- Uses daily closing prices (TradingView compatible)
- Price difference analysis

### EMA Analysis
- Exact calculation from ema_calculator.py
- EMA-9, EMA-15 periods
- Exponential weighting formula
- Bullish/Bearish crossover analysis

## Available Symbols
- RELIANCE
- TCS  
- HDFCBANK
- INFY
- ICICIBANK

## Original Scripts (UNCHANGED)
- test_zone/rsi_scanner_final.py
- test_zone/tradingview_dma.py
- test_zone/ema_calculator.py
- test_zone/rsi_config.py
- dashboard/config_local.py

All original calculations preserved exactly as created.
