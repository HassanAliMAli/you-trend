import axios from 'axios';

// When deployed as a single app, the API is at the same URL as the frontend
// In development, we use localhost:8000
const isDevelopment = process.env.NODE_ENV === 'development';

// In development, use localhost:8000
// In production, API requests will go to the same domain the app is hosted on
const API_BASE_URL = isDevelopment ? 'http://localhost:8000' : '';

// Log the current environment and API URL being used
console.log(`Running in ${process.env.NODE_ENV} mode`);
console.log(`Using API base URL: ${API_BASE_URL} (empty string means same domain)`);

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Add a timeout to prevent long-hanging requests
  timeout: 10000,
});

// Helper functions for YouTube API key management
const API_KEY_STORAGE_KEY = 'youtube_api_key';

// Save API key to localStorage
export const saveApiKey = (apiKey) => {
  localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
};

// Get API key from localStorage
export const getApiKey = () => {
  return localStorage.getItem(API_KEY_STORAGE_KEY);
};

// Remove API key from localStorage
export const removeApiKey = () => {
  localStorage.removeItem(API_KEY_STORAGE_KEY);
};

// Check if API key is configured
export const isApiKeyConfigured = () => {
  return !!getApiKey();
};

// API functions for different endpoints
export const apiService = {
  // Get API status
  getStatus: async () => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Error getting API status:', error);
      throw error;
    }
  },

  // Get quota usage
  getQuotaUsage: async () => {
    try {
      const response = await api.get('/api/quota');
      return response.data;
    } catch (error) {
      console.error('Error getting quota usage:', error);
      throw error;
    }
  },

  // Analyze trends
  analyzeTrends: async (params) => {
    try {
      console.log('Sending trends analysis request with params:', params);
      
      // Ensure we have a valid query
      if (!params || !params.query) {
        throw new Error('A search query is required for trend analysis');
      }
      
      // Get the YouTube API key from localStorage
      const apiKey = getApiKey();
      
      // Pass through the parameters exactly as received
      // The TrendsPage component now sends max_results directly
      const requestData = {
        query: params.query,
        // Use params.max_results directly (TrendsPage now sends this)
        max_results: params.max_results,
        // Include API key in the request if available
        api_key: apiKey || undefined,
        // Add region filtering parameters
        country: params.country,
        duration: params.duration,
        order: params.order
      };
      
      console.log('API REQUEST - exact max_results value:', requestData.max_results);
      console.log('API REQUEST - max_results type:', typeof requestData.max_results);
      console.log('Full request data:', JSON.stringify(requestData));
      
      console.log('Using API key from localStorage:', apiKey ? `${apiKey.substring(0, 5)}...${apiKey.substring(apiKey.length - 5)}` : 'Not configured');
      
      // Set proper content type and other headers
      const response = await api.post('/api/trends', requestData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Trends analysis response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error analyzing trends:', error);
      console.error('Error response:', error.response?.data || 'No response data');
      throw error;
    }
  },

  // Compare niches
  compareNiches: async (params) => {
    try {
      const response = await api.post('/api/compare', params);
      return response.data;
    } catch (error) {
      console.error('Error comparing niches:', error);
      throw error;
    }
  },

  // Generate report
  generateReport: async (params) => {
    try {
      const response = await api.post('/api/generate-report', params);
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  },
};

export default api;
