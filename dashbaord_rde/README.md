# Technical Analysis Dashboard 📊

A comprehensive Flask-based technical analysis dashboard for Indian stock market monitoring, optimized for Railway.app deployment.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YourTemplateID)

## 🌟 Features

### Technical Indicators
- **RSI-14**: Relative Strength Index with overbought/oversold signals
- **DMA Analysis**: Displaced Moving Averages (10, 20, 50 periods)
- **EMA Analysis**: Exponential Moving Averages (9, 15 periods) with crossover signals

### Dashboard Capabilities
- **16 Indian Stocks**: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, AXISBANK, KOTAKBANK, SBIN, MARUTI, ASIANPAINT, HINDUNILVR, NESTLEIND, BAJFINANCE, BAJAJFINSV, BHARTIARTL, WIPRO
- **Real-time Data**: Live API endpoints with JSON responses
- **Interactive UI**: Dark/light theme toggle, responsive design
- **Detailed Analysis**: 5-day hourly historical data with sorting capabilities
- **Mobile Optimized**: Responsive layout for all devices

## 🚀 Quick Deploy to Railway

### One-Click Deploy
1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Fork this repository
4. Railway will automatically deploy your app

### Manual Deploy
1. Fork this repository
2. Connect Railway to your GitHub account
3. Import this repository in Railway
4. Railway will auto-detect the Python environment and deploy

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/dashbaord_rde.git
   cd dashbaord_rde
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   Open your browser to `http://localhost:5000`

## 📁 Project Structure

```
dashbaord_rde/
├── app.py                 # Flask backend with API endpoints
├── dashboard.html         # Frontend dashboard interface
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version for Railway
├── Procfile              # Railway/Heroku process configuration
├── railway.json          # Railway-specific settings
├── .gitignore           # Git ignore rules
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000

# Optional: Add your own configurations
SECRET_KEY=your-secret-key-here
```

### Railway Configuration
The `railway.json` file contains Railway-specific settings:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT app:app",
    "healthcheckPath": "/health"
  }
}
```

## 📡 API Endpoints

### Stock Data API
- **GET** `/api/data/<symbol>` - Get complete technical analysis for a symbol
- **GET** `/health` - Health check endpoint
- **GET** `/` - Main dashboard interface

### Response Format
```json
{
  "status": "success",
  "data": {
    "symbol": "RELIANCE",
    "current_price": 1409.90,
    "data_points": 64,
    "rsi": {
      "rsi_14": {
        "value": 52.34,
        "signal": "NEUTRAL",
        "interpretation": "Normal Range"
      }
    },
    "dma": {
      "dma_10": {
        "value": 1405.23,
        "difference": 4.67,
        "difference_pct": 0.33,
        "signal": "ABOVE"
      }
    },
    "ema": {
      "ema_9": {
        "value": 1408.12,
        "difference": 1.78,
        "difference_pct": 0.13
      }
    }
  }
}
```

## 🎨 Theme Support

The dashboard supports both light and dark themes with automatic persistence:

- **Light Theme**: Clean, professional appearance
- **Dark Theme**: Reduced eye strain for extended use
- **Auto-Save**: Theme preference saved in localStorage

## 📱 Responsive Design

Optimized for all screen sizes:
- **Desktop**: Full featured layout with side-by-side tables
- **Tablet**: Stacked layout with touch-friendly controls
- **Mobile**: Compact layout with horizontal scrolling tables

## 🔍 Technical Analysis Details

### RSI (Relative Strength Index)
- **Period**: 14 days
- **Overbought**: > 70
- **Oversold**: < 30
- **Calculation**: Wilder's Smoothing method

### DMA (Displaced Moving Average)
- **Periods**: 10, 20, 50 days
- **Calculation**: Simple Moving Average of daily closing prices
- **Signals**: Above/Below current price analysis

### EMA (Exponential Moving Average)
- **Periods**: 9, 15 days
- **Calculation**: Exponential weighting with trend analysis
- **Crossover**: EMA-9 vs EMA-15 trend detection

## 🚀 Performance Features

### Backend Optimizations
- **Gunicorn**: Production WSGI server with optimized worker configuration
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Checks**: Railway health monitoring endpoint
- **Environment Detection**: Automatic port binding for cloud deployment

### Frontend Optimizations
- **Vanilla JavaScript**: No heavy frameworks, fast loading
- **CSS Variables**: Dynamic theming with optimal performance
- **Responsive Tables**: Efficient rendering for large datasets
- **Local Storage**: Client-side preference caching

## 🔒 Security Features

- **Environment Variables**: Sensitive configuration externalized
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: Symbol parameter validation
- **Error Handling**: Graceful error responses

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in .env file or use environment variable
   export PORT=8000
   python app.py
   ```

2. **Module Not Found**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

3. **Railway Deployment Issues**
   - Ensure `runtime.txt` specifies Python 3.11
   - Check `Procfile` contains correct start command
   - Verify all files are committed to git

## 📈 Future Enhancements

- [ ] Real market data integration
- [ ] Additional technical indicators (MACD, Bollinger Bands)
- [ ] Websocket support for real-time updates
- [ ] User authentication and portfolio tracking
- [ ] Export functionality (PDF, CSV)
- [ ] Alert system for technical signals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [Your Railway App URL]
- **Railway Template**: [Template Link]
- **GitHub Repository**: [Repository Link]

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team

---

**Built with ❤️ for the Indian Stock Market Community**

*Deployed on Railway.app with ⚡ lightning-fast performance*