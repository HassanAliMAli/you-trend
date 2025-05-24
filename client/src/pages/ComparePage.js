import React, { useState } from 'react';
import { useApi } from '../contexts/ApiContext';
import { FaSpinner, FaExchangeAlt, FaTimes, FaPlus } from 'react-icons/fa';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ComparePage = () => {
  const { compareNiches, loading, error } = useApi();
  const [niches, setNiches] = useState(['', '']);
  const [formData, setFormData] = useState({
    country: 'Pakistan',
    max_results: 10
  });
  const [results, setResults] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleNicheChange = (index, value) => {
    const updatedNiches = [...niches];
    updatedNiches[index] = value;
    setNiches(updatedNiches);
  };

  const addNiche = () => {
    if (niches.length < 5) {
      setNiches([...niches, '']);
    }
  };

  const removeNiche = (index) => {
    // Keep at least 2 niches
    if (niches.length <= 2) return;
    
    const updatedNiches = [...niches];
    updatedNiches.splice(index, 1);
    setNiches(updatedNiches);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Filter out empty niches
    const filteredNiches = niches.filter(niche => niche.trim() !== '');
    
    if (filteredNiches.length < 2) {
      alert('Please enter at least 2 niches to compare');
      return;
    }
    
    try {
      console.log('Sending comparison request for niches:', filteredNiches);
      
      // Let's go back to using the context function but with better debugging
      const data = await compareNiches({
        niches: filteredNiches,
        max_results: formData.max_results,
        country: formData.country
      });
      
      console.log('Received comparison data:', data);
      
      // Create a fallback data structure if something is wrong with the response
      if (!data) {
        throw new Error('No data returned from server');
      }
      
      // Add the niches property to the results object
      // This ensures our component has access to the original query terms
      const enhancedData = {
        ...data,
        niches: filteredNiches
      };
      
      console.log('Setting results with enhanced data:', enhancedData);
      setResults(enhancedData);
      
      if (document.getElementById('results')) {
        window.scrollTo({ top: document.getElementById('results').offsetTop - 100, behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Error comparing niches:', err);
      // Display the error to the user
      alert(`Error: ${err.message || 'Failed to compare niches'}`);
    }
  };

  // Country options
  const countries = [
    { code: 'PK', name: 'Pakistan' },
    { code: 'US', name: 'United States' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'IN', name: 'India' },
    { code: 'CA', name: 'Canada' },
    { code: 'AU', name: 'Australia' }
  ];

  // Format large numbers
  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  // Prepare chart data
  const getChartData = () => {
    if (!results || !results.results) return null;

    const labels = results.niches || Object.keys(results.results);
    const viewsData = [];

    for (const niche of labels) {
      const nicheData = results.results[niche];
      if (nicheData && nicheData.metrics) {
        viewsData.push(nicheData.metrics.avg_views || 0);
      } else {
        viewsData.push(0);
      }
    }

    return {
      labels,
      datasets: [
        {
          label: 'Average Views',
          data: viewsData,
          backgroundColor: 'rgba(59, 130, 246, 0.7)', // blue
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1,
        }
      ]
    };
  };

  // Prepare engagement chart data
  const getEngagementChartData = () => {
    if (!results || !results.results) return null;

    const labels = results.niches || Object.keys(results.results);
    const engagementData = [];

    for (const niche of labels) {
      const nicheData = results.results[niche];
      if (nicheData && nicheData.metrics) {
        engagementData.push((nicheData.metrics.avg_engagement || 0) * 100);
      } else {
        engagementData.push(0);
      }
    }

    return {
      labels,
      datasets: [
        {
          label: 'Engagement Rate (%)',
          data: engagementData,
          backgroundColor: 'rgba(52, 211, 153, 0.7)', // green
          borderColor: 'rgba(52, 211, 153, 1)',
          borderWidth: 1,
        }
      ]
    };
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Average Views by Niche',
      },
    },
  };

  const engagementChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Engagement Rate by Niche',
      },
    },
  };

  return (
    <div className="flex flex-col space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Compare YouTube Niches
        </h1>
        <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Compare different niches side by side to identify trends, growth opportunities, and competition levels
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div>
              <label className="block text-gray-700 dark:text-gray-300 font-medium mb-2">
                Niches to Compare
              </label>
              <div className="space-y-3">
                {niches.map((niche, index) => (
                  <div key={index} className="flex items-center">
                    <div className="relative flex-grow">
                      <input
                        type="text"
                        value={niche}
                        onChange={(e) => handleNicheChange(index, e.target.value)}
                        className="w-full pl-3 pr-10 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        placeholder={`Niche ${index + 1} (e.g., gaming, cooking)`}
                      />
                    </div>
                    {niches.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeNiche(index)}
                        className="ml-2 p-2 text-red-500 hover:text-red-700 rounded-full hover:bg-red-100 dark:hover:bg-red-900"
                        title="Remove niche"
                      >
                        <FaTimes />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              {niches.length < 5 && (
                <button
                  type="button"
                  onClick={addNiche}
                  className="mt-3 flex items-center text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  <FaPlus className="mr-1" /> Add another niche
                </button>
              )}
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 dark:text-gray-300 font-medium mb-2">
                  Country
                </label>
                <select
                  name="country"
                  value={formData.country}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  {countries.map((country) => (
                    <option key={country.code} value={country.name}>
                      {country.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-gray-700 dark:text-gray-300 font-medium mb-2">
                  Results per Niche
                </label>
                <select
                  name="max_results"
                  value={formData.max_results}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="5">5 videos</option>
                  <option value="10">10 videos</option>
                  <option value="15">15 videos</option>
                  <option value="20">20 videos</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <FaSpinner className="animate-spin mr-2" />
                    Comparing...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <FaExchangeAlt className="mr-2" />
                    Compare Niches
                  </div>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md">
          <p>{error}</p>
        </div>
      )}

      {/* Results Section */}
      {results && results.results && (
        <div id="results" className="space-y-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Comparison Results
          </h2>

          {/* Charts */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card p-4">
              {getChartData() && (
                <Bar data={getChartData()} options={chartOptions} />
              )}
            </div>
            <div className="card p-4">
              {getEngagementChartData() && (
                <Bar data={getEngagementChartData()} options={engagementChartOptions} />
              )}
            </div>
          </div>

          {/* Detailed Comparison Table */}
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Metric
                  </th>
                  {results.niches && results.niches.map((niche) => (
                    <th key={niche} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      {niche}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    Average Views
                  </td>
                  {results.niches && results.niches.map((niche) => (
                    <td key={niche} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatNumber(results.results[niche]?.metrics?.avg_views || 0)}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    Engagement Rate
                  </td>
                  {results.niches && results.niches.map((niche) => (
                    <td key={niche} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {((results.results[niche]?.metrics?.avg_engagement || 0) * 100).toFixed(2)}%
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    Video Count
                  </td>
                  {results.niches && results.niches.map((niche) => (
                    <td key={niche} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {results.results[niche]?.metrics?.video_count || 0}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    Top Keywords
                  </td>
                  {results.niches && results.niches.map((niche) => (
                    <td key={niche} className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {results.results[niche]?.keywords && results.results[niche].keywords.length > 0 ? (
                        <ul className="list-disc list-inside">
                          {results.results[niche].keywords.slice(0, 5).map((keyword, idx) => (
                            <li key={idx}>{keyword}</li>
                          ))}
                        </ul>
                      ) : (
                        'No keywords found'
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparePage;
