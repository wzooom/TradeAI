import React, { useState, useEffect } from 'react';
import { useLeague } from '../context/LeagueContext';

const Roster = ({ teamId, teamName }) => {
  const [rosterData, setRosterData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState('starters');

  useEffect(() => {
    if (teamId) {
      fetchRoster();
    }
  }, [teamId]);

  const fetchRoster = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/roster/${teamId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch roster');
      }
      
      const data = await response.json();
      setRosterData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getPositionColor = (position) => {
    const colors = {
      'QB': 'bg-red-100 text-red-800',
      'RB': 'bg-green-100 text-green-800',
      'WR': 'bg-blue-100 text-blue-800',
      'TE': 'bg-yellow-100 text-yellow-800',
      'K': 'bg-purple-100 text-purple-800',
      'D/ST': 'bg-gray-100 text-gray-800'
    };
    return colors[position] || 'bg-gray-100 text-gray-800';
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

  const PlayerCard = ({ player, showLineupSlot = false }) => (
    <div className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium text-gray-900">{player.name}</h4>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPositionColor(player.position)}`}>
              {player.position}
            </span>
            {showLineupSlot && (
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                {player.lineup_slot}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>{player.team}</span>
            <span className={getInjuryColor(player.injury_status)}>
              {player.injury_status}
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-blue-600">
            {player.trade_value}
          </div>
          <div className="text-xs text-gray-500">Trade Value</div>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div className="text-center">
          <div className="font-medium text-gray-900">{player.season_points}</div>
          <div className="text-xs text-gray-500">Season Pts</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">{player.avg_points}</div>
          <div className="text-xs text-gray-500">Avg/Game</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">{player.projected_points}</div>
          <div className="text-xs text-gray-500">Projected</div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <div className="text-red-600 mb-2">Failed to load roster</div>
          <div className="text-gray-600 text-sm mb-4">{error}</div>
          <button
            onClick={fetchRoster}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!rosterData) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center text-gray-600">
          No roster data available
        </div>
      </div>
    );
  }

  const { team, roster, team_stats } = rosterData;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {team.name} Roster
          </h2>
          <p className="text-gray-600">
            {team.owner} • {team.record} • {roster.total_players} players
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {team_stats.projected_points.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Projected Pts</div>
        </div>
      </div>

      {/* View Toggle */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {[
          { key: 'starters', label: 'Starters', count: roster.starters.length },
          { key: 'bench', label: 'Bench', count: roster.bench.length },
          { key: 'all', label: 'All Players', count: roster.all_players.length }
        ].map((view) => (
          <button
            key={view.key}
            onClick={() => setSelectedView(view.key)}
            className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
              selectedView === view.key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {view.label} ({view.count})
          </button>
        ))}
      </div>

      {/* Team Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">
            {team_stats.total_points.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Total Points</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">
            {team_stats.avg_starter_points.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Avg Starter Pts</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">
            {roster.starters.length}
          </div>
          <div className="text-sm text-gray-600">Active Starters</div>
        </div>
      </div>

      {/* Player List */}
      <div className="space-y-3">
        {selectedView === 'starters' && (
          <>
            <h3 className="font-medium text-gray-900 mb-3">Starting Lineup</h3>
            {roster.starters.map((player) => (
              <PlayerCard key={player.id} player={player} showLineupSlot={true} />
            ))}
          </>
        )}

        {selectedView === 'bench' && (
          <>
            <h3 className="font-medium text-gray-900 mb-3">Bench Players</h3>
            {roster.bench.map((player) => (
              <PlayerCard key={player.id} player={player} />
            ))}
          </>
        )}

        {selectedView === 'all' && (
          <>
            {Object.entries(roster.by_position).map(([position, players]) => (
              players.length > 0 && (
                <div key={position}>
                  <h3 className="font-medium text-gray-900 mb-3 mt-6 first:mt-0">
                    {position} ({players.length})
                  </h3>
                  <div className="space-y-3">
                    {players.map((player) => (
                      <PlayerCard key={player.id} player={player} showLineupSlot={true} />
                    ))}
                  </div>
                </div>
              )
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default Roster;
