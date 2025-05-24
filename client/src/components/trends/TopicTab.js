import React from 'react';
import { FaTags } from 'react-icons/fa';
import ChartComponent from '../ChartComponent';

const TopicTab = ({ results, topicsChartData, searchQuery }) => {
  return (
    <div className="space-y-6">
      {/* Topics Pie Chart */}
      {topicsChartData && results.topics && results.topics.length > 0 && (
        <div className="card p-4">
          <div className="flex items-center mb-4">
            <FaTags className="text-primary-500 mr-2" />
            <h3 className="text-lg font-medium">Topic Popularity</h3>
          </div>
          <div className="h-80 flex justify-center">
            <div className="w-full max-w-md">
              <ChartComponent 
                type="pie" 
                data={topicsChartData} 
                title={`Popular ${searchQuery} Topics`}
                height={300}
              />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
            Distribution of popular topics in the {searchQuery} category
          </p>
        </div>
      )}
      
      {/* Topic Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {results.topics && results.topics.length > 0 ? (
          results.topics.map((topic) => (
            <div key={topic.name} className="card p-4">
              <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-1">{topic.name}</h3>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                <p>Popularity: <span className="font-bold">{topic.count}</span> videos</p>
                <div className="mt-3">
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div 
                      className="bg-primary-600 h-2.5 rounded-full" 
                      style={{ width: `${Math.min(100, (topic.count / 10) * 100)}%` }}
                    ></div>
                  </div>
                </div>
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  This topic is trending in the {searchQuery} category
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="md:col-span-3 text-center text-gray-500 dark:text-gray-400 py-8">
            No topics found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};

export default TopicTab;
