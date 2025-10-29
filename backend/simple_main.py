from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import logging
from espn_service import ESPNService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fantasy Trade Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ESPN service
espn_service = ESPNService()

class LeagueConnection(BaseModel):
    league_id: str
    espn_s2: str = None
    swid: str = None

class CookieExtraction(BaseModel):
    cookies: str  # Full cookie string from browser

class TradeAnalysis(BaseModel):
    team1_players: List[Dict]
    team2_players: List[Dict]

@app.post("/api/extract-cookies")
async def extract_cookies(extraction: CookieExtraction):
    """Extract ESPN cookies from browser cookie string"""
    try:
        logger.info("Extracting ESPN cookies from browser string")
        
        espn_s2, swid = espn_service.extract_cookies_from_string(extraction.cookies)
        
        if espn_s2 and swid:
            return {
                "success": True,
                "espn_s2": espn_s2,
                "swid": swid,
                "message": "Successfully extracted ESPN cookies"
            }
        else:
            raise HTTPException(status_code=400, detail="Could not find ESPN_S2 and SWID cookies in the provided string")
            
    except Exception as e:
        logger.error(f"Cookie extraction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/connect-league")
async def connect_league(connection: LeagueConnection):
    """Connect to ESPN league and fetch real data"""
    try:
        logger.info(f"Connecting to ESPN league: {connection.league_id}")
        
        # Try with cookies first, then fallback to public
        if connection.espn_s2 and connection.swid:
            league_data = espn_service.connect_with_cookies(
                league_id=connection.league_id,
                espn_s2=connection.espn_s2,
                swid=connection.swid
            )
        else:
            # Try as public league
            league_data = espn_service.connect_public_league(connection.league_id)
        
        logger.info(f"Successfully connected to league: {league_data['league']['name']}")
        return league_data
        
    except Exception as e:
        logger.error(f"Failed to connect to league: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/analyze-trade")
async def analyze_trade(trade: TradeAnalysis):
    """Analyze a proposed trade between two teams"""
    try:
        logger.info("Analyzing trade proposal")
        
        # Calculate values for both sides
        team1_value = espn_service.calculate_trade_value(trade.team1_players)
        team2_value = espn_service.calculate_trade_value(trade.team2_players)
        
        # Determine trade fairness
        value_difference = abs(team1_value['total_value'] - team2_value['total_value'])
        fairness_threshold = 5.0  # Points threshold for "fair" trade
        
        is_fair = value_difference <= fairness_threshold
        
        # Determine winner
        if team1_value['total_value'] > team2_value['total_value']:
            winner = "team1"
            advantage = team1_value['total_value'] - team2_value['total_value']
        elif team2_value['total_value'] > team1_value['total_value']:
            winner = "team2"
            advantage = team2_value['total_value'] - team1_value['total_value']
        else:
            winner = "tie"
            advantage = 0
        
        return {
            "team1_value": team1_value,
            "team2_value": team2_value,
            "is_fair": is_fair,
            "winner": winner,
            "advantage": round(advantage, 2),
            "recommendation": "Accept" if is_fair else f"Decline - {winner} wins by {advantage:.1f} points"
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze trade: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/select-team")
async def select_team(team_selection: dict):
    """Allow user to manually select their team"""
    try:
        team_id = team_selection.get('team_id')
        if not team_id:
            raise HTTPException(status_code=400, detail="Team ID is required")
        
        if not espn_service.current_league:
            raise HTTPException(status_code=400, detail="No league connected")
        
        # Find the selected team
        selected_team = None
        for team in espn_service.current_league.teams:
            if team.team_id == int(team_id):
                selected_team = espn_service._parse_team_from_api(team)
                break
        
        if not selected_team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        logger.info(f"User manually selected team: {selected_team['name']}")
        return {"success": True, "selected_team": selected_team}
        
    except Exception as e:
        logger.error(f"Failed to select team: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/roster/{team_id}")
async def get_team_roster(team_id: int):
    """Get detailed roster information for a specific team"""
    try:
        if not espn_service.current_league:
            raise HTTPException(status_code=400, detail="No league connected")
        
        # Find the team
        target_team = None
        for team in espn_service.current_league.teams:
            if team.team_id == team_id:
                target_team = team
                break
        
        if not target_team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Parse team with full roster
        team_data = espn_service._parse_team_from_api(target_team)
        
        # Organize roster by position
        roster_by_position = {
            'QB': [],
            'RB': [],
            'WR': [],
            'TE': [],
            'K': [],
            'D/ST': [],
            'BENCH': []
        }
        
        starters = []
        bench = []
        
        for player in team_data['roster']:
            position = player['position']
            if position in roster_by_position:
                roster_by_position[position].append(player)
            
            if player['is_starter']:
                starters.append(player)
            else:
                bench.append(player)
        
        return {
            "team": {
                "id": team_data['id'],
                "name": team_data['name'],
                "owner": team_data['owner'],
                "record": f"{team_data['wins']}-{team_data['losses']}"
            },
            "roster": {
                "all_players": team_data['roster'],
                "by_position": roster_by_position,
                "starters": starters,
                "bench": bench,
                "total_players": len(team_data['roster'])
            },
            "team_stats": {
                "total_points": sum(p['season_points'] for p in team_data['roster']),
                "avg_starter_points": sum(p['avg_points'] for p in starters) / max(1, len(starters)),
                "projected_points": sum(p['projected_points'] for p in starters)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get roster: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "espn_integration": True, "message": "ESPN Fantasy API connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
