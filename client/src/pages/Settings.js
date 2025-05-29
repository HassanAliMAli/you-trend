import React, { useState, useEffect, useContext } from 'react';
// import { ApiContext } from '../contexts/ApiContext'; // Assuming you have/will have an ApiContext for API key
import { useApi } from '../contexts/ApiContext'; // Correct way to use the context

// Storage keys - ensure this matches ApiContext.js
const API_KEY_STORAGE_KEY = 'youtube_api_key';

const SettingsPage = () => {
  // const { apiKey, setApiKey, apiQuota, setApiQuota } = useContext(ApiContext); // Using ApiContext
  const { 
    saveApiKey, 
    getApiKey, 
    isApiKeyConfigured, 
    quotaUsage: contextQuotaUsage, /* Renaming to avoid conflict */
    getQuotaUsage /* Function to fetch quota */
  } = useApi(); 

  const [localApiKey, setLocalApiKey] = useState('');
  // const [quotaUsage, setQuotaUsage] = useState(0); // Example: 0% - Handled by contextQuotaUsage
  const [currentQuota, setCurrentQuota] = useState(null); // To store fetched quota data
  const [quotaLimit, setQuotaLimit] = useState(10000); // Default YouTube API quota, can be part of fetched quota data

  // Load API key from localStorage on component mount
  useEffect(() => {
    const storedApiKey = getApiKey(); // Use context's getter
    if (storedApiKey) {
      setLocalApiKey(storedApiKey);
    }
    // Fetch initial quota usage if API key is configured
    if (isApiKeyConfigured()) {
      fetchQuota();
    }
  }, [getApiKey, isApiKeyConfigured]); // Add getQuotaUsage to dependencies if it changes identities

  const fetchQuota = async () => {
    try {
      const quotaData = await getQuotaUsage(); // Assuming getQuotaUsage fetches and returns { usage, limit }
      if (quotaData) {
        setCurrentQuota(quotaData);
        // Assuming quotaData might contain a limit, otherwise keep default or make it static
        if (quotaData.limit) { 
            setQuotaLimit(quotaData.limit);
        }
      }
    } catch (error) {
      console.error("Failed to fetch quota:", error);
      // Handle error (e.g., display a message to the user)
    }
  };
  
  // Effect to update currentQuota when contextQuotaUsage changes
  useEffect(() => {
    if (contextQuotaUsage) {
        setCurrentQuota(contextQuotaUsage);
        if (contextQuotaUsage.limit) {
            setQuotaLimit(contextQuotaUsage.limit);
        }
    }
  }, [contextQuotaUsage]);


  const handleApiKeyChange = (e) => {
    setLocalApiKey(e.target.value);
  };

  const handleSaveSettings = () => {
    // sessionStorage.setItem('youtubeApiKey', localApiKey);
    // setApiKey(localApiKey); // Update context
    console.log('SettingsPage (handleSaveSettings): Saving API key:', localApiKey); // Log before saving
    saveApiKey(localApiKey); // Use context's save function
    alert('Settings saved! API Key stored in localStorage.');
    // Here you might also trigger a re-fetch of quota or other API-dependent data
    // For example, if an API key is newly added, fetch quota:
    if (localApiKey) {
        fetchQuota();
    }
  };

  // Use currentQuota for display, which is updated from context or direct fetch
  const displayQuotaUsage = currentQuota?.usage_amount || 0; 
  const displayQuotaLimit = currentQuota?.limit_amount || quotaLimit;
  const quotaPercentage = displayQuotaLimit > 0 ? (displayQuotaUsage / displayQuotaLimit) * 100 : 0;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>

      <div className="mb-6 p-4 border rounded shadow-sm">
        <h2 className="text-xl font-semibold mb-2">YouTube API Key</h2>
        <p className="text-sm text-gray-600 mb-2">
          Enter your YouTube Data API v3 key. This key is stored in your browser's local storage and is required to fetch data.
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
        {isApiKeyConfigured() ? (
          <>
            <p className="text-sm text-gray-600 mb-1">
              Daily Quota Usage: {displayQuotaUsage.toLocaleString()} / {displayQuotaLimit.toLocaleString()} units
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
            <button
                onClick={fetchQuota}
                className="mt-2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-1 px-3 rounded text-sm"
            >
                Refresh Quota
            </button>
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