import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

# Disable GPU/MPS usage for consistency with training
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_MPS_ENABLED"] = "0"
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import tensorflow as tf
import requests
from espn_api.football import League
import logging
from model_service import PlayerValuationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fantasy Trade Analyzer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model service
model_service = None

class LeagueConnection(BaseModel):
    league_id: str
    espn_s2: str
    swid: str

class PlayerValuation(BaseModel):
    player_id: str

class TradeAnalysis(BaseModel):
    user_team_id: int
    partner_team_id: int
    user_players: List[str]
    partner_players: List[str]

@app.on_event("startup")
async def load_model_and_data():
    """Load the trained model and preprocessing data on startup"""
    global model_service
    
    try:
        # Initialize model service
        model_path = Path(__file__).parent.parent / "models" / "fp_model_final.keras"
        data_path = Path(__file__).parent.parent / "data" / "nfl_seasonal_preprocessed.csv"
        
        model_service = PlayerValuationService(str(model_path), str(data_path))
        
        if model_service.load_model_and_data():
            logger.info("✅ Model service initialized successfully")
        else:
            raise Exception("Failed to load model service")
        
    except Exception as e:
        logger.error(f"❌ Error loading model service: {e}")
        raise

def get_espn_league(league_id: str, espn_s2: str, swid: str):
    """Connect to ESPN Fantasy League"""
    try:
        league = League(
            league_id=int(league_id),
            year=2024,  # Current season
            espn_s2=espn_s2,
            swid=swid
        )
        return league
    except Exception as e:
        logger.error(f"Error connecting to ESPN league: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to connect to league: {str(e)}")

def format_team_data(team):
    """Format ESPN team data for frontend"""
    roster = []
    for player in team.roster:
        roster.append({
            "playerId": str(player.playerId),
            "name": player.name,
            "position": player.position,
            "team": getattr(player, 'proTeam', 'N/A'),
            "injuryStatus": getattr(player, 'injuryStatus', None),
            "projectedPoints": getattr(player, 'projected_points', 0)
        })
    
    return {
        "id": team.team_id,
        "name": team.team_name,
        "owner": team.owner,
        "wins": team.wins,
        "losses": team.losses,
        "roster": roster
    }


@app.post("/api/connect-league")
async def connect_league(connection: LeagueConnection):
    """Connect to ESPN Fantasy League and return league/team data"""
    try:
        league = get_espn_league(connection.league_id, connection.espn_s2, connection.swid)
        
        # Format league data
        league_data = {
            "id": league.league_id,
            "name": getattr(league, 'settings', {}).get('name', f'League {league.league_id}'),
            "size": len(league.teams)
        }
        
        # Format team data
        teams_data = []
        user_team = None
        
        for team in league.teams:
            team_data = format_team_data(team)
            teams_data.append(team_data)
            
            # Assume the first team is the user's team for now
            # In a real app, you'd determine this based on authentication
            if user_team is None:
                user_team = team_data
        
        return {
            "league": league_data,
            "teams": teams_data,
            "user_team": user_team
        }
        
    except Exception as e:
        logger.error(f"Error in connect_league: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/player-valuation")
async def get_player_valuation(player_data: PlayerValuation):
    """Get AI-predicted fantasy points for a player"""
    try:
        if not model_service or not model_service.is_loaded():
            raise HTTPException(status_code=500, detail="Model service not loaded")
        
        # For demo purposes, create mock player data
        # In production, you'd fetch actual player stats from a database
        mock_player_data = {
            "playerId": player_data.player_id,
            "position": "RB",  # Default position - would be fetched from database
            "projectedPoints": 150  # Default projection - would be current season projection
        }
        
        # Get prediction from model service
        predicted_points = model_service.predict_fantasy_points(mock_player_data)
        
        return {"predicted_points": predicted_points}
        
    except Exception as e:
        logger.error(f"Error in player valuation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-trade")
async def analyze_trade(trade: TradeAnalysis):
    """Analyze the impact of a proposed trade"""
    try:
        if not model_service or not model_service.is_loaded():
            raise HTTPException(status_code=500, detail="Model service not loaded")
        
        # Create mock player data for analysis
        # In production, you'd fetch actual player data from database
        user_players_data = []
        partner_players_data = []
        
        for player_id in trade.user_players:
            user_players_data.append({
                "playerId": player_id,
                "position": "RB",  # Would be fetched from database
                "projectedPoints": 150
            })
        
        for player_id in trade.partner_players:
            partner_players_data.append({
                "playerId": player_id,
                "position": "WR",  # Would be fetched from database
                "projectedPoints": 140
            })
        
        # Analyze trade using model service
        analysis = model_service.analyze_trade_impact(user_players_data, partner_players_data)
        
        return {
            "user_current_total": 1000,  # Mock current team total
            "user_new_total": 1000 + analysis['user_net_change'],
            "user_point_change": analysis['user_net_change'],
            "partner_current_total": 1000,  # Mock partner team total
            "partner_new_total": 1000 + analysis['partner_net_change'],
            "partner_point_change": analysis['partner_net_change'],
            "recommendation": analysis['recommendation']
        }
        
    except Exception as e:
        logger.error(f"Error in trade analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model_service is not None and model_service.is_loaded(),
        "feature_count": len(model_service.feature_columns) if model_service and model_service.feature_columns else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
