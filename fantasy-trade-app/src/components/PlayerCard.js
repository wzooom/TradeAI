import React from 'react';

const PlayerCard = ({ player, isSelected, onToggle, showStats = true }) => {
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

  const getInjuryStatus = (status) => {
    const statusMap = {
      'ACTIVE': { text: 'Healthy', color: 'text-green-600' },
      'QUESTIONABLE': { text: 'Questionable', color: 'text-yellow-600' },
      'DOUBTFUL': { text: 'Doubtful', color: 'text-orange-600' },
      'OUT': { text: 'Out', color: 'text-red-600' },
      'IR': { text: 'IR', color: 'text-red-600' }
    };
    return statusMap[status] || { text: status, color: 'text-gray-600' };
  };

  const injuryInfo = getInjuryStatus(player.injury_status);

  return (
    <div
      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 bg-white'
      }`}
      onClick={() => onToggle(player)}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{player.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPositionColor(player.position)}`}>
              {player.position}
            </span>
            {player.injury_status !== 'ACTIVE' && (
              <span className={`text-xs font-medium ${injuryInfo.color}`}>
                {injuryInfo.text}
              </span>
            )}
          </div>
        </div>
        
        {showStats && (
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {player.projected_points?.toFixed(1) || '0.0'} pts
            </div>
            <div className="text-xs text-gray-500">projected</div>
          </div>
        )}
      </div>

      {showStats && (
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
          <div>
            <span className="font-medium">Season: </span>
            {player.season_points?.toFixed(1) || '0.0'} pts
          </div>
          <div>
            <span className="font-medium">Avg: </span>
            {player.avg_points?.toFixed(1) || '0.0'} pts
          </div>
        </div>
      )}

      {isSelected && (
        <div className="mt-2 text-xs text-blue-600 font-medium">
          ✓ Selected for trade
        </div>
      )}
    </div>
  );
};

export default PlayerCard;
