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
    
    try {
      // Pass parameters through directly without transformation
      // The TrendsPage component now sends max_results directly with the correct naming
      
      console.log('ApiContext: passing params directly to API:', params);
      console.log('ApiContext: max_results value:', params.max_results);
      
      const response = await api.post('/api/trends', params);
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
    console.log('Compare niches called with params:', params);
    
    try {
      // First, try to use the GET endpoint which is more reliable
      // This is a fallback mechanism to avoid timeout issues
      let response;
      let isUsingFallback = false;
      
      try {
        // First try the normal POST endpoint using our API instance
        console.log('Attempting POST request to /api/compare');
        
        response = await api.post('/api/compare', params);
        
        console.log('POST request successful');
      } catch (postError) {
        console.warn('POST request failed, trying GET fallback:', postError.message);
        
        // If POST fails, fall back to the GET endpoint
        isUsingFallback = true;
        console.log('Attempting GET request to /api/compare');
        
        // Use our configured API instance for consistency
        response = await api.get('/api/compare');
        
        console.log('GET fallback successful');
      }
      
      console.log('Received comparison response:', response.data);
      
      // Ensure we have valid response data
      if (!response.data || !response.data.results) {
        throw new Error('Invalid response data structure');
      }
      
      // Map the response data to a more usable format for the frontend
      const results = {};
      
      // Process the niches data
      if (Array.isArray(response.data.results)) {
        // If we get back results that don't match the requested niches,
        // we need to make sure we're using the correct niche names
        const niches = params.niches || [];
        
        response.data.results.forEach((niche, index) => {
          // Use the original niche name if available, otherwise use the one from the response
          const nicheKey = (index < niches.length) ? niches[index] : niche.niche;
          
          results[nicheKey] = {
            niche: nicheKey,
            metrics: {
              avg_views: niche.views,
              avg_engagement: niche.engagement,
              video_count: niche.videoCount
            },
            keywords: niche.keywords?.map(kw => 
              typeof kw === 'string' ? kw : (kw.keyword || kw.name || ''))
              || []
          };
        });
      }
      
      console.log('Processed comparison results:', results);
      
      const processedData = {
        niches: params.niches,
        results: results,
        is_mock: response.data.mock_data || isUsingFallback,
        timestamp: new Date().toISOString(),
        message: response.data.message || (isUsingFallback ? 'Using fallback data' : ''),
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
      setError(err.message || 'Failed to compare niches');
      setLoading(false);
      
      // Create mock data as a last resort fallback
      if (params.niches && params.niches.length > 0) {
        console.log('Creating emergency mock data for UI');
        
        // Completely static emergency fallback data so UI doesn't break
        const mockData = {
          niches: params.niches,
          results: {},
          is_mock: true,
          timestamp: new Date().toISOString(),
          message: 'Error connecting to server - showing emergency mock data',
          comparative_analysis: {
            viewsRatio: '1.5',
            engagementDifference: '2.5%',
            keywordOverlap: [],
            recommendedApproach: 'Unable to provide recommendations due to connection error'
          }
        };
        
        // Generate mock data for each niche
        params.niches.forEach(niche => {
          mockData.results[niche] = {
            niche: niche,
            metrics: {
              avg_views: Math.floor(Math.random() * 500000) + 10000,
              avg_engagement: (Math.random() * 0.1) + 0.01,
              video_count: Math.floor(Math.random() * 20) + 5
            },
            keywords: [
              `${niche} tips`, 
              `best ${niche}`, 
              `${niche} tutorial`, 
              `${niche} ideas`, 
              `${niche} advice`
            ]
          };
        });
        
        return mockData;
      }
      
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

  // API Key management
  const saveApiKey = (apiKey) => {
    localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
    // We don't need setApiKey since we're not tracking it in state
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
