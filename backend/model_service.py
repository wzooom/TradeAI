"""
Model service for player valuation and prediction
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class PlayerValuationService:
    def __init__(self, model_path: str, data_path: str):
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.position_stats = {}
        
    def load_model_and_data(self):
        """Load the trained model and preprocessing components"""
        try:
            # Load model
            self.model = tf.keras.models.load_model(str(self.model_path))
            logger.info(f"✅ Model loaded from {self.model_path}")
            
            # Load training data for feature columns and scaling
            df = pd.read_csv(self.data_path)
            
            # Get feature columns (exclude target variables)
            self.feature_columns = [col for col in df.columns 
                                  if col not in ['fantasy_points', 'fantasy_points_ppr']]
            
            # Fit scaler on training data
            self.scaler = StandardScaler()
            self.scaler.fit(df[self.feature_columns])
            
            # Calculate position-based statistics for better estimates
            self._calculate_position_stats(df)
            
            logger.info(f"✅ Loaded {len(self.feature_columns)} features")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading model or data: {e}")
            return False
    
    def _calculate_position_stats(self, df):
        """Calculate average statistics by position for better feature estimation"""
        try:
            # Group by position and calculate means
            position_groups = df.groupby('position').mean() if 'position' in df.columns else None
            
            if position_groups is not None:
                for position in ['QB', 'RB', 'WR', 'TE']:
                    if position in position_groups.index:
                        self.position_stats[position] = position_groups.loc[position].to_dict()
                        
            logger.info(f"✅ Position statistics calculated for {len(self.position_stats)} positions")
            
        except Exception as e:
            logger.warning(f"Could not calculate position stats: {e}")
    
    def create_player_features(self, player_data: dict) -> np.ndarray:
        """Create feature vector for a player"""
        if self.feature_columns is None:
            raise ValueError("Model not loaded")
        
        # Initialize feature vector with zeros
        features = np.zeros(len(self.feature_columns))
        
        # Get player info
        position = player_data.get('position', 'RB')
        projected_points = player_data.get('projectedPoints', 150)
        
        # Set position indicators
        position_flags = {
            'is_qb': 1 if position == 'QB' else 0,
            'is_rb': 1 if position == 'RB' else 0,
            'is_wr': 1 if position == 'WR' else 0,
            'is_te': 1 if position == 'TE' else 0,
        }
        
        for flag, value in position_flags.items():
            if flag in self.feature_columns:
                idx = self.feature_columns.index(flag)
                features[idx] = value
        
        # Use position averages if available, otherwise estimate
        if position in self.position_stats:
            pos_stats = self.position_stats[position]
            for feature, avg_value in pos_stats.items():
                if feature in self.feature_columns and not pd.isna(avg_value):
                    idx = self.feature_columns.index(feature)
                    # Scale the average based on projected points
                    scale_factor = projected_points / 150  # Normalize around 150 points
                    features[idx] = avg_value * scale_factor
        else:
            # Fallback: estimate basic stats based on position and projected points
            self._estimate_basic_stats(features, position, projected_points)
        
        # Set games to full season
        if 'games' in self.feature_columns:
            idx = self.feature_columns.index('games')
            features[idx] = 17
        
        return features.reshape(1, -1)
    
    def _estimate_basic_stats(self, features, position, projected_points):
        """Estimate basic statistics when position averages aren't available"""
        scale_factor = projected_points / 150
        
        if position == 'QB':
            stat_estimates = {
                'passing_yards': 3500 * scale_factor,
                'passing_tds': 25 * scale_factor,
                'completions': 350 * scale_factor,
                'attempts': 550 * scale_factor,
                'interceptions': 10,
            }
        elif position == 'RB':
            stat_estimates = {
                'rushing_yards': 800 * scale_factor,
                'rushing_tds': 8 * scale_factor,
                'rushing_attempts': 200 * scale_factor,
                'receiving_yards': 300 * scale_factor,
                'receptions': 30 * scale_factor,
                'targets': 40 * scale_factor,
            }
        elif position == 'WR':
            stat_estimates = {
                'receiving_yards': 900 * scale_factor,
                'receiving_tds': 7 * scale_factor,
                'receptions': 70 * scale_factor,
                'targets': 110 * scale_factor,
                'rushing_yards': 50 * scale_factor,
            }
        elif position == 'TE':
            stat_estimates = {
                'receiving_yards': 600 * scale_factor,
                'receiving_tds': 5 * scale_factor,
                'receptions': 50 * scale_factor,
                'targets': 75 * scale_factor,
            }
        else:
            stat_estimates = {}
        
        # Apply estimates to feature vector
        for stat, value in stat_estimates.items():
            if stat in self.feature_columns:
                idx = self.feature_columns.index(stat)
                features[idx] = value
    
    def predict_fantasy_points(self, player_data: dict) -> float:
        """Predict fantasy points for a player"""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not loaded")
        
        # Create feature vector
        features = self.create_player_features(player_data)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled, verbose=0)
        
        return float(prediction[0][0])
    
    def analyze_trade_impact(self, user_players: list, partner_players: list) -> dict:
        """Analyze the fantasy point impact of a trade"""
        user_giving_value = sum(self.predict_fantasy_points(player) for player in user_players)
        user_receiving_value = sum(self.predict_fantasy_points(player) for player in partner_players)
        
        user_net_change = user_receiving_value - user_giving_value
        partner_net_change = user_giving_value - user_receiving_value
        
        # Generate recommendation
        if user_net_change > 10:
            recommendation = "Excellent trade for you! This significantly improves your team."
        elif user_net_change > 5:
            recommendation = "Good trade for you. Consider accepting this offer."
        elif user_net_change > 0:
            recommendation = "Slight advantage to you. Worth considering based on team needs."
        elif user_net_change > -5:
            recommendation = "Fairly even trade. Consider roster construction and bye weeks."
        elif user_net_change > -10:
            recommendation = "This trade favors your opponent. You might want to ask for more."
        else:
            recommendation = "Poor trade for you. Consider declining or asking for significant additions."
        
        return {
            'user_giving_value': user_giving_value,
            'user_receiving_value': user_receiving_value,
            'user_net_change': user_net_change,
            'partner_net_change': partner_net_change,
            'recommendation': recommendation
        }
    
    def is_loaded(self) -> bool:
        """Check if model and components are loaded"""
        return all([
            self.model is not None,
            self.scaler is not None,
            self.feature_columns is not None
        ])
