# Fantasy Football Trade Analyzer - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Setup Environment
```bash
python3 setup.py
```

### 2. Start Backend
```bash
./start_backend.sh
```

### 3. Start Frontend
```bash
./start_frontend.sh
```

Then open http://localhost:3000 in your browser!

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **ESPN Fantasy Football League** (2024 season)
- Your trained model: `models/fp_model_final.keras`
- Your preprocessed data: `data/nfl_seasonal_preprocessed.csv`

## 🔑 Getting ESPN Credentials

1. **Log into ESPN Fantasy** in your browser
2. **Open Developer Tools** (F12 or right-click → Inspect)
3. **Go to Application tab** → Storage → Cookies → espn.com
4. **Copy these values:**
   - `ESPN_S2` (long string starting with AEB...)
   - `SWID` (string in format {ABC-DEF-...})

## 🎯 How to Use

1. **Connect League**: Enter your ESPN credentials and league ID
2. **View Teams**: Browse all teams and their rosters with AI valuations
3. **Analyze Trades**: Select players from two teams to see projected impact
4. **Make Decisions**: Use AI recommendations to evaluate trade fairness

## 🔧 Troubleshooting

### Backend Issues
- **Model not loading**: Check `models/fp_model_final.keras` exists
- **Data not found**: Verify `data/nfl_seasonal_preprocessed.csv` exists
- **Dependencies**: Run `pip install -r backend/requirements.txt`

### Frontend Issues
- **Won't start**: Run `npm install` in `fantasy-trade-app/` directory
- **API errors**: Ensure backend is running on port 8000
- **CORS issues**: Check backend allows localhost:3000

### ESPN Connection Issues
- **Invalid credentials**: Get fresh cookies from browser
- **League not found**: Verify league ID is correct
- **Private league**: Ensure you're a member of the league

## 📊 Features Overview

### 🤖 AI Player Valuations
- Uses your trained TensorFlow model
- Predicts season-long fantasy points
- Accounts for position, stats, and trends

### 📈 Trade Analysis
- Compares player values in proposed trades
- Shows net point impact for both teams
- Provides intelligent recommendations

### 🎨 Modern Interface
- Clean, responsive design
- Real-time calculations
- Easy team and player selection

## 🏗️ Project Structure

```
FP_Tensorflow/
├── models/
│   └── fp_model_final.keras          # Your trained model
├── data/
│   └── nfl_seasonal_preprocessed.csv # Your training data
├── backend/                          # FastAPI server
│   ├── main.py                      # API endpoints
│   ├── model_service.py             # ML inference
│   └── requirements.txt             # Python dependencies
├── fantasy-trade-app/               # React frontend
│   ├── src/
│   │   ├── components/              # UI components
│   │   ├── context/                 # State management
│   │   └── App.js                   # Main app
│   └── package.json                 # Node dependencies
├── setup.py                         # Environment setup
├── start_backend.sh                 # Backend launcher
├── start_frontend.sh                # Frontend launcher
└── README.md                        # Full documentation
```

## 🔗 Useful Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 💡 Tips for Success

1. **Fresh Cookies**: ESPN cookies expire, get new ones if connection fails
2. **League Access**: You must be a member of the league to access data
3. **Model Performance**: Results depend on your model's training quality
4. **Trade Context**: Consider bye weeks, injuries, and team needs beyond points
5. **Regular Updates**: Restart backend if you update the model

## 🆘 Need Help?

1. Check the health endpoint: http://localhost:8000/api/health
2. Look at browser console for frontend errors
3. Check terminal output for backend errors
4. Verify all files are in correct locations
5. Ensure ESPN credentials are current

Happy trading! 🏈📊
