import requests
from typing import Dict, List, Optional
import logging
from espn_api.football import League
import urllib.parse

logger = logging.getLogger(__name__)

class ESPNService:
    def __init__(self):
        self.current_league = None
    
    def extract_cookies_from_string(self, cookie_string: str) -> tuple:
        """Extract ESPN_S2 and SWID from full cookie string"""
        try:
            espn_s2 = None
            swid = None
            
            # Parse cookie string
            cookies = cookie_string.split(';')
            for cookie in cookies:
                cookie = cookie.strip()
                if cookie.startswith('ESPN_S2='):
                    espn_s2 = cookie.split('=', 1)[1]
                elif cookie.startswith('SWID='):
                    swid = cookie.split('=', 1)[1]
            
            return espn_s2, swid
            
        except Exception as e:
            logger.error(f"Failed to extract cookies: {e}")
            return None, None
    
    def connect_with_cookies(self, league_id: str, espn_s2: str = None, swid: str = None) -> Dict:
        """Connect to ESPN league using cookies (most reliable method)"""
        try:
            logger.info(f"Connecting to ESPN league {league_id} with cookies")
            logger.info(f"Raw ESPN_S2: {espn_s2[:50] if espn_s2 else 'None'}...")
            logger.info(f"Raw SWID: {swid}")
            
            # Decode URL-encoded cookies
            if espn_s2:
                espn_s2_decoded = urllib.parse.unquote(espn_s2)
                logger.info(f"Decoded ESPN_S2: {espn_s2_decoded[:50]}...")
            else:
                espn_s2_decoded = None
                
            if swid:
                swid_decoded = urllib.parse.unquote(swid)
                logger.info(f"Decoded SWID: {swid_decoded}")
            else:
                swid_decoded = None
            
            # Try multiple years - ESPN leagues can be 2024 or 2025
            years_to_try = [2025, 2024, 2023]
            league = None
            
            for year in years_to_try:
                try:
                    logger.info(f"Trying year {year}")
                    if espn_s2_decoded and swid_decoded:
                        logger.info(f"Attempting connection with both cookies for year {year}")
                        league = League(league_id=int(league_id), year=year, espn_s2=espn_s2_decoded, swid=swid_decoded)
                    else:
                        logger.info(f"Attempting public league connection for year {year}")
                        league = League(league_id=int(league_id), year=year)
                    
                    # If we get here, connection succeeded
                    logger.info(f"Successfully connected to league: {league.settings.name} (Year: {year})")
                    self.current_league = league
                    return self._parse_league_from_api(league, user_swid=swid_decoded)
                    
                except Exception as year_error:
                    logger.info(f"Year {year} failed: {year_error}")
                    continue
            
            if not league:
                raise Exception("Could not connect to league in any year (2023-2025)")
            
            self.current_league = league
            return self._parse_league_from_api(league)
            
        except Exception as e:
            logger.error(f"Failed to connect with cookies: {e}")
            logger.error(f"Exception type: {type(e)}")
            raise Exception(f"Failed to connect to ESPN league: {str(e)}")
    
    def connect_public_league(self, league_id: str) -> Dict:
        """Connect to a public ESPN league (no authentication needed)"""
        try:
            logger.info(f"Connecting to public ESPN league {league_id}")
            
            league = League(league_id=int(league_id), year=2024)
            self.current_league = league
            return self._parse_league_from_api(league)
            
        except Exception as e:
            logger.error(f"Failed to connect to public league: {e}")
            raise Exception(f"Failed to connect to ESPN league: {str(e)}")
    
    def _parse_league_from_api(self, league, user_swid=None) -> Dict:
        """Parse ESPN API league object into our format"""
        try:
            logger.info(f"Parsing league data...")
            logger.info(f"League ID: {league.league_id}")
            logger.info(f"League settings: {dir(league.settings)}")
            logger.info(f"Number of teams: {len(league.teams)}")
            logger.info(f"User SWID: {user_swid}")
            
            # Parse league info
            league_name = getattr(league.settings, 'name', f'League {league.league_id}')
            logger.info(f"League name: {league_name}")
            
            league_info = {
                'id': str(league.league_id),
                'name': league_name,
                'size': len(league.teams),
                'scoring_type': 'STANDARD',  # Could be enhanced to detect actual scoring
                'current_week': getattr(league, 'current_week', 1)
            }
            
            # Parse teams
            teams = []
            user_team = None
            
            for i, team in enumerate(league.teams):
                logger.info(f"Parsing team {i+1}: {dir(team)}")
                team_data = self._parse_team_from_api(team)
                teams.append(team_data)
                
                # Try to identify user's team by SWID
                if user_swid and self._is_user_team(team, user_swid):
                    logger.info(f"Found user team: {team_data['name']}")
                    user_team = team_data
            
            # If we couldn't identify user team, default to first team but mark it as uncertain
            if not user_team and teams:
                user_team = teams[0]
                user_team['uncertain_ownership'] = True
                logger.warning(f"Could not identify user team, defaulting to: {user_team['name']}")
            
            return {
                'league': league_info,
                'teams': teams,
                'user_team': user_team
            }
            
        except Exception as e:
            logger.error(f"Error parsing league data: {e}")
            logger.error(f"Exception details: {type(e)}")
            raise Exception("Invalid league data format")
    
    def _parse_team_from_api(self, team) -> Dict:
        """Parse ESPN API team object into our format"""
        try:
            logger.info(f"Team attributes: {[attr for attr in dir(team) if not attr.startswith('_')]}")
            
            # Try different ways to get team name
            team_name = "Unknown Team"
            if hasattr(team, 'team_name') and team.team_name:
                team_name = team.team_name
            elif hasattr(team, 'name') and team.name:
                team_name = team.name
            elif hasattr(team, 'location') and hasattr(team, 'nickname'):
                team_name = f"{team.location} {team.nickname}".strip()
            
            # Try different ways to get owner
            owner = "Unknown"
            if hasattr(team, 'owner') and team.owner:
                owner = team.owner
            elif hasattr(team, 'primary_owner') and team.primary_owner:
                owner = team.primary_owner
            
            # Try different ways to get record
            wins = getattr(team, 'wins', 0)
            losses = getattr(team, 'losses', 0)
            
            # Try to get points
            points_for = 0
            points_against = 0
            
            if hasattr(team, 'points_for'):
                points_for = team.points_for
            elif hasattr(team, 'record') and hasattr(team.record, 'points_for'):
                points_for = team.record.points_for
                
            if hasattr(team, 'points_against'):
                points_against = team.points_against
            elif hasattr(team, 'record') and hasattr(team.record, 'points_against'):
                points_against = team.record.points_against
            
            logger.info(f"Parsed team: {team_name} (Owner: {owner}, Record: {wins}-{losses})")
            
            team_data = {
                'id': getattr(team, 'team_id', 0),
                'name': team_name,
                'owner': owner,
                'wins': wins,
                'losses': losses,
                'points_for': points_for,
                'points_against': points_against,
                'roster': []
            }
            
            # Parse full roster
            if hasattr(team, 'roster') and team.roster:
                logger.info(f"Parsing {len(team.roster)} players for team {team_name}")
                for i, player in enumerate(team.roster):
                    try:
                        player_data = self._parse_player_from_api(player)
                        if player_data:
                            team_data['roster'].append(player_data)
                        
                        # Limit detailed logging to first few players to avoid spam
                        if i >= 3:
                            logger.info(f"... parsing remaining {len(team.roster) - i - 1} players (logging reduced)")
                            break
                    except Exception as player_error:
                        logger.error(f"Error parsing player {i+1}: {player_error}")
                        continue
                        
                # Parse remaining players without detailed logging
                for player in team.roster[4:]:
                    try:
                        player_data = self._parse_player_from_api(player)
                        if player_data:
                            team_data['roster'].append(player_data)
                    except Exception as player_error:
                        continue
            
            return team_data
            
        except Exception as e:
            logger.error(f"Error parsing team data: {e}")
            logger.error(f"Team object type: {type(team)}")
            return {
                'id': getattr(team, 'team_id', 0),
                'name': 'Unknown Team',
                'owner': 'Unknown',
                'wins': 0,
                'losses': 0,
                'points_for': 0,
                'points_against': 0,
                'roster': []
            }
    
    def _is_user_team(self, team, user_swid: str) -> bool:
        """Check if this team belongs to the user based on SWID"""
        try:
            # Clean up SWID format (remove braces if present)
            clean_user_swid = user_swid.strip('{}')
            logger.info(f"Looking for user SWID: {clean_user_swid}")
            
            # Check all possible team owner attributes
            team_name = getattr(team, 'team_name', 'Unknown')
            logger.info(f"Checking team: {team_name}")
            logger.info(f"Team attributes: {[attr for attr in dir(team) if 'owner' in attr.lower()]}")
            
            # Try different owner attributes
            owner_sources = []
            
            if hasattr(team, 'owners'):
                owner_sources.append(('owners', team.owners))
            if hasattr(team, 'owner'):
                owner_sources.append(('owner', team.owner))
            if hasattr(team, 'primary_owner'):
                owner_sources.append(('primary_owner', team.primary_owner))
            if hasattr(team, 'owner_id'):
                owner_sources.append(('owner_id', team.owner_id))
                
            logger.info(f"Found owner sources: {[source[0] for source in owner_sources]}")
            
            for source_name, owner_data in owner_sources:
                logger.info(f"Checking {source_name}: {owner_data} (type: {type(owner_data)})")
                
                if isinstance(owner_data, list):
                    for owner in owner_data:
                        if self._check_owner_match(owner, clean_user_swid):
                            logger.info(f"MATCH FOUND in {source_name}!")
                            return True
                else:
                    if self._check_owner_match(owner_data, clean_user_swid):
                        logger.info(f"MATCH FOUND in {source_name}!")
                        return True
            
            logger.info(f"No match found for team {team_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking team ownership: {e}")
            return False
    
    def _check_owner_match(self, owner, clean_user_swid: str) -> bool:
        """Check if a single owner matches the user SWID"""
        try:
            if owner is None:
                return False
                
            # If owner has an id attribute
            if hasattr(owner, 'id') and owner.id:
                owner_id = str(owner.id).strip('{}')
                logger.info(f"  Comparing owner.id '{owner_id}' with user '{clean_user_swid}'")
                if owner_id == clean_user_swid:
                    return True
                    
            # If owner is a string (SWID)
            if isinstance(owner, str):
                owner_clean = owner.strip('{}')
                logger.info(f"  Comparing owner string '{owner_clean}' with user '{clean_user_swid}'")
                if owner_clean == clean_user_swid:
                    return True
                    
            # If owner is a dict with id
            if isinstance(owner, dict) and 'id' in owner:
                owner_id = str(owner['id']).strip('{}')
                logger.info(f"  Comparing owner dict id '{owner_id}' with user '{clean_user_swid}'")
                if owner_id == clean_user_swid:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error in owner match check: {e}")
            return False
    
    def _parse_player_from_api(self, player) -> Optional[Dict]:
        """Parse ESPN API player object into our format"""
        try:
            # Debug: Log available player attributes
            logger.info(f"Parsing player: {getattr(player, 'name', 'Unknown')}")
            logger.info(f"Player attributes: {[attr for attr in dir(player) if not attr.startswith('_')]}")
            
            # Basic player info
            player_id = getattr(player, 'playerId', 0)
            name = getattr(player, 'name', 'Unknown Player')
            
            # Position handling
            position = 'UNKNOWN'
            if hasattr(player, 'position'):
                position = player.position
            elif hasattr(player, 'eligibleSlots'):
                # Map slot IDs to positions (ESPN uses numeric slots)
                slot_map = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE', 16: 'D/ST', 17: 'K'}
                eligible_slots = getattr(player, 'eligibleSlots', [])
                if eligible_slots and eligible_slots[0] in slot_map:
                    position = slot_map[eligible_slots[0]]
            
            # Team info
            pro_team = 'FA'
            if hasattr(player, 'proTeam'):
                pro_team = player.proTeam
            elif hasattr(player, 'team'):
                pro_team = getattr(player.team, 'abbrev', 'FA') if hasattr(player.team, 'abbrev') else 'FA'
            
            # Injury status
            injury_status = 'ACTIVE'
            if hasattr(player, 'injuryStatus'):
                injury_status = player.injuryStatus
            elif hasattr(player, 'injured'):
                injury_status = 'INJURED' if player.injured else 'ACTIVE'
            
            # Points and stats
            projected_points = 0
            season_points = 0
            avg_points = 0
            
            # Try multiple ways to get points
            if hasattr(player, 'projected_total_points'):
                projected_points = player.projected_total_points or 0
            elif hasattr(player, 'projected_points'):
                projected_points = player.projected_points or 0
                
            if hasattr(player, 'total_points'):
                season_points = player.total_points or 0
            elif hasattr(player, 'points'):
                season_points = player.points or 0
            elif hasattr(player, 'stats'):
                # Try to extract from stats object
                try:
                    stats = player.stats
                    if isinstance(stats, dict) and 'points' in stats:
                        season_points = stats['points']
                except:
                    pass
            
            # Calculate average (assuming we're in week 8-12 range)
            current_week = 8  # Could be dynamic
            avg_points = season_points / max(1, current_week) if season_points > 0 else 0
            
            # Lineup slot
            lineup_slot = 'BENCH'
            if hasattr(player, 'slot_position'):
                lineup_slot = player.slot_position
            elif hasattr(player, 'lineupSlot'):
                slot_map = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE', 16: 'D/ST', 17: 'K', 20: 'BENCH', 21: 'IR'}
                lineup_slot = slot_map.get(player.lineupSlot, 'BENCH')
            
            # Additional stats for better analysis
            percent_owned = getattr(player, 'percent_owned', 0)
            percent_started = getattr(player, 'percent_started', 0)
            
            player_data = {
                'id': player_id,
                'name': name,
                'position': position,
                'team': pro_team,
                'injury_status': injury_status,
                'projected_points': round(projected_points, 1),
                'season_points': round(season_points, 1),
                'avg_points': round(avg_points, 1),
                'lineup_slot': lineup_slot,
                'percent_owned': percent_owned,
                'percent_started': percent_started,
                'is_starter': lineup_slot not in ['BENCH', 'IR'],
                'trade_value': self._calculate_player_value(position, avg_points, projected_points)
            }
            
            logger.info(f"Parsed player: {name} ({position}) - {season_points} pts, {lineup_slot}")
            return player_data
            
        except Exception as e:
            logger.error(f"Error parsing player data: {e}")
            logger.error(f"Player object type: {type(player)}")
            return None
    
    def _calculate_player_value(self, position: str, avg_points: float, projected_points: float) -> float:
        """Calculate a basic trade value for a player"""
        try:
            # Position multipliers (some positions are more valuable)
            position_multipliers = {
                'QB': 1.0,
                'RB': 1.2,  # RBs often more valuable due to scarcity
                'WR': 1.1,
                'TE': 1.0,
                'K': 0.5,   # Kickers less valuable
                'D/ST': 0.7  # Defense less valuable
            }
            
            multiplier = position_multipliers.get(position, 1.0)
            
            # Use average of season performance and projections
            base_value = (avg_points * 0.7) + (projected_points * 0.3)
            
            return round(base_value * multiplier, 1)
            
        except Exception as e:
            logger.error(f"Error calculating player value: {e}")
            return 0.0
    
    def calculate_trade_value(self, players: List[Dict]) -> Dict:
        """Calculate basic trade values for players"""
        try:
            total_value = 0
            position_values = {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0, 'K': 0, 'D/ST': 0}
            
            for player in players:
                # Simple value calculation based on projected points and position scarcity
                base_value = player.get('projected_points', 0)
                position = player.get('position', 'UNKNOWN')
                
                # Position scarcity multipliers (RB/WR more valuable due to scarcity)
                multipliers = {
                    'QB': 0.8,
                    'RB': 1.2,
                    'WR': 1.1,
                    'TE': 1.0,
                    'K': 0.5,
                    'D/ST': 0.6
                }
                
                player_value = base_value * multipliers.get(position, 1.0)
                total_value += player_value
                
                if position in position_values:
                    position_values[position] += player_value
            
            return {
                'total_value': round(total_value, 2),
                'position_breakdown': position_values,
                'average_value': round(total_value / max(1, len(players)), 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trade value: {e}")
            return {'total_value': 0, 'position_breakdown': {}, 'average_value': 0}
