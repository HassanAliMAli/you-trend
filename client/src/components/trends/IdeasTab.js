import React from 'react';
import { FaLightbulb } from 'react-icons/fa';

const IdeasTab = ({ results }) => {
  return (
    <div className="space-y-6">
      {results.ideas && results.ideas.length > 0 ? (
        results.ideas.map((idea, index) => (
          <div key={index} className="card">
            <div className="flex items-start">
              <div className="w-12 h-12 flex-shrink-0 bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300 rounded-lg flex items-center justify-center">
                <FaLightbulb size={24} />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">{idea}</h3>
                
                <div className="mt-3">
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <span className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 px-2 py-0.5 rounded-full text-xs font-medium">
                      Trending Topic
                    </span>
                    <span className="ml-3 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 px-2 py-0.5 rounded-full text-xs font-medium">
                      Based on {results.videos.length} videos
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          No video ideas generated for this query.
        </div>
      )}
    </div>
  );
};

export default IdeasTab;
