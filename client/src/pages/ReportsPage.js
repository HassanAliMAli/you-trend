import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { FaFileAlt, FaSpinner, FaFileCsv, FaFilePdf, FaFileExcel, FaFileAlt as FaFileText } from 'react-icons/fa';
import { exportData, exportTopicsAndIdeas, exportCompleteData } from '../utils/exportUtils';

const ReportsPage = () => {
  const { generateReport, loading, error, searchHistory, getSearchById } = useApi();
  const [formData, setFormData] = useState({
    trend_data_id: '',
    report_format: 'pdf',
    include_charts: true
  });
  const [result, setResult] = useState(null);
  const [selectedSearch, setSelectedSearch] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Get the selected search data
      const searchData = getSearchById(formData.trend_data_id);
      
      if (!searchData) {
        throw new Error('Selected search data not found');
      }
      
      // Pass the selected search data to the report generator
      const data = await generateReport({
        ...formData,
        search_data: searchData
      });
      
      setResult(data);
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };
  
  // Update selected search when trend_data_id changes
  useEffect(() => {
    if (formData.trend_data_id) {
      const search = getSearchById(formData.trend_data_id);
      setSelectedSearch(search);
    } else {
      setSelectedSearch(null);
    }
  }, [formData.trend_data_id, getSearchById]);

  // Report formats with icons
  const reportFormats = [
    { value: 'pdf', name: 'PDF Document', icon: <FaFilePdf className="h-8 w-8 text-red-500" />, description: 'Fully formatted document with tables, charts, and sections' },
    { value: 'xlsx', name: 'Excel Spreadsheet', icon: <FaFileExcel className="h-8 w-8 text-green-500" />, description: 'Data in Excel format with multiple sheets for analysis' },
    { value: 'csv', name: 'CSV File', icon: <FaFileCsv className="h-8 w-8 text-gray-500" />, description: 'Simple data format for importing into any software' },
    { value: 'txt', name: 'Text Document', icon: <FaFileText className="h-8 w-8 text-blue-500" />, description: 'Plain text format for quick viewing' },
  ];
  
  // Handle exporting data based on the search type and format
  const handleExportData = () => {
    if (!selectedSearch || !selectedSearch.data) {
      alert('Please select a search to export');
      return;
    }
    
    const format = formData.report_format;
    const data = selectedSearch.data;
    
    if (selectedSearch.type === 'trend') {
      // Export trend data
      if (data.videos && data.videos.length > 0) {
        exportData(data.videos, 'videos', format);
      } else if (data.channels && data.channels.length > 0) {
        exportData(data.channels, 'channels', format);
      } else if ((data.topics && data.topics.length > 0) || (data.ideas && data.ideas.length > 0)) {
        exportTopicsAndIdeas(data, format);
      } else {
        alert('No data available to export');
      }
    } else if (selectedSearch.type === 'compare') {
      // Export comparison data
      exportCompleteData(data, format);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        Report Generation & Export
      </h1>
      <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">
        Generate and export reports from your trend analyses and niche comparisons.
      </p>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Report Generation Form */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Generate New Report
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Search Selection */}
            <div>
              <label htmlFor="trend_data_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Select Search Data
              </label>
              <select
                id="trend_data_id"
                name="trend_data_id"
                value={formData.trend_data_id}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                required
              >
                <option value="">-- Select a search --</option>
                {searchHistory.map((search) => (
                  <option key={search.id} value={search.id}>
                    {search.name} - {search.date}
                  </option>
                ))}
              </select>
            </div>

            {/* Report Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Report Format
              </label>
              <div className="grid grid-cols-2 gap-4">
                {reportFormats.map((format) => (
                  <div
                    key={format.value}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors duration-200 ${
                      formData.report_format === format.value
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                    }`}
                    onClick={() => setFormData({ ...formData, report_format: format.value })}
                  >
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="report_format"
                        value={format.value}
                        checked={formData.report_format === format.value}
                        onChange={handleChange}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500"
                      />
                      <div className="ml-3">
                        <div className="flex items-center">
                          {format.icon}
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {format.name}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {format.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Include Charts */}
            <div className="flex items-center">
              <input
                id="include_charts"
                name="include_charts"
                type="checkbox"
                checked={formData.include_charts}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="include_charts" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Include visualizations and charts (PDF and Excel only)
              </label>
            </div>

            {/* Buttons */}
            <div className="flex space-x-4 pt-4">
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !formData.trend_data_id}
              >
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FaFileAlt className="mr-2" />
                    Generate Report
                  </>
                )}
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={handleExportData}
                disabled={!selectedSearch}
              >
                Export Raw Data
              </button>
            </div>
          </form>

          {/* Selected Search Info */}
          {selectedSearch && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-md">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Selected Search Information
              </h3>
              <div className="text-sm text-gray-700 dark:text-gray-300">
                <p><strong>Name:</strong> {selectedSearch.name}</p>
                <p><strong>Date:</strong> {selectedSearch.date}</p>
                <p><strong>Type:</strong> {selectedSearch.type === 'trend' ? 'Trend Analysis' : 'Niche Comparison'}</p>
                <p><strong>Data Available:</strong></p>
                <ul className="list-disc list-inside ml-4 mt-1">
                  {selectedSearch.data?.videos && (
                    <li>{selectedSearch.data.videos.length} videos</li>
                  )}
                  {selectedSearch.data?.channels && (
                    <li>{selectedSearch.data.channels.length} channels</li>
                  )}
                  {selectedSearch.data?.topics && (
                    <li>{selectedSearch.data.topics.length} topics</li>
                  )}
                  {selectedSearch.data?.ideas && (
                    <li>{selectedSearch.data.ideas.length} content ideas</li>
                  )}
                  {selectedSearch.data?.niches && (
                    <li>{selectedSearch.data.niches.length} niches compared</li>
                  )}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Export Information */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Report & Export Options
          </h2>
          <div className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md border border-blue-100 dark:border-blue-800">
              <h3 className="text-lg font-medium text-blue-900 dark:text-blue-300">
                Available Export Options
              </h3>
              <ul className="list-disc list-inside mt-2 space-y-2 text-blue-800 dark:text-blue-300">
                <li>
                  <strong>PDF:</strong> Complete reports with charts, tables, and insights
                </li>
                <li>
                  <strong>Excel:</strong> Multi-sheet workbook with all data categories
                </li>
                <li>
                  <strong>CSV:</strong> Simple data files for importing into other tools
                </li>
                <li>
                  <strong>Text:</strong> Plain text format for quick viewing
                </li>
              </ul>
              <div className="pt-2">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  <strong>Tip:</strong> Export your data in multiple formats (PDF, Excel, CSV, Text) to analyze it further 
                  in your preferred tools or share with your team.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md mt-6">
          <p>{error}</p>
        </div>
      )}

      {/* Result Message */}
      {result && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 rounded-md mt-6">
          <h3 className="font-bold">Feature Coming Soon</h3>
          <p>
            {result.message || "The advanced report generation feature is planned for the next release. Basic exports are available now."}
          </p>
          <p className="mt-2 text-sm">
            The report generation feature is planned for the next release. Stay tuned!
          </p>
        </div>
      )}

      {/* Available Search Data */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Search Data Available for Export
        </h2>
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Search Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {searchHistory.length > 0 ? (
                  searchHistory.map((search) => (
                    <tr key={search.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {search.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {search.date}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {search.type === 'trend' ? 'Trend Analysis' : 'Niche Comparison'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => setFormData({...formData, trend_data_id: search.id})}
                          className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                        >
                          Select for Export
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-6 py-8 text-center text-gray-500 dark:text-gray-400" colSpan="4">
                      No search data available. Perform some trend analyses or niche comparisons first.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
