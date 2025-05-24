import React from 'react';
import { FaChartLine } from 'react-icons/fa';
import ChartComponent from '../ChartComponent';

const VideoTab = ({ results, videoChartData, searchQuery, formatNumber }) => {
  return (
    <div className="space-y-6">
      {/* Videos View/Like Chart */}
      {videoChartData && results.videos && results.videos.length > 0 && (
        <div className="card p-4">
          <div className="flex items-center mb-4">
            <FaChartLine className="text-primary-500 mr-2" />
            <h3 className="text-lg font-medium">Video Performance</h3>
          </div>
          <div className="h-80">
            <ChartComponent 
              type="bar" 
              data={videoChartData} 
              title={`Top ${searchQuery} Videos Performance`}
              height={300}
              options={{
                indexAxis: 'y',
                scales: {
                  x: {
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
            View and like counts for top videos
          </p>
        </div>
      )}
      
      {/* Video Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {results.videos && results.videos.length > 0 ? (
          results.videos.map((video) => (
            <div key={video.id} className="card flex">
              <div className="flex-shrink-0 w-1/3">
                <a 
                  href={`https://www.youtube.com/watch?v=${video.id}`} 
                  target="_blank" 
                  rel="noreferrer"
                >
                  <img
                    src={video.snippet.thumbnails.medium.url}
                    alt={video.snippet.title}
                    className="w-full h-auto rounded-lg"
                  />
                </a>
              </div>
              <div className="flex-1 pl-4">
                <a 
                  href={`https://www.youtube.com/watch?v=${video.id}`} 
                  target="_blank" 
                  rel="noreferrer"
                  className="text-primary-600 dark:text-primary-400 hover:underline font-medium line-clamp-2"
                >
                  {video.snippet.title}
                </a>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {video.snippet.channelTitle}
                </p>
                <div className="mt-2 flex space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>{formatNumber(video.statistics.viewCount)} views</span>
                  <span>{formatNumber(video.statistics.likeCount)} likes</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="md:col-span-2 text-center text-gray-500 dark:text-gray-400 py-8">
            No videos found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoTab;
