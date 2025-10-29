import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLeague } from '../context/LeagueContext';
import TradeVisualization from './TradeVisualization';

// Player card component for trade selection
const PlayerTradeCard = ({ player, isSelected, onToggle, teamColor = 'blue' }) => {
  const getPositionColor = (position) => {
    const colors = {
      'QB': 'bg-red-100 text-red-800 border-red-200',
      'RB': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      'WR': 'bg-sky-100 text-sky-800 border-sky-200',
      'TE': 'bg-amber-100 text-amber-800 border-amber-200',
      'K': 'bg-purple-100 text-purple-800 border-purple-200',
      'D/ST': 'bg-slate-100 text-slate-800 border-slate-200'
    };
    return colors[position] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getInjuryColor = (status) => {
    const colors = {
      'ACTIVE': 'text-green-600',
      'QUESTIONABLE': 'text-yellow-600',
      'DOUBTFUL': 'text-orange-600',
      'OUT': 'text-red-600',
      'INJURED': 'text-red-600'
    };
    return colors[status] || 'text-gray-600';
  };

  const getTeamStyles = (teamColor, isSelected) => {
    if (teamColor === 'blue') {
      return isSelected 
        ? 'border-blue-500 bg-blue-200 shadow-lg transform scale-105' 
        : 'border-blue-300 hover:border-blue-400 bg-white hover:bg-blue-50 hover:shadow-md';
    } else {
      return isSelected 
        ? 'border-green-500 bg-green-200 shadow-lg transform scale-105' 
        : 'border-green-300 hover:border-green-400 bg-white hover:bg-green-50 hover:shadow-md';
    }
  };

  return (
    <div
      onClick={() => onToggle(player)}
      className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${getTeamStyles(teamColor, isSelected)}`}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-gray-900 text-base">{player.name}</h4>
            <span className={`px-2 py-1 text-xs font-bold rounded-lg border ${getPositionColor(player.position)}`}>
              {player.position}
            </span>
            {player.injury_status !== 'ACTIVE' && (
              <span className={`text-xs font-bold px-2 py-1 rounded-full bg-red-100 ${getInjuryColor(player.injury_status)}`}>
                {player.injury_status}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            <span className="font-medium">{player.team}</span> • {player.lineup_slot}
          </div>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span><strong>{player.season_points}</strong> season pts</span>
            <span><strong>{player.avg_points}</strong> avg/game</span>
          </div>
        </div>
        <div className="text-right ml-4">
          <div className={`text-2xl font-bold ${teamColor === 'blue' ? 'text-blue-700' : 'text-green-700'}`}>
            {player.trade_value}
          </div>
          <div className="text-xs text-gray-500 font-medium">Trade Value</div>
          {isSelected && (
            <div className={`mt-2 text-xs font-bold ${teamColor === 'blue' ? 'text-blue-800' : 'text-green-800'}`}>
              ✓ SELECTED
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const TradeAnalyzer = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { league, teams, userTeam } = useLeague();
  
  const [tradePartner, setTradePartner] = useState(location.state?.tradePartner || null);
  const [myRoster, setMyRoster] = useState(null);
  const [partnerRoster, setPartnerRoster] = useState(null);
  const [selectedMyPlayers, setSelectedMyPlayers] = useState([]);
  const [selectedTheirPlayers, setSelectedTheirPlayers] = useState([]);
  const [tradeAnalysis, setTradeAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch rosters when component mounts or trade partner changes
  useEffect(() => {
    if (userTeam && tradePartner) {
      fetchRosters();
    }
  }, [userTeam, tradePartner]);

  // Auto-analyze trade when selections change
  useEffect(() => {
    if (selectedMyPlayers.length > 0 || selectedTheirPlayers.length > 0) {
      analyzeTrade();
    } else {
      setTradeAnalysis(null);
    }
  }, [selectedMyPlayers, selectedTheirPlayers]);

  const fetchRosters = async () => {
    setLoading(true);
    try {
      // Fetch both rosters in parallel
      const [myRosterResponse, partnerRosterResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/roster/${userTeam.id}`),
        fetch(`http://localhost:8000/api/roster/${tradePartner.id}`)
      ]);

      if (!myRosterResponse.ok || !partnerRosterResponse.ok) {
        throw new Error('Failed to fetch rosters');
      }

      const [myRosterData, partnerRosterData] = await Promise.all([
        myRosterResponse.json(),
        partnerRosterResponse.json()
      ]);

      setMyRoster(myRosterData);
      setPartnerRoster(partnerRosterData);
    } catch (error) {
      console.error('Error fetching rosters:', error);
      alert('Failed to load team rosters');
    } finally {
      setLoading(false);
    }
  };

  const analyzeTrade = async () => {
    if (selectedMyPlayers.length === 0 && selectedTheirPlayers.length === 0) {
      setTradeAnalysis(null);
      return;
    }

    setAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/analyze-trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team1_players: selectedMyPlayers,
          team2_players: selectedTheirPlayers
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze trade');
      }

      const analysis = await response.json();
      setTradeAnalysis(analysis);
    } catch (error) {
      console.error('Error analyzing trade:', error);
      setTradeAnalysis({
        error: 'Failed to analyze trade',
        is_fair: false,
        recommendation: 'Unable to analyze'
      });
    } finally {
      setAnalyzing(false);
    }
  };

  if (!league || !userTeam) {
    navigate('/');
    return <div>Loading...</div>;
  }

  const togglePlayerSelection = (player, isMyPlayer) => {
    if (isMyPlayer) {
      setSelectedMyPlayers(prev => 
        prev.find(p => p.id === player.id)
          ? prev.filter(p => p.id !== player.id)
          : [...prev, player]
      );
    } else {
      setSelectedTheirPlayers(prev => 
        prev.find(p => p.id === player.id)
          ? prev.filter(p => p.id !== player.id)
          : [...prev, player]
      );
    }
  };


  const clearTrade = () => {
    setSelectedMyPlayers([]);
    setSelectedTheirPlayers([]);
    setTradeAnalysis(null);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center py-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Trade Analyzer</h1>
        <p className="text-xl text-gray-600">Compare players and analyze trade fairness</p>
      </div>

      {!tradePartner && (
        <div className="bg-white shadow-xl rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Select Trade Partner</h2>
          <p className="text-gray-600 text-center mb-8">Choose a team to start analyzing potential trades</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {teams.filter(team => team.id !== userTeam.id).map((team) => (
              <button
                key={team.id}
                onClick={() => setTradePartner(team)}
                className="group p-6 rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg text-left transition-all duration-200 transform hover:-translate-y-1"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="font-bold text-gray-900 text-lg group-hover:text-blue-900">{team.name}</div>
                  <div className="bg-gray-100 group-hover:bg-blue-100 rounded-full p-2">
                    <span className="text-lg">👥</span>
                  </div>
                </div>
                <div className="text-sm text-gray-600 mb-2">{team.owner}</div>
                <div className="bg-gray-100 group-hover:bg-blue-100 text-gray-700 group-hover:text-blue-800 px-2 py-1 rounded-full text-xs font-medium inline-block">
                  {team.wins}-{team.losses}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {tradePartner && (
        <>
          {/* Trade Header */}
          <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-3xl font-bold mb-2">
                  {userTeam.name} ↔ {tradePartner.name}
                </h2>
                <p className="text-blue-100">
                  Click players below to add them to the trade
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={clearTrade}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg transition-all font-medium"
                >
                  Clear Selections
                </button>
                <button
                  onClick={() => setTradePartner(null)}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg transition-all font-medium"
                >
                  Change Partner
                </button>
              </div>
            </div>
          </div>

          {/* Team Rosters */}
          <div className="bg-white shadow-xl rounded-2xl p-6">

            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
                {/* VS Divider - Only visible on large screens */}
                <div className="hidden lg:flex absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                  <div className="bg-white rounded-full p-4 shadow-lg border-4 border-gray-200">
                    <span className="text-2xl font-bold text-gray-600">VS</span>
                  </div>
                </div>

                {/* Your Team Column */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border-2 border-blue-200">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-bold text-blue-900">
                        Your Team
                      </h3>
                      <p className="text-blue-700 text-sm">
                        {myRoster?.team.name} • {myRoster?.team.record}
                      </p>
                    </div>
                    <div className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {selectedMyPlayers.length} selected
                    </div>
                  </div>
                  
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {myRoster?.roster.all_players?.map((player) => (
                      <PlayerTradeCard
                        key={player.id}
                        player={player}
                        isSelected={selectedMyPlayers.find(p => p.id === player.id)}
                        onToggle={(p) => togglePlayerSelection(p, true)}
                        teamColor="blue"
                      />
                    ))}
                  </div>
                </div>

                {/* Their Team Column */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border-2 border-green-200">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-bold text-green-900">
                        {tradePartner.name}
                      </h3>
                      <p className="text-green-700 text-sm">
                        {partnerRoster?.team.name} • {partnerRoster?.team.record}
                      </p>
                    </div>
                    <div className="bg-green-200 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                      {selectedTheirPlayers.length} selected
                    </div>
                  </div>
                  
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {partnerRoster?.roster.all_players?.map((player) => (
                      <PlayerTradeCard
                        key={player.id}
                        player={player}
                        isSelected={selectedTheirPlayers.find(p => p.id === player.id)}
                        onToggle={(p) => togglePlayerSelection(p, false)}
                        teamColor="green"
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

          </div>

          {/* Trade Analysis Results */}
          {analyzing && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
                <span className="text-gray-600">Analyzing trade...</span>
              </div>
            </div>
          )}
          
          {/* Trade Visualization */}
          <TradeVisualization 
            tradeAnalysis={tradeAnalysis}
            selectedMyPlayers={selectedMyPlayers}
            selectedTheirPlayers={selectedTheirPlayers}
          />

          {/* Trade Analysis Summary */}
          {tradeAnalysis && !analyzing && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Trade Recommendation</h3>
              
              <div className={`p-4 rounded-lg ${tradeAnalysis.is_fair ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className={`text-lg font-semibold ${tradeAnalysis.is_fair ? 'text-green-800' : 'text-red-800'}`}>
                  {tradeAnalysis.recommendation}
                </div>
                {!tradeAnalysis.is_fair && (
                  <div className={`text-sm mt-1 ${tradeAnalysis.is_fair ? 'text-green-700' : 'text-red-700'}`}>
                    Advantage: {tradeAnalysis.advantage} points to {tradeAnalysis.winner === 'team1' ? 'you' : 'them'}
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-sm text-gray-600">Your Total</div>
                  <div className="text-xl font-bold text-blue-600">
                    {selectedMyPlayers.reduce((sum, p) => sum + (p.trade_value || 0), 0).toFixed(1)}
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-sm text-gray-600">Their Total</div>
                  <div className="text-xl font-bold text-green-600">
                    {selectedTheirPlayers.reduce((sum, p) => sum + (p.trade_value || 0), 0).toFixed(1)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TradeAnalyzer;
