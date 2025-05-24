import React from 'react';
import { FaSearch } from 'react-icons/fa';
import LoadingSpinner from '../LoadingSpinner';

const SearchForm = ({ 
  searchQuery, 
  setSearchQuery, 
  country, 
  setCountry, 
  videoDuration, 
  setVideoDuration, 
  sortOrder, 
  setSortOrder, 
  maxResults, 
  setMaxResults, 
  loading, 
  handleAnalyzeClick 
}) => {
  return (
    <div className="card">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search Keyword or Topic</label>
          <div className="relative">
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="news"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyzeClick()}
            />
            <FaSearch className="absolute left-3 top-3 text-gray-400" />
          </div>
        </div>

        {/* Country Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
          <select 
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          >
            <option>Global</option>
            <option>Pakistan</option>
            <option>United States</option>
            <option>United Kingdom</option>
            <option>Canada</option>
            <option>Australia</option>
            <option>India</option>
          </select>
        </div>

        {/* Video Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Video Duration</label>
          <select 
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            value={videoDuration}
            onChange={(e) => setVideoDuration(e.target.value)}
          >
            <option>Any Duration</option>
            <option>Short (&lt; 4 minutes)</option>
            <option>Medium (4-20 minutes)</option>
            <option>Long (&gt; 20 minutes)</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sort Order</label>
          <select 
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option>View Count</option>
            <option>Relevance</option>
            <option>Rating</option>
          </select>
        </div>

        {/* Maximum Results */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Maximum Results</label>
          <input 
            type="number" 
            min="5" 
            max="50" 
            value={maxResults} 
            onChange={(e) => setMaxResults(e.target.value)}
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
          />
        </div>
      </div>

      {/* Analyze Button */}
      <button 
        onClick={handleAnalyzeClick}
        disabled={loading || !searchQuery.trim()}
        className="flex items-center justify-center w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-md transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
      >
        {loading ? (
          <>
            <LoadingSpinner size="sm" color="white" />
            <span className="ml-2">Analyzing...</span>
          </>
        ) : (
          <>
            <FaSearch className="mr-2" /> Analyze Trends
          </>
        )}
      </button>
    </div>
  );
};

export default SearchForm;
