import React, { useState } from 'react';

const TradeVisualization = ({ tradeAnalysis, selectedMyPlayers, selectedTheirPlayers }) => {
  const [hoveredPlayer, setHoveredPlayer] = useState(null);

  if (!selectedMyPlayers.length && !selectedTheirPlayers.length) {
    return null;
  }

  // Position colors for consistency
  const getPositionColor = (position) => {
    const colors = {
      'QB': '#ef4444', // red
      'RB': '#22c55e', // green
      'WR': '#3b82f6', // blue
      'TE': '#eab308', // yellow
      'K': '#a855f7',  // purple
      'D/ST': '#6b7280' // gray
    };
    return colors[position] || '#6b7280';
  };

  // Calculate max height for scaling
  const myTotal = selectedMyPlayers.reduce((sum, player) => sum + (player.trade_value || 0), 0);
  const theirTotal = selectedTheirPlayers.reduce((sum, player) => sum + (player.trade_value || 0), 0);
  const maxTotal = Math.max(myTotal, theirTotal, 1);
  
  // Bar height (in pixels)
  const maxBarHeight = 300;
  const myBarHeight = (myTotal / maxTotal) * maxBarHeight;
  const theirBarHeight = (theirTotal / maxTotal) * maxBarHeight;

  // Calculate segment heights
  const calculateSegments = (players, totalBarHeight) => {
    const totalValue = players.reduce((sum, player) => sum + (player.trade_value || 0), 0);
    let currentHeight = 0;
    
    return players.map(player => {
      const playerValue = player.trade_value || 0;
      const segmentHeight = totalValue > 0 ? (playerValue / totalValue) * totalBarHeight : 0;
      const segment = {
        player,
        height: segmentHeight,
        y: currentHeight,
        value: playerValue
      };
      currentHeight += segmentHeight;
      return segment;
    });
  };

  const mySegments = calculateSegments(selectedMyPlayers, myBarHeight);
  const theirSegments = calculateSegments(selectedTheirPlayers, theirBarHeight);

  const PlayerTooltip = ({ player, x, y }) => (
    <div 
      className="absolute z-10 bg-black text-white text-xs rounded px-2 py-1 pointer-events-none"
      style={{ 
        left: x, 
        top: y - 40,
        transform: 'translateX(-50%)'
      }}
    >
      <div className="font-medium">{player.name}</div>
      <div>{player.position} • {player.trade_value} pts</div>
    </div>
  );

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Trade Value Comparison</h3>
      
      <div className="relative">
        {/* Chart Container */}
        <div className="flex justify-center items-end space-x-8" style={{ height: maxBarHeight + 60 }}>
          
          {/* Your Team Bar */}
          <div className="flex flex-col items-center">
            <div className="text-sm font-medium text-gray-700 mb-2">Your Players</div>
            <div 
              className="relative bg-gray-100 rounded-t-lg border-2 border-gray-300"
              style={{ width: '80px', height: maxBarHeight }}
            >
              {/* Bar segments */}
              <div className="absolute bottom-0 w-full">
                {mySegments.map((segment, index) => (
                  <div
                    key={segment.player.id}
                    className="relative cursor-pointer transition-opacity hover:opacity-80"
                    style={{
                      height: `${segment.height}px`,
                      backgroundColor: getPositionColor(segment.player.position),
                      borderTop: index > 0 ? '1px solid rgba(255,255,255,0.3)' : 'none'
                    }}
                    onMouseEnter={(e) => {
                      const rect = e.target.getBoundingClientRect();
                      setHoveredPlayer({
                        player: segment.player,
                        x: rect.left + rect.width / 2,
                        y: rect.top
                      });
                    }}
                    onMouseLeave={() => setHoveredPlayer(null)}
                  >
                    {/* Player initials for larger segments */}
                    {segment.height > 25 && (
                      <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">
                        {segment.player.name.split(' ').map(n => n[0]).join('')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="text-lg font-bold text-blue-600">{myTotal.toFixed(1)}</div>
              <div className="text-xs text-gray-500">Total Points</div>
            </div>
          </div>

          {/* VS Indicator */}
          <div className="flex flex-col items-center justify-center pb-16">
            <div className="text-2xl font-bold text-gray-400">VS</div>
            {tradeAnalysis ? (
              tradeAnalysis.is_fair ? (
                <div className="text-green-600 text-sm font-medium mt-2">Fair Trade</div>
              ) : (
                <div className="text-red-600 text-sm font-medium mt-2">
                  {tradeAnalysis.advantage.toFixed(1)} pt advantage
                </div>
              )
            ) : (
              <div className="text-gray-500 text-sm font-medium mt-2">
                {Math.abs(myTotal - theirTotal).toFixed(1)} pt difference
              </div>
            )}
          </div>

          {/* Their Team Bar */}
          <div className="flex flex-col items-center">
            <div className="text-sm font-medium text-gray-700 mb-2">Their Players</div>
            <div 
              className="relative bg-gray-100 rounded-t-lg border-2 border-gray-300"
              style={{ width: '80px', height: maxBarHeight }}
            >
              {/* Bar segments */}
              <div className="absolute bottom-0 w-full">
                {theirSegments.map((segment, index) => (
                  <div
                    key={segment.player.id}
                    className="relative cursor-pointer transition-opacity hover:opacity-80"
                    style={{
                      height: `${segment.height}px`,
                      backgroundColor: getPositionColor(segment.player.position),
                      borderTop: index > 0 ? '1px solid rgba(255,255,255,0.3)' : 'none'
                    }}
                    onMouseEnter={(e) => {
                      const rect = e.target.getBoundingClientRect();
                      setHoveredPlayer({
                        player: segment.player,
                        x: rect.left + rect.width / 2,
                        y: rect.top
                      });
                    }}
                    onMouseLeave={() => setHoveredPlayer(null)}
                  >
                    {/* Player initials for larger segments */}
                    {segment.height > 25 && (
                      <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">
                        {segment.player.name.split(' ').map(n => n[0]).join('')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="text-lg font-bold text-green-600">{theirTotal.toFixed(1)}</div>
              <div className="text-xs text-gray-500">Total Points</div>
            </div>
          </div>
        </div>

        {/* Tooltip */}
        {hoveredPlayer && (
          <PlayerTooltip 
            player={hoveredPlayer.player}
            x={hoveredPlayer.x}
            y={hoveredPlayer.y}
          />
        )}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="text-sm font-medium text-gray-700 mb-3">Position Legend</div>
        <div className="flex flex-wrap gap-4">
          {['QB', 'RB', 'WR', 'TE', 'K', 'D/ST'].map(position => (
            <div key={position} className="flex items-center">
              <div 
                className="w-4 h-4 rounded mr-2"
                style={{ backgroundColor: getPositionColor(position) }}
              ></div>
              <span className="text-sm text-gray-600">{position}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Player Breakdown */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Your Players */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Your Players ({selectedMyPlayers.length})</h4>
            <div className="space-y-2">
              {selectedMyPlayers.map(player => (
                <div key={player.id} className="flex justify-between items-center text-sm">
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded mr-2"
                      style={{ backgroundColor: getPositionColor(player.position) }}
                    ></div>
                    <span>{player.name}</span>
                    <span className="ml-2 text-gray-500">({player.position})</span>
                  </div>
                  <span className="font-medium">{player.trade_value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Their Players */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Their Players ({selectedTheirPlayers.length})</h4>
            <div className="space-y-2">
              {selectedTheirPlayers.map(player => (
                <div key={player.id} className="flex justify-between items-center text-sm">
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded mr-2"
                      style={{ backgroundColor: getPositionColor(player.position) }}
                    ></div>
                    <span>{player.name}</span>
                    <span className="ml-2 text-gray-500">({player.position})</span>
                  </div>
                  <span className="font-medium">{player.trade_value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeVisualization;
