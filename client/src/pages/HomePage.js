import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaChartLine, FaExchangeAlt, FaFileAlt, FaArrowRight, FaCog } from 'react-icons/fa';
import ApiKeyForm from '../components/ApiKeyForm';
import { isApiKeyConfigured, getApiKey } from '../utils/api';

const HomePage = () => {
  const [apiConfigured, setApiConfigured] = useState(false);
  
  useEffect(() => {
    // Check if API key is configured in localStorage
    const checkApiStatus = () => {
      const hasApiKey = isApiKeyConfigured();
      setApiConfigured(hasApiKey);
      
      if (hasApiKey) {
        const apiKey = getApiKey();
        console.log('Using API key from localStorage:', apiKey ? `${apiKey.substring(0, 5)}...${apiKey.substring(apiKey.length - 5)}` : 'Not available');
      }
    };
    
    checkApiStatus();
    
    // Listen for storage changes (in case API key is updated in another tab)
    const handleStorageChange = () => {
      checkApiStatus();
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);
  return (
    <div className="container mx-auto px-4 py-8">
      <section className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Welcome to YouTrend</h1>
        <p className="text-xl text-gray-700 dark:text-gray-300">
          Your complete YouTube trend analysis tool for content creators and marketers.
        </p>
      </section>
      
      <section className="mb-12">
        <div className="flex items-center mb-4">
          <FaCog className="text-primary-600 mr-2" />
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
            {apiConfigured ? 'API Configuration' : 'API Configuration Required'}
          </h2>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 mb-4">
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            YouTrend requires a YouTube API key to fetch data. You can:
          </p>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-2">
            <li>Enter your YouTube API key below (it will be stored in your browser)</li>
            <li>API key will be sent with each request and won't depend on server configuration</li>
            <li>Your key will persist across page refreshes but not across different browsers or devices</li>
          </ul>
        </div>
        <ApiKeyForm />
      </section>
      
      <section className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          YouTube Trend Analysis
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8">
          Discover trending topics, analyze top-performing channels, and get data-driven
          insights to boost your YouTube content strategy
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link to="/trends" className="btn-primary flex items-center justify-center">
            <span>Analyze Trends</span>
            <FaArrowRight className="ml-2" />
          </Link>
          <Link to="/compare" className="btn-secondary flex items-center justify-center">
            <span>Compare Niches</span>
            <FaArrowRight className="ml-2" />
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
          Key Features
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="card flex flex-col items-center text-center p-6">
            <div className="bg-primary-100 dark:bg-primary-900 p-3 rounded-full mb-4">
              <FaChartLine className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Trend Analysis
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Discover trending topics, keywords, and content formats. Analyze top-performing videos 
              and channels to understand what's working in your niche.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card flex flex-col items-center text-center p-6">
            <div className="bg-primary-100 dark:bg-primary-900 p-3 rounded-full mb-4">
              <FaExchangeAlt className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Niche Comparison
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Compare different niches side-by-side to identify growth opportunities, analyze 
              competitive landscapes, and find the best fit for your content.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card flex flex-col items-center text-center p-6">
            <div className="bg-primary-100 dark:bg-primary-900 p-3 rounded-full mb-4">
              <FaFileAlt className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Detailed Reports
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Generate comprehensive reports with actionable insights, content ideas, and optimization 
              tips to enhance your YouTube strategy.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Step 1 */}
          <div className="card flex flex-col p-6 relative">
            <div className="absolute -top-4 -left-4 bg-primary-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">
              1
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 mt-2">
              Search for a Topic
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Enter your keywords, select filters like country, language, and date range to focus your analysis.
            </p>
          </div>

          {/* Step 2 */}
          <div className="card flex flex-col p-6 relative">
            <div className="absolute -top-4 -left-4 bg-primary-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">
              2
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 mt-2">
              Analyze the Results
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Review top-performing channels, videos, and trending topics with detailed metrics and insights.
            </p>
          </div>

          {/* Step 3 */}
          <div className="card flex flex-col p-6 relative">
            <div className="absolute -top-4 -left-4 bg-primary-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">
              3
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 mt-2">
              Get Actionable Insights
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Receive content ideas, optimization tips, and generate reports to enhance your content strategy.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white rounded-xl p-8 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Boost Your YouTube Strategy?</h2>
        <p className="text-xl mb-6 max-w-2xl mx-auto">
          Start analyzing trends and get data-driven insights to grow your channel today!
        </p>
        <Link to="/trends" className="inline-block px-6 py-3 bg-white text-primary-600 font-bold rounded-lg hover:bg-gray-100 transition duration-300">
          Get Started Now
        </Link>
      </section>
    </div>
  );
};

export default HomePage;
