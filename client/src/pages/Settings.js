import React, { useState, useEffect, useContext } from 'react';
import { ApiContext } from '../contexts/ApiContext'; // Assuming you have/will have an ApiContext for API key

const SettingsPage = () => {
  const { apiKey, setApiKey, apiQuota, setApiQuota } = useContext(ApiContext); // Using ApiContext
  const [localApiKey, setLocalApiKey] = useState(apiKey || '');
  const [quotaUsage, setQuotaUsage] = useState(0); // Example: 0%
  const [quotaLimit, setQuotaLimit] = useState(10000); // Default YouTube API quota

  // Load API key from session storage on component mount
  useEffect(() => {
    const storedApiKey = sessionStorage.getItem('youtubeApiKey');
    if (storedApiKey) {
      setLocalApiKey(storedApiKey);
      setApiKey(storedApiKey); // Update context
    }
    // In a real app, you would fetch actual quota usage here
    // For now, let's simulate it or connect it to apiQuota from context if available
    if (apiQuota) {
      setQuotaUsage(apiQuota.usage);
      setQuotaLimit(apiQuota.limit);
    }
  }, [setApiKey, apiQuota]);

  const handleApiKeyChange = (e) => {
    setLocalApiKey(e.target.value);
  };

  const handleSaveSettings = () => {
    sessionStorage.setItem('youtubeApiKey', localApiKey);
    setApiKey(localApiKey); // Update context
    alert('Settings saved!');
    // Here you might also trigger a re-fetch of quota or other API-dependent data
  };

  const quotaPercentage = quotaLimit > 0 ? (quotaUsage / quotaLimit) * 100 : 0;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>

      <div className="mb-6 p-4 border rounded shadow-sm">
        <h2 className="text-xl font-semibold mb-2">YouTube API Key</h2>
        <p className="text-sm text-gray-600 mb-2">
          Enter your YouTube Data API v3 key. This key is stored in your browser's session storage and is required to fetch data.
        </p>
        <input
          type="text"
          value={localApiKey}
          onChange={handleApiKeyChange}
          placeholder="Enter your YouTube API Key"
          className="w-full p-2 border rounded mb-2"
        />
        <button
          onClick={handleSaveSettings}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Save API Key
        </button>
      </div>

      <div className="p-4 border rounded shadow-sm">
        <h2 className="text-xl font-semibold mb-2">API Quota Usage</h2>
        {localApiKey ? (
          <>
            <p className="text-sm text-gray-600 mb-1">
              Daily Quota Usage: {quotaUsage.toLocaleString()} / {quotaLimit.toLocaleString()} units
            </p>
            <div className="w-full bg-gray-200 rounded-full h-6 mb-2">
              <div
                className={`h-6 rounded-full ${quotaPercentage > 80 ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${quotaPercentage}%` }}
              >
                <span className="flex justify-center items-center h-full text-xs font-semibold text-white">
                  {quotaPercentage.toFixed(1)}%
                </span>
              </div>
            </div>
            {quotaPercentage > 80 && (
              <p className="text-red-600 text-sm font-semibold">
                Warning: You have used over 80% of your daily API quota.
              </p>
            )}
          </>
        ) : (
          <p className="text-gray-600">
            Please enter and save your API key to view quota usage.
          </p>
        )}
      </div>
    </div>
  );
};

export default SettingsPage; 