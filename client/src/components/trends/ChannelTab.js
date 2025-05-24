import React from 'react';
import { FaChartBar } from 'react-icons/fa';
import ChartComponent from '../ChartComponent';

const ChannelTab = ({ results, channelChartData, searchQuery, formatNumber }) => {
  return (
    <div className="space-y-6">
      {/* Channel Subscribers Chart */}
      {channelChartData && results.channels && results.channels.length > 0 && (
        <div className="card p-4">
          <div className="flex items-center mb-4">
            <FaChartBar className="text-primary-500 mr-2" />
            <h3 className="text-lg font-medium">Channel Analytics</h3>
          </div>
          <div className="h-80">
            <ChartComponent 
              type="bar" 
              data={channelChartData} 
              title={`Top ${searchQuery} Channels Analytics`}
              height={300}
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: function(value) {
                        return formatNumber(value);
                      }
                    }
                  }
                }
              }}
            />
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
            Channel subscriber count and video count comparison
          </p>
        </div>
      )}
      
      {/* Channel Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {results.channels && results.channels.length > 0 ? (
          results.channels.map((channel) => (
            <div key={channel.id} className="card">
              <div className="flex">
                <div className="flex-shrink-0">
                  <img
                    src={channel.snippet.thumbnails.medium.url}
                    alt={channel.snippet.title}
                    className="w-32 h-32 rounded-lg object-cover"
                  />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-gray-800 dark:text-white">
                    {channel.snippet.title}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                    {channel.snippet.description}
                  </p>
                  <div className="mt-3 flex items-center text-xs text-gray-500 dark:text-gray-400 space-x-4">
                    <span>{formatNumber(channel.statistics.subscriberCount)} subscribers</span>
                    <span>{formatNumber(channel.statistics.videoCount)} videos</span>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="md:col-span-2 text-center text-gray-500 dark:text-gray-400 py-8">
            No channels found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};

export default ChannelTab;
