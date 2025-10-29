import React, { createContext, useContext, useState } from 'react';

const LeagueContext = createContext();

export const useLeague = () => {
  const context = useContext(LeagueContext);
  if (!context) {
    throw new Error('useLeague must be used within a LeagueProvider');
  }
  return context;
};

export const LeagueProvider = ({ children }) => {
  const [league, setLeague] = useState(null);
  const [teams, setTeams] = useState([]);
  const [userTeam, setUserTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const connectLeague = async (leagueId, espnS2, swid) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/connect-league', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          league_id: leagueId,
          espn_s2: espnS2,
          swid: swid
        })
      });

      if (!response.ok) {
        throw new Error('Failed to connect to league');
      }

      const data = await response.json();
      setLeague(data.league);
      setTeams(data.teams);
      setUserTeam(data.user_team);
      
      return true;
    } catch (err) {
      setError(err.message || 'Failed to connect to league');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    league,
    teams,
    userTeam,
    setUserTeam,
    loading,
    error,
    connectLeague
  };

  return (
    <LeagueContext.Provider value={value}>
      {children}
    </LeagueContext.Provider>
  );
};
