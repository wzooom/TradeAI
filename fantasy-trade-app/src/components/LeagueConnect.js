import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeague } from '../context/LeagueContext';

const LeagueConnect = () => {
  const navigate = useNavigate();
  const { connectLeague, loading, error, league } = useLeague();
  const [step, setStep] = useState('method'); // 'method', 'manual', 'auto'
  const [formData, setFormData] = useState({
    leagueId: '',
    espnS2: '',
    swid: ''
  });
  const [cookieString, setCookieString] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await connectLeague(formData.leagueId, formData.espnS2, formData.swid);
    if (success) {
      navigate('/dashboard');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAutoExtract = async () => {
    if (!cookieString.trim()) {
      alert('Please paste your cookies first');
      return;
    }

    try {
      // Check if it's the bookmarklet format (ESPN_S2|SWID)
      if (cookieString.includes('|') && !cookieString.includes(';')) {
        const [espnS2, swid] = cookieString.split('|');
        setFormData(prev => ({
          ...prev,
          espnS2: espnS2.trim(),
          swid: swid.trim()
        }));
        alert('Cookies extracted successfully! Now enter your League ID.');
        return;
      }

      // Parse cookie string format
      const cookies = {};
      cookieString.split(';').forEach(cookie => {
        const [name, value] = cookie.split('=').map(s => s.trim());
        if (name && value) {
          cookies[name] = value;
        }
      });

      const espnS2 = cookies['ESPN_S2'] || cookies['espn_s2'];
      const swid = cookies['SWID'] || cookies['swid'];

      if (!espnS2 || !swid) {
        throw new Error('Could not find ESPN_S2 and SWID cookies. Make sure you copied them from ESPN Fantasy.');
      }

      setFormData(prev => ({
        ...prev,
        espnS2,
        swid
      }));
      
      alert('Cookies extracted successfully! Now enter your League ID.');
      
    } catch (err) {
      alert(err.message || 'Failed to extract cookies');
    }
  };

  const openESPNInstructions = () => {
    window.open('https://fantasy.espn.com', '_blank');
  };

  // If already connected, redirect to dashboard
  if (league) {
    navigate('/dashboard');
    return <div>Redirecting...</div>;
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="max-w-2xl w-full mx-auto px-4">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-full p-4">
              <span className="text-4xl">🏈</span>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Fantasy Trade Analyzer
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Connect your ESPN league to analyze trades, view rosters, and make smarter decisions
          </p>
        </div>

        {/* Connection Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Connect Your ESPN League
          </h2>

          {step === 'method' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-4">
                <button
                  onClick={() => setStep('auto')}
                  className="group p-6 border-2 border-blue-200 rounded-xl hover:border-blue-500 text-left transition-all duration-200 hover:shadow-lg"
                >
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                        <span className="text-2xl">🚀</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-900">
                        Quick Connect (Recommended)
                      </h3>
                      <p className="text-gray-600 mt-1">
                        Use our bookmarklet to automatically extract your ESPN cookies
                      </p>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setStep('manual')}
                  className="group p-6 border-2 border-gray-200 rounded-xl hover:border-gray-400 text-left transition-all duration-200 hover:shadow-lg"
                >
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center group-hover:bg-gray-200 transition-colors">
                        <span className="text-2xl">⚙️</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-gray-800">
                        Manual Setup
                      </h3>
                      <p className="text-gray-600 mt-1">
                        Manually enter your League ID and authentication cookies
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {step === 'auto' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">Step 1: Get the Bookmarklet</h3>
                <p className="text-blue-800 text-sm mb-3">
                  Copy this bookmarklet and save it as a bookmark in your browser:
                </p>
                <div className="bg-white p-3 rounded border text-xs font-mono break-all">
                  {`javascript:(function(){const cookies=document.cookie;let espnS2=cookies.match(/espn_s2=([^;]+)/)?.[1];let swid=cookies.match(/SWID=([^;]+)/)?.[1];if(espnS2&&swid){navigator.clipboard.writeText(espnS2+'|'+swid).then(()=>alert('✅ ESPN cookies copied! Go back to Fantasy Trade Analyzer and paste them.'));} else{alert('❌ Please make sure you are on fantasy.espn.com and logged in.');}})();`}
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 mb-2">Step 2: Use the Bookmarklet</h3>
                <p className="text-green-800 text-sm mb-3">
                  1. Go to fantasy.espn.com and log in<br/>
                  2. Click the bookmarklet you saved<br/>
                  3. Your cookies will be copied automatically
                </p>
                <button
                  onClick={openESPNInstructions}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                >
                  Open ESPN Fantasy →
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Step 3: Paste Your Cookies Here
                </label>
                <textarea
                  value={cookieString}
                  onChange={(e) => setCookieString(e.target.value)}
                  placeholder="Paste the cookies from the bookmarklet here..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="3"
                />
                <button
                  onClick={handleAutoExtract}
                  className="mt-3 w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Extract Cookies
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Step 4: Enter Your League ID
                </label>
                <input
                  type="text"
                  name="leagueId"
                  value={formData.leagueId}
                  onChange={handleChange}
                  placeholder="e.g., 123456789"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Find this in your ESPN league URL: fantasy.espn.com/football/league?leagueId=YOUR_ID
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setStep('method')}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  ← Back
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={loading || !formData.leagueId || !formData.espnS2 || !formData.swid}
                  className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {loading ? 'Connecting...' : 'Connect League'}
                </button>
              </div>
            </div>
          )}

          {step === 'manual' && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  League ID *
                </label>
                <input
                  type="text"
                  name="leagueId"
                  value={formData.leagueId}
                  onChange={handleChange}
                  required
                  placeholder="e.g., 123456789"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ESPN_S2 Cookie
                </label>
                <input
                  type="text"
                  name="espnS2"
                  value={formData.espnS2}
                  onChange={handleChange}
                  placeholder="Optional - for private leagues"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SWID Cookie
                </label>
                <input
                  type="text"
                  name="swid"
                  value={formData.swid}
                  onChange={handleChange}
                  placeholder="Optional - for private leagues"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setStep('method')}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  ← Back
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.leagueId}
                  className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {loading ? 'Connecting...' : 'Connect League'}
                </button>
              </div>
            </form>
          )}

          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-red-400 text-xl">❌</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Connection Failed</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Features Preview */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Trade Analysis</h3>
            <p className="text-gray-600 text-sm">Get instant analysis of trade fairness with visual comparisons</p>
          </div>
          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-4">
              <span className="text-2xl">👥</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Team Rosters</h3>
            <p className="text-gray-600 text-sm">View detailed rosters with player stats and trade values</p>
          </div>
          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-4">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Decisions</h3>
            <p className="text-gray-600 text-sm">Make data-driven trade decisions with confidence</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeagueConnect;
