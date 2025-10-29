# Fantasy Football Trade Analyzer

A modern web application that connects to your ESPN Fantasy Football league and uses AI-powered player valuations to analyze potential trades. Built with React frontend and FastAPI backend, leveraging a trained TensorFlow model to predict fantasy points.

## Features

- 🔗 **ESPN League Integration**: Connect your ESPN Fantasy Football league using cookies
- 🤖 **AI Player Valuations**: Uses your trained `fp_model_final.keras` model to predict season fantasy points
- 📊 **Trade Analysis**: Compare trade scenarios and see projected point impacts
- 💻 **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- ⚡ **Real-time Updates**: Live trade calculations and team comparisons

## Architecture

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS with custom components
- **State Management**: Context API for league data
- **Routing**: React Router for navigation
- **HTTP Client**: Axios for API communication

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **ML Integration**: TensorFlow model inference
- **ESPN API**: espn-api library for league data
- **Data Processing**: Pandas and NumPy for feature engineering

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Your trained `fp_model_final.keras` model
- ESPN Fantasy Football league access

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the API server**:
   ```bash
   python simple_main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd fantasy-trade-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   
   The app will open at `http://localhost:3000`

## Getting ESPN Credentials

To connect your ESPN Fantasy league, you'll need two cookie values:

1. **Log into ESPN Fantasy** in your browser
2. **Open Developer Tools** (F12)
3. **Go to Application/Storage → Cookies → espn.com**
4. **Copy the values** for `ESPN_S2` and `SWID`

These cookies authenticate your access to private league data.

## How It Works

### Player Valuation Model
The application uses your pre-trained `fp_model_final.keras` model which:
- Predicts season-long fantasy points for NFL players
- Takes player statistics and metadata as input features
- Outputs projected fantasy points for the remainder of the season

### Trade Analysis Process
1. **Connect League**: Fetch team rosters and player data from ESPN
2. **Value Players**: Run each player through the AI model for projections
3. **Compare Trades**: Calculate point differences between proposed trades
4. **Generate Insights**: Provide recommendations based on projected impacts

### Feature Engineering
The model expects the same features used during training:
- Player statistics (passing, rushing, receiving)
- Efficiency metrics (yards per attempt, catch rate, etc.)
- Positional indicators (QB, RB, WR, TE flags)
- Experience factors (years in league, draft position)

## API Endpoints

### `POST /api/connect-league`
Connect to ESPN Fantasy league
```json
{
  "league_id": "123456",
  "espn_s2": "cookie_value",
  "swid": "cookie_value"
}
```

### `POST /api/player-valuation`
Get AI prediction for a player
```json
{
  "player_id": "player_id"
}
```

### `POST /api/analyze-trade`
Analyze a proposed trade
```json
{
  "user_team_id": 1,
  "partner_team_id": 2,
  "user_players": ["player1", "player2"],
  "partner_players": ["player3", "player4"]
}
```

## Model Integration

The application integrates with your existing TensorFlow model:

1. **Model Loading**: Loads `fp_model_final.keras` on startup
2. **Feature Preparation**: Creates feature vectors matching training data
3. **Preprocessing**: Applies same scaling used during training
4. **Inference**: Generates predictions for fantasy points
5. **Trade Calculations**: Compares player values for trade analysis

## Customization

### Adding New Features
To add new player features to the model:
1. Update feature engineering in `backend/main.py`
2. Ensure features match your training data columns
3. Update the preprocessing pipeline accordingly

### UI Modifications
The frontend uses Tailwind CSS for styling:
- Modify components in `src/components/`
- Update styles in component files
- Customize theme in `tailwind.config.js`

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure `fp_model_final.keras` is in the correct path
2. **ESPN Connection Fails**: Verify cookies are current and league ID is correct
3. **Feature Mismatch**: Check that model expects the same features as training
4. **CORS Issues**: Ensure backend allows frontend origin in CORS settings

### Debug Mode
Enable debug logging by setting log level in `backend/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- 📱 Mobile-responsive design improvements
- 🔄 Real-time league updates via WebSocket
- 📈 Historical trade analysis and tracking
- 🎯 Position-specific trade recommendations
- 🏆 League standings and playoff implications
- 📊 Advanced analytics and visualizations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and personal use. ESPN data usage should comply with their Terms of Service.
