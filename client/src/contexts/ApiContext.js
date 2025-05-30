import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// Create context
const ApiContext = createContext();

// API base URL - handle both absolute and relative URLs
let API_BASE_URL = process.env.REACT_APP_API_URL || '';

// If API_BASE_URL is empty, we're using relative URLs on the same domain
// otherwise we need to use the full URL provided
if (!API_BASE_URL) {
  // We're on the same domain, use relative URLs
  console.log('Using relative URLs for API endpoints');
  API_BASE_URL = '';
} else {
  // Using a different domain, ensure it has the proper format
  if (!API_BASE_URL.startsWith('http')) {
    API_BASE_URL = 'https://' + API_BASE_URL;
  }
  console.log('Using external API URL:', API_BASE_URL);
}

// Storage keys
const SEARCH_HISTORY_KEY = 'youtrend_search_history';
const API_KEY_STORAGE_KEY = 'youtube_api_key';

export const ApiProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quotaUsage, setQuotaUsage] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [searchResults] = useState(null);
  const [comparisonResults, setComparisonResults] = useState(null);

  // Create axios instance with proper URL handling
  const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    // Add timeout to all requests
    timeout: 15000 // 15 second timeout
  });
  
  // Add debugging interceptor to log all requests
  api.interceptors.request.use(request => {
    console.log('API Request:', request.method?.toUpperCase(), request.url);
    return request;
  });
  
  // Add response interceptor to handle errors consistently
  api.interceptors.response.use(
    response => {
      console.log('API Response:', response.status, response.config.url);
      return response;
    },
    error => {
      console.error('API Error:', error.message, error.config?.url);
      return Promise.reject(error);
    }
  );
  
  // Load search history from localStorage on component mount
  useEffect(() => {
    // Log current API key status on mount
    const currentKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    console.log(`ApiContext: Provider mounted. Initial API key from localStorage: ${currentKey}`);

    const storedHistory = localStorage.getItem(SEARCH_HISTORY_KEY);
    if (storedHistory) {
      try {
        setSearchHistory(JSON.parse(storedHistory));
      } catch (err) {
        console.error('Error parsing search history:', err);
        // If there's an error, reset the history
        localStorage.removeItem(SEARCH_HISTORY_KEY);
      }
    }
  }, []);
  
  // Save a search to history
  const saveSearchToHistory = (search) => {
    // Create a unique ID for the search
    const id = `search-${Date.now()}`;
    
    // Format the date
    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().split('T')[0]; // YYYY-MM-DD format
    
    // Create the search history entry
    const searchEntry = {
      id: id,
      name: search.title || search.query,
      date: formattedDate,
      type: search.type, // 'trend' or 'compare'
      data: search.data,
      params: search.params
    };
    
    // Add to state and localStorage
    const updatedHistory = [searchEntry, ...searchHistory.slice(0, 4)]; // Keep only the latest 5 including the new one
    setSearchHistory(updatedHistory);
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(updatedHistory));
    
    return id;
  };
  
  // Get search history
  const getSearchHistory = () => {
    return searchHistory;
  };
  
  // Get a specific search from history
  const getSearchById = (id) => {
    return searchHistory.find(search => search.id === id);
  };

  // Analyze trends
  const analyzeTrends = async (params) => {
    setLoading(true);
    setError(null);
    const apiKey = getApiKey(); // Get API key using the context's getter
    // Log the retrieved key. This is important for debugging.
    console.log('ApiContext (analyzeTrends): API key from getApiKey():', apiKey);
    // Optional: For one more debug cycle, verify directly from localStorage.
    // console.log('ApiContext (analyzeTrends): API key directly from localStorage.getItem():', localStorage.getItem(API_KEY_STORAGE_KEY));

    let apiDuration = null;
    if (params.duration && params.duration !== 'Any Duration') {
      const durationMapping = {
        'Short (< 4 minutes)': 'short',
        'Medium (4-20 minutes)': 'medium',
        'Long (> 20 minutes)': 'long'
      };
      apiDuration = durationMapping[params.duration] || null;
    }

    let apiOrder = 'viewCount'; 
    if (params.order) {
      const orderMapping = {
        'View Count': 'viewCount',
        'Relevance': 'relevance',
        'Rating': 'rating',
        'Date': 'date'
      };
      apiOrder = orderMapping[params.order] || 'viewCount';
    }

    const requestParams = {
      query: params.query,
      max_results: params.max_results ? parseInt(params.max_results, 10) : 10,
      country: params.country || 'US', // Backend handles 'Global' specific interpretation
      api_key: apiKey, // Use the retrieved apiKey
      duration: apiDuration,
      order: apiOrder,
      category: params.category || null,
      published_after: params.published_after || null,
      published_before: params.published_before || null,
      language: params.language || null
    };

    // Remove any top-level undefined properties before sending
    Object.keys(requestParams).forEach(key => {
        if (requestParams[key] === undefined) {
            requestParams[key] = null; // Or delete requestParams[key]; Pydantic usually handles None/null for Optional fields
        }
    });

    try {
      console.log('ApiContext: sending requestParams for trends:', requestParams);
      const response = await api.post('/api/trends', requestParams);
      setQuotaUsage(response.data.quota_usage);
      
      // Process the data to ensure all tabs are properly organized for exporting
      const processedData = {
        // Original data
        ...response.data,
        // Add explicit tab structure for better organization when exporting
        tabs: {
          videos: response.data.videos || [],
          channels: response.data.channels || [],
          topics: response.data.topics || [],
          ideas: response.data.ideas || []
        },
        // Add analysis metadata
        analysisMetadata: {
          queryDate: new Date().toISOString(),
          trendDirection: response.data.topics.length > 0 ? 
            (response.data.topics[0].count > 10 ? 'Strongly Upward' : 'Moderate') : 'Neutral',
          contentGap: identifyContentGap(response.data),
          recommendedActions: generateRecommendations(response.data)
        }
      };
      
      // Save the search to history with enhanced data
      saveSearchToHistory({
        title: `${params.query} - ${params.country || 'Global'}`,
        query: params.query,
        type: 'trend',
        data: processedData,
        params: params // Save the original params
      });
      
      setLoading(false);
      return processedData;
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while analyzing trends');
      setLoading(false);
      throw err;
    }
  };

  // Helper function to identify content gaps based on data
  const identifyContentGap = (data) => {
    // Find topics with high count but few videos
    const topTopics = data.topics.slice(0, 3).map(t => t.name);
    const videoTopics = data.videos
      .flatMap(v => v.snippet?.title?.toLowerCase().split(' ') || [])
      .filter(word => word.length > 3);
    
    // Find topics that aren't well represented in videos
    const gaps = topTopics.filter(topic => {
      const matchCount = videoTopics.filter(word => word.includes(topic.toLowerCase())).length;
      return matchCount < 3; // Less than 3 videos contain this topic
    });
    
    return gaps.length > 0 ? 
      `Content gap identified for topics: ${gaps.join(', ')}` : 
      'No significant content gaps identified';
  };

  // Helper function to generate recommendations based on data
  const generateRecommendations = (data) => {
    const recommendations = [];
    
    // Add recommendations based on video performance
    if (data.videos.length > 0) {
      // Sort videos by views
      const sortedVideos = [...data.videos].sort((a, b) => 
        parseInt(b.statistics?.viewCount || 0) - parseInt(a.statistics?.viewCount || 0)
      );
      
      // Check for patterns in top performing videos
      const topVideos = sortedVideos.slice(0, 3);
      const topTitles = topVideos.map(v => v.snippet?.title || '');
      
      // Check for common keywords in top videos
      const commonWords = getCommonWords(topTitles);
      if (commonWords.length > 0) {
        recommendations.push(`Include keywords like "${commonWords.join('", "')}" in titles`); 
      }
      
      // Check format patterns (video length etc)
      recommendations.push('Focus on video formats similar to top performers');
    }
    
    // Add recommendation based on topics
    if (data.topics.length > 0) {
      recommendations.push(`Create content around trending topic: ${data.topics[0].name}`);
    }
    
    return recommendations;
  };

  // Helper function to find common words in an array of strings
  const getCommonWords = (strings) => {
    if (!strings || strings.length === 0) return [];
    
    // Get all words and their frequencies
    const wordCounts = {};
    strings.forEach(str => {
      const words = str.toLowerCase().split(/\s+/).filter(word => word.length > 3);
      words.forEach(word => {
        wordCounts[word] = (wordCounts[word] || 0) + 1;
      });
    });
    
    // Get words that appear in most strings
    return Object.entries(wordCounts)
      .filter(([_, count]) => count > strings.length / 2)
      .map(([word]) => word)
      .slice(0, 3); // Top 3 common words
  };

  // Compare niches - improved implementation with better error handling and fallbacks
  const compareNiches = async (params) => {
    setLoading(true);
    setError(null);
    const apiKey = getApiKey(); // Get API key using the context's getter
    // Log the retrieved key. This is important for debugging.
    console.log('ApiContext (compareNiches): API key from getApiKey():', apiKey);
    // Optional: For one more debug cycle, verify directly from localStorage.
    // console.log('ApiContext (compareNiches): API key directly from localStorage.getItem():', localStorage.getItem(API_KEY_STORAGE_KEY));

    const requestParams = { 
      // Explicitly list fields for CompareNichesRequestBody
      niches: params.niches ? params.niches.join(',') : '',
      max_results: params.max_results ? parseInt(params.max_results, 10) : 10,
      country: params.country || 'US',
      api_key: apiKey, // Use the retrieved apiKey
      // Add other fields from CompareNichesRequestBody if they exist in `params`
      // Example: some_other_field: params.some_other_field || null
    };

    // Remove any top-level undefined properties before sending
    Object.keys(requestParams).forEach(key => {
        if (requestParams[key] === undefined) {
            requestParams[key] = null;
        }
    });

    try {
      console.log('Attempting POST request to /api/compare with params:', requestParams);
      const response = await api.post('/api/compare', requestParams);
      console.log('POST request successful');
      
      console.log('Received comparison response:', response.data);
      
      // Ensure we have valid response data
      if (!response.data || !response.data.results) {
        // It's possible the backend sends an empty results array for valid but no-data scenarios
        // but top-level response.data must exist. results can be an empty object/array.
        if (response.data && typeof response.data.results === 'object') {
            // This is acceptable, proceed
        } else {
            throw new Error('Invalid response data structure');
        }
      }
      
      // Map the response data to a more usable format for the frontend
      const results = {};
      const responseNiches = params.niches || []; // Use original niches for keys

      // Process the niches data
      // The backend is expected to return results in the same order as the input niches string
      if (Array.isArray(response.data.results)) {
        response.data.results.forEach((nicheData, index) => {
          const nicheKey = responseNiches[index] || nicheData.niche || `niche_${index}`;
          
          results[nicheKey] = {
            niche: nicheKey,
            metrics: {
              avg_views: nicheData.views,
              avg_engagement: nicheData.engagement,
              video_count: nicheData.videoCount
            },
            keywords: nicheData.keywords?.map(kw => 
              typeof kw === 'string' ? kw : (kw.keyword || kw.name || ''))
              || []
          };
        });
      } else if (typeof response.data.results === 'object' && response.data.results !== null) {
        // Handle if backend returns results as an object keyed by niche name
         for (const key in response.data.results) {
            if (responseNiches.includes(key)) { // Ensure we only process requested niches
                const nicheData = response.data.results[key];
                 results[key] = {
                    niche: key,
                    metrics: {
                        avg_views: nicheData.views,
                        avg_engagement: nicheData.engagement,
                        video_count: nicheData.videoCount
                    },
                    keywords: nicheData.keywords?.map(kw => 
                        typeof kw === 'string' ? kw : (kw.keyword || kw.name || ''))
                        || []
                };
            }
        }
      }
      
      console.log('Processed comparison results:', results);
      
      const processedData = {
        niches: responseNiches, // Use the original array of niches
        results: results,
        is_mock: response.data.mock_data || false, // Ensure is_mock is explicitly false if not from backend
        timestamp: new Date().toISOString(),
        message: response.data.message || '',
        comparative_analysis: {
          viewsRatio: calculateViewsRatio(Object.values(results)),
          engagementDifference: calculateEngagementDifference(Object.values(results)),
          keywordOverlap: getKeywordOverlap(Object.values(results)),
          recommendedApproach: getRecommendedApproach(Object.values(results))
        }
      };
      
      setComparisonResults(processedData);
      setLoading(false);
      
      return processedData;
    } catch (err) {
      console.error('Error comparing niches:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to compare niches');
      setLoading(false);
      // Ensure NO MOCK DATA is returned. The component should handle the error state.
      throw err;
    }
  };
  
  // Helper functions for niche analysis - these are reserved for future implementation
  // and will be connected to the UI in a future update
  // eslint-disable-next-line no-unused-vars
  const getContentGapsForNiche = (nicheData) => {
    const keywords = nicheData.keywords || [];
    // Look for potential gaps based on keywords
    return keywords.length > 3 ?
      `Consider creating content focusing on combinations of ${keywords.slice(0, 3).join(' and ')}` :
      'Explore broader keyword combinations';
  };
  
  // eslint-disable-next-line no-unused-vars
  const getCompetitorAnalysis = (nicheData) => {
    return `${nicheData.metrics?.video_count || 0} videos in this niche with ` +
      `average engagement of ${(nicheData.metrics?.avg_engagement || 0) * 100}%`;
  };
  
  // eslint-disable-next-line no-unused-vars
  const getRecommendedTags = (nicheData) => {
    return (nicheData.keywords || []).concat(['youtube', 'trending', 'viral']);
  };
  
  // eslint-disable-next-line no-unused-vars
  const getBestDayToPublish = (nicheData) => {
    // This would be based on actual data analysis in a real implementation
    const days = ['Monday', 'Wednesday', 'Friday', 'Saturday', 'Sunday'];
    return days[Math.floor(Math.random() * days.length)];
  };
  
  // Comparative analysis functions
  const calculateViewsRatio = (nichesData) => {
    if (nichesData.length < 2) return 1;
    
    const niche1Views = nichesData[0].metrics?.avg_views || 1;
    const niche2Views = nichesData[1].metrics?.avg_views || 1;
    
    return (niche1Views / niche2Views).toFixed(2);
  };
  
  const calculateEngagementDifference = (nichesData) => {
    if (nichesData.length < 2) return 0;
    
    const niche1Engagement = nichesData[0].metrics?.avg_engagement || 0;
    const niche2Engagement = nichesData[1].metrics?.avg_engagement || 0;
    
    return ((niche1Engagement - niche2Engagement) * 100).toFixed(2) + '%';
  };
  
  const getKeywordOverlap = (nichesData) => {
    if (nichesData.length < 2) return [];
    
    const keywords1 = nichesData[0].keywords || [];
    const keywords2 = nichesData[1].keywords || [];
    
    return keywords1.filter(kw => keywords2.includes(kw));
  };
  
  const getRecommendedApproach = (nichesData) => {
    if (nichesData.length < 2) return 'Insufficient data for recommendations';
    
    const niche1Views = nichesData[0].metrics?.avg_views || 0;
    const niche2Views = nichesData[1].metrics?.avg_views || 0;
    const niche1Engagement = nichesData[0].metrics?.avg_engagement || 0;
    const niche2Engagement = nichesData[1].metrics?.avg_engagement || 0;
    
    if (niche1Views > niche2Views && niche1Engagement > niche2Engagement) {
      return `Focus on ${nichesData[0].niche} for both views and engagement`;
    } else if (niche1Views > niche2Views) {
      return `Use ${nichesData[0].niche} for views and ${nichesData[1].niche} for engagement`;
    } else if (niche1Engagement > niche2Engagement) {
      return `Use ${nichesData[1].niche} for views and ${nichesData[0].niche} for engagement`;
    } else {
      return `${nichesData[1].niche} outperforms ${nichesData[0].niche} - consider focusing there`;
    }
  };

  // Generate report
  const generateReport = async (params) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/generate-report', params);
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while generating the report');
      setLoading(false);
      throw err;
    }
  };

  // Get API status
  const getApiStatus = async () => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (err) {
      console.error('Error getting API status:', err);
      throw err;
    }
  };

  // Get quota usage
  const getQuotaUsage = async () => {
    try {
      const response = await api.get('/api/quota');
      setQuotaUsage(response.data);
      return response.data;
    } catch (err) {
      console.error('Error getting quota usage:', err);
      throw err;
    }
  };

  // Save API key to localStorage
  const saveApiKey = (apiKey) => {
    console.log('ApiContext (saveApiKey): Attempting to save API key:', apiKey);
    const trimmedApiKey = apiKey ? apiKey.trim() : ''; // Trim whitespace
    if (trimmedApiKey) {
      localStorage.setItem(API_KEY_STORAGE_KEY, trimmedApiKey);
      console.log('ApiContext (saveApiKey): API key saved to localStorage. Value now:', localStorage.getItem(API_KEY_STORAGE_KEY));
    } else {
      localStorage.removeItem(API_KEY_STORAGE_KEY); // Remove if key is empty after trim
      console.log('ApiContext (saveApiKey): API key was empty or whitespace, removed from localStorage.');
    }
    // Optionally, trigger a quota fetch or other updates here
    // For instance, if a key is newly added or changed:
    if (trimmedApiKey) {
      getQuotaUsage(); // Attempt to fetch quota with the new key
    } else {
      setQuotaUsage(null); // Clear quota if key is removed
    }
  };
  
  const getApiKey = () => {
    return localStorage.getItem(API_KEY_STORAGE_KEY);
  };
  
  const removeApiKey = () => {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
    // We don't need setApiKey since we're not tracking it in state
  };
  
  const isApiKeyConfigured = () => {
    return Boolean(getApiKey());
  };

  return (
    <ApiContext.Provider
      value={{
        loading,
        error,
        searchResults,
        comparisonResults,
        quotaUsage,
        searchHistory,
        analyzeTrends,
        compareNiches,
        generateReport,
        getApiStatus,
        getQuotaUsage,
        saveApiKey,
        getApiKey,
        removeApiKey,
        isApiKeyConfigured,
        getSearchHistory,
        getSearchById
      }}
    >
      {children}
    </ApiContext.Provider>
  );
};

// Custom hook to use the API context
export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};
