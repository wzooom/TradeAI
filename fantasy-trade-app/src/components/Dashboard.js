import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeague } from '../context/LeagueContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const { league, teams, userTeam, setUserTeam } = useLeague();
  const [showTeamSelector, setShowTeamSelector] = useState(false);
  const [selectingTeam, setSelectingTeam] = useState(false);

  if (!league) {
    navigate('/');
    return <div>Loading...</div>;
  }

  const handleSelectTeam = async (teamId) => {
    setSelectingTeam(true);
    try {
      const response = await fetch('http://localhost:8000/api/select-team', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ team_id: teamId })
      });

      if (!response.ok) {
        throw new Error('Failed to select team');
      }

      const data = await response.json();
      setUserTeam(data.selected_team);
      setShowTeamSelector(false);
      
    } catch (error) {
      alert('Failed to select team: ' + error.message);
    } finally {
      setSelectingTeam(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Welcome to Your League
        </h1>
        <p className="text-xl text-gray-600">
          Analyze trades, view rosters, and make smarter decisions
        </p>
      </div>

      {/* League Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">League Size</p>
              <p className="text-3xl font-bold">{teams.length}</p>
              <p className="text-blue-100 text-sm">Teams</p>
            </div>
            <div className="bg-blue-400 bg-opacity-30 rounded-full p-3">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">League Name</p>
              <p className="text-xl font-bold truncate">{league.name}</p>
              <p className="text-green-100 text-sm">Active League</p>
            </div>
            <div className="bg-green-400 bg-opacity-30 rounded-full p-3">
              <span className="text-2xl">🏆</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Your Team</p>
              <p className="text-xl font-bold truncate">{userTeam?.name || 'N/A'}</p>
              <p className="text-purple-100 text-sm">
                {userTeam ? `${userTeam.wins}-${userTeam.losses}` : 'Not Selected'}
              </p>
              {userTeam?.uncertain_ownership && (
                <button
                  onClick={() => {
                    console.log('Button clicked - opening team selector');
                    setShowTeamSelector(true);
                  }}
                  className="mt-2 text-xs bg-purple-400 bg-opacity-50 text-white px-3 py-1 rounded-full hover:bg-opacity-70 transition-all"
                >
                  Change Team
                </button>
              )}
            </div>
            <div className="bg-purple-400 bg-opacity-30 rounded-full p-3">
              <span className="text-2xl">🏈</span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Selection Warning */}
      {userTeam?.uncertain_ownership && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="bg-yellow-100 rounded-full p-2">
                <span className="text-yellow-600 text-xl">⚠️</span>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-yellow-800">
                Team Selection Uncertain
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>We couldn't automatically identify your team. Currently showing: <strong>{userTeam.name}</strong></p>
                <button
                  onClick={() => {
                    console.log('Warning button clicked - opening team selector');
                    setShowTeamSelector(true);
                  }}
                  className="mt-3 bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                >
                  Select Your Team
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Teams Section */}
      <div className="bg-white shadow-xl rounded-2xl p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">League Teams</h2>
            <p className="text-gray-600 mt-1">Click a team to propose a trade or view their roster</p>
          </div>
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
            {teams.length} Teams
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {teams.map((team) => (
            <div
              key={team.id}
              className="group bg-gradient-to-br from-gray-50 to-gray-100 hover:from-blue-50 hover:to-blue-100 rounded-xl p-6 border border-gray-200 hover:border-blue-300 cursor-pointer transition-all duration-200 hover:shadow-lg transform hover:-translate-y-1"
              onClick={() => navigate('/trade', { state: { tradePartner: team } })}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 text-lg group-hover:text-blue-900 transition-colors">
                    {team.name}
                  </h3>
                  <p className="text-gray-600 text-sm mt-1">{team.owner}</p>
                  <div className="flex items-center mt-2">
                    <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                      {team.wins}-{team.losses}
                    </span>
                  </div>
                </div>
                <div className="bg-white bg-opacity-50 rounded-full p-2">
                  <span className="text-xl">👥</span>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // This will trigger the parent onClick (trade)
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Propose Trade
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate('/roster', { state: { teamId: team.id, teamName: team.name } })
                  }}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  View Roster
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Team Selector Modal */}
      {showTeamSelector && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Your Team</h3>
              <div className="space-y-2">
                {teams.map((team) => (
                  <button
                    key={team.id}
                    onClick={() => handleSelectTeam(team.id)}
                    disabled={selectingTeam}
                    className="w-full text-left p-3 border rounded-lg hover:bg-blue-50 hover:border-blue-300 disabled:opacity-50"
                  >
                    <div className="font-medium">{team.name}</div>
                    <div className="text-sm text-gray-600">{team.owner} • {team.wins}-{team.losses}</div>
                  </button>
                ))}
              </div>
              <div className="mt-4 flex justify-end space-x-2">
                <button
                  onClick={() => setShowTeamSelector(false)}
                  disabled={selectingTeam}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
