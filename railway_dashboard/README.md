# Railway Deployment - Technical Analysis Dashboard

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/dashboard-template)

## 📊 Features

- **RSI Analysis**: 14-period RSI with overbought/oversold signals
- **DMA Analysis**: 10/20/50 period moving averages with TradingView compatibility  
- **EMA Analysis**: 9/15 period exponential moving averages with crossover trends
- **Real-time Data**: Mock data simulation for testing and demo
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle between themes
- **Multi-Symbol Support**: 16+ Indian stock symbols

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Railway.app
- **APIs**: RESTful JSON endpoints

## 🔧 Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd railway_dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🌐 Railway Deployment

### Method 1: One-Click Deploy
1. Click the "Deploy on Railway" button above
2. Connect your GitHub repository
3. Railway will automatically deploy

### Method 2: Manual Deploy
1. Create new project on [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects Python and uses `Procfile`
4. Set environment variables if needed
5. Deploy automatically

### Environment Variables (Optional)
- `PORT` - Automatically set by Railway
- `FLASK_ENV` - Set to `production` 
- `PYTHONPATH` - Auto-configured

## 📁 Project Structure

```
railway_dashboard/
├── app.py              # Main Flask application
├── dashboard.html      # Frontend dashboard
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── runtime.txt        # Python version specification
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🔌 API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/symbols` - List of available symbols
- `GET /api/data/<symbol>` - Technical analysis data for symbol
- `GET /health` - Health check endpoint
- `GET /api/health` - API health status

## 📈 Supported Symbols

- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- KOTAKBANK, HINDUNILVR, BHARTIARTL, SBIN
- BAJFINANCE, MARUTI, ASIANPAINT, NESTLEIND
- AXISBANK, BAJAJFINSV, WIPRO

## 🎯 Technical Indicators

### RSI (Relative Strength Index)
- **Period**: 14
- **Calculation**: Wilder's Smoothing
- **Signals**: Overbought (>70), Oversold (<30), Neutral

### DMA (Displaced Moving Average)
- **Periods**: 10, 20, 50 days
- **Calculation**: Simple Moving Average of daily closes
- **Signals**: Above/Below current price
- **Compatibility**: TradingView standard

### EMA (Exponential Moving Average)
- **Periods**: 9, 15 days
- **Calculation**: Exponential weighting formula
- **Signals**: Bullish/Bearish crossover trends
- **Analysis**: Price vs EMA difference in ₹ and %

## 🎨 Dashboard Features

- **Real-time Updates**: Auto-refresh data
- **Symbol Selection**: Dropdown with major Indian stocks
- **Color Coding**: Green (bullish), Red (bearish), Gray (neutral)
- **Responsive Tables**: Optimized for all screen sizes
- **Detail Tabs**: Hourly analysis for last 5 trading days
- **Sort Functionality**: Click column headers to sort
- **Theme Toggle**: Switch between light and dark modes

## 🔄 Data Flow

1. User selects symbol from dropdown
2. Frontend calls `/api/data/<symbol>`
3. Backend generates realistic mock data
4. Technical indicators calculated
5. Results displayed in responsive tables
6. Auto-refresh every 30 seconds

## 🚨 Production Notes

- Currently uses **mock data** for demonstration
- Ready for real API integration
- Optimized for Railway's infrastructure
- Auto-scaling enabled
- Health checks configured

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues or questions:
- Create GitHub issue
- Check Railway documentation
- Review Flask documentation

---

**🎯 Ready to deploy? Click the Railway button above!**