import React, { useState } from 'react';
import { FaYoutube, FaTags, FaLightbulb } from 'react-icons/fa';
import { useApi } from '../contexts/ApiContext';
import { formatNumber, prepareChannelChartData, prepareVideoChartData, prepareTopicsChartData } from '../utils/chartUtils';

// Import components
import SearchForm from '../components/trends/SearchForm';
import VideoTab from '../components/trends/VideoTab';
import ChannelTab from '../components/trends/ChannelTab';
import TopicTab from '../components/trends/TopicTab';
import IdeasTab from '../components/trends/IdeasTab';

const TrendsPage = () => {
  const { analyzeTrends } = useApi();
  const [activeTab, setActiveTab] = useState('videos');
  const [searchQuery, setSearchQuery] = useState('');
  const [country, setCountry] = useState('Global');
  const [videoDuration, setVideoDuration] = useState('Any Duration');
  const [sortOrder, setSortOrder] = useState('View Count');
  const [maxResults, setMaxResults] = useState(10);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  // Chart data states
  const [channelChartData, setChannelChartData] = useState(null);
  const [videoChartData, setVideoChartData] = useState(null);
  const [topicsChartData, setTopicsChartData] = useState(null);

  /**
   * Handle the analyze button click
   * Fetches trend data from the API and prepares chart data
   */
  const handleAnalyzeClick = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setResults(null);
      
      // Convert maxResults to number
      const numResults = parseInt(maxResults, 10);
      
      const response = await analyzeTrends({
        query: searchQuery.trim(),
        max_results: numResults,
        country: country,
        duration: videoDuration !== 'Any Duration' ? videoDuration : undefined,
        order: sortOrder
      });
      
      setResults(response);
      
      // Prepare chart data using utility functions
      setChannelChartData(prepareChannelChartData(response));
      setVideoChartData(prepareVideoChartData(response));
      setTopicsChartData(prepareTopicsChartData(response));
    } catch (error) {
      console.error('Error in trend analysis:', error);
      setError(error.response?.data?.error || error.message || 'An error occurred while analyzing trends');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          YouTube Trend Analysis
        </h1>
        <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Discover trending content, top channels, and get data-driven insights for your YouTube strategy
        </p>
      </div>

      {/* Search Form - Using extracted component */}
      <SearchForm
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        country={country}
        setCountry={setCountry}
        videoDuration={videoDuration}
        setVideoDuration={setVideoDuration}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
        maxResults={maxResults}
        setMaxResults={setMaxResults}
        loading={loading}
        handleAnalyzeClick={handleAnalyzeClick}
      />

      {/* Error Message */}
      {error && (
        <div className="mb-8 p-4 bg-red-100 text-red-800 rounded-md border border-red-200 dark:bg-red-900 dark:text-red-100 dark:border-red-700">
          <p className="font-medium">An error occurred while analyzing trends</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="mb-8">
          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
            <button
              className={`py-2 px-4 border-b-2 font-medium text-sm ${activeTab === 'videos' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              onClick={() => setActiveTab('videos')}
            >
              <FaYoutube className="inline mr-2" /> Videos
            </button>
            <button
              className={`py-2 px-4 border-b-2 font-medium text-sm ${activeTab === 'channels' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              onClick={() => setActiveTab('channels')}
            >
              <FaYoutube className="inline mr-2" /> Channels
            </button>
            <button
              className={`py-2 px-4 border-b-2 font-medium text-sm ${activeTab === 'topics' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              onClick={() => setActiveTab('topics')}
            >
              <FaTags className="inline mr-2" /> Topics
            </button>
            <button
              className={`py-2 px-4 border-b-2 font-medium text-sm ${activeTab === 'ideas' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'}`}
              onClick={() => setActiveTab('ideas')}
            >
              <FaLightbulb className="inline mr-2" /> Video Ideas
            </button>
          </div>

          {/* Videos Tab - Using extracted component */}
          {activeTab === 'videos' && (
            <VideoTab 
              results={results} 
              videoChartData={videoChartData}
              searchQuery={searchQuery} 
              formatNumber={formatNumber} 
            />
          )}

          {/* Channels Tab - Using extracted component */}
          {activeTab === 'channels' && (
            <ChannelTab 
              results={results} 
              channelChartData={channelChartData}
              searchQuery={searchQuery} 
              formatNumber={formatNumber} 
            />
          )}

          {/* Topics Tab - Using extracted component */}
          {activeTab === 'topics' && (
            <TopicTab 
              results={results} 
              topicsChartData={topicsChartData}
              searchQuery={searchQuery} 
            />
          )}

          {/* Ideas Tab - Using extracted component */}
          {activeTab === 'ideas' && (
            <IdeasTab results={results} />
          )}
        </div>
      )}
    </div>
  );
};

export default TrendsPage;
