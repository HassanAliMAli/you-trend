/**
 * Utility functions for preparing and formatting chart data
 */

/**
 * Format numbers with K/M suffixes for readability
 * @param {number} num - The number to format
 * @returns {string} Formatted number string
 */
export const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

/**
 * Prepare channel chart data from API results
 * @param {Object} data - Channel data from API
 * @returns {Object} Formatted chart data for the channels
 */
export const prepareChannelChartData = (data) => {
  if (!data || !data.channels || data.channels.length === 0) return null;
  
  const channelLabels = data.channels.map(channel => channel.snippet.title);
  const subscriberCounts = data.channels.map(channel => parseInt(channel.statistics.subscriberCount || 0));
  const videoCounts = data.channels.map(channel => parseInt(channel.statistics.videoCount || 0));
  
  return {
    labels: channelLabels,
    datasets: [
      {
        label: 'Subscribers',
        data: subscriberCounts,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: 'Videos',
        data: videoCounts,
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      }
    ]
  };
};

/**
 * Prepare video chart data from API results
 * @param {Object} data - Video data from API
 * @returns {Object} Formatted chart data for the videos
 */
export const prepareVideoChartData = (data) => {
  if (!data || !data.videos || data.videos.length === 0) return null;
  
  const videoLabels = data.videos.map(video => video.snippet.title.substring(0, 20) + '...');
  const viewCounts = data.videos.map(video => parseInt(video.statistics.viewCount || 0));
  const likeCounts = data.videos.map(video => parseInt(video.statistics.likeCount || 0));
  
  return {
    labels: videoLabels,
    datasets: [
      {
        label: 'Views',
        data: viewCounts,
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
      },
      {
        label: 'Likes',
        data: likeCounts,
        backgroundColor: 'rgba(139, 92, 246, 0.5)',
        borderColor: 'rgba(139, 92, 246, 1)',
        borderWidth: 1,
      }
    ]
  };
};

/**
 * Prepare topics chart data from API results
 * @param {Object} data - Topic data from API
 * @returns {Object} Formatted chart data for the topics
 */
export const prepareTopicsChartData = (data) => {
  if (!data || !data.topics || data.topics.length === 0) return null;
  
  const topicLabels = data.topics.map(topic => topic.name);
  const topicCounts = data.topics.map(topic => topic.count);
  
  return {
    labels: topicLabels,
    datasets: [
      {
        label: 'Popularity',
        data: topicCounts,
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      }
    ]
  };
};
