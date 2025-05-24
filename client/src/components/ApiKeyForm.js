import React, { useState, useEffect } from 'react';
import api, { apiService, saveApiKey, getApiKey, isApiKeyConfigured } from '../utils/api';
import { FaKey, FaCheckCircle, FaTimesCircle, FaTrash } from 'react-icons/fa';

const ApiKeyForm = () => {
  const [apiKey, setApiKey] = useState('');
  const [isConfigured, setIsConfigured] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  const [savedKey, setSavedKey] = useState('');

  // Check if API key is already configured in localStorage
  useEffect(() => {
    // Get API key from localStorage
    const storedApiKey = getApiKey();
    if (storedApiKey) {
      setIsConfigured(true);
      setSavedKey(storedApiKey);
      // Show the first and last 5 characters of the key for reference
      const maskedKey = storedApiKey.length > 10 ? 
        `${storedApiKey.substring(0, 5)}...${storedApiKey.substring(storedApiKey.length - 5)}` : 
        '***********';
      setMessage(`Using API key: ${maskedKey}`);
      setMessageType('success');
    } else {
      setIsConfigured(false);
      setMessage('No YouTube API key configured');
      setMessageType('error');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setMessage('Please enter a valid API key');
      setMessageType('error');
      return;
    }

    setIsSubmitting(true);
    setMessage('');

    try {
      // Save API key to localStorage
      saveApiKey(apiKey.trim());
      setSavedKey(apiKey.trim());
      
      // Show success message with masked key
      const maskedKey = apiKey.length > 10 ? 
        `${apiKey.substring(0, 5)}...${apiKey.substring(apiKey.length - 5)}` : 
        '***********';
      
      setIsConfigured(true);
      setMessage(`API key saved successfully: ${maskedKey}`);
      setMessageType('success');
      setApiKey(''); // Clear input field
      
      // Test the API key with a simple request
      try {
        // Make a test request to verify the API key works
        await apiService.getQuotaUsage();
      } catch (testError) {
        console.log('API key saved but test request failed:', testError);
        // We'll still keep the key saved even if the test request fails
      }
    } catch (error) {
      setMessage('Error saving API key: ' + (error.message || 'Unknown error'));
      setMessageType('error');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Function to clear the saved API key
  const handleClearApiKey = () => {
    // Remove API key from localStorage
    localStorage.removeItem('youtrend_youtube_api_key');
    
    // Update state
    setIsConfigured(false);
    setSavedKey('');
    setMessage('API key removed successfully');
    setMessageType('success');
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 mb-6">
      <div className="flex items-center mb-4">
        <FaKey className="text-primary-500 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white">YouTube API Configuration</h2>
      </div>

      {isConfigured ? (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center text-green-600 dark:text-green-400">
            <FaCheckCircle className="mr-2" />
            <span>YouTube API key is configured</span>
          </div>
          <button 
            onClick={handleClearApiKey}
            className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 flex items-center"
            title="Remove API key"
          >
            <FaTrash className="mr-1" />
            <span>Remove</span>
          </button>
        </div>
      ) : (
        <div className="flex items-center text-yellow-600 dark:text-yellow-400 mb-4">
          <FaTimesCircle className="mr-2" />
          <span>YouTube API key is not configured</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            YouTube API Key
          </label>
          <input
            type="text"
            id="apiKey"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder={isConfigured ? "Enter new API key to update" : "Enter your YouTube API key"}
            disabled={isSubmitting}
          />
        </div>

        {message && (
          <div className={`mb-4 p-3 rounded-md ${messageType === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'}`}>
            {message}
          </div>
        )}

        <button
          type="submit"
          className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-md transition duration-200 disabled:opacity-50"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : isConfigured ? 'Update API Key' : 'Save API Key'}
        </button>
      </form>

      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>To use this application, you need a YouTube Data API key.</p>
        <ol className="list-decimal list-inside mt-2 space-y-1">
          <li>Go to the <a href="https://console.developers.google.com/" target="_blank" rel="noopener noreferrer" className="text-primary-600 dark:text-primary-400 hover:underline">Google Developers Console</a></li>
          <li>Create a new project or select an existing one</li>
          <li>Enable the YouTube Data API v3</li>
          <li>Create credentials and copy your API key</li>
          <li>Paste it above and click "Configure API Key"</li>
        </ol>
      </div>
    </div>
  );
};

export default ApiKeyForm;
