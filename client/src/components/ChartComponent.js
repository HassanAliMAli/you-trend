import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

// Default styling options
const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: 'rgba(107, 114, 128, 1)', // text-gray-500
        font: {
          size: 12,
        },
      },
    },
    title: {
      display: true,
      text: 'Chart Title',
      color: 'rgba(17, 24, 39, 1)', // text-gray-900
      font: {
        size: 16,
        weight: 'bold',
      },
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
};

/**
 * A flexible chart component supporting Bar, Pie, and Line charts
 * @param {Object} props Component props
 * @param {string} props.type - Chart type: 'bar', 'pie', or 'line'
 * @param {Object} props.data - Data for the chart
 * @param {Object} props.options - Chart options (merged with defaults)
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 300)
 */
const ChartComponent = ({ type = 'bar', data, options = {}, title = 'Chart', height = 300 }) => {
  // Merge with default options
  const chartOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...options.plugins,
      title: {
        ...defaultOptions.plugins.title,
        ...(options.plugins?.title || {}),
        text: title,
      },
    },
  };

  const chartStyle = {
    height: `${height}px`,
    width: '100%',
  };

  // Render different chart types based on the type prop
  const renderChart = () => {
    switch (type.toLowerCase()) {
      case 'bar':
        return <Bar data={data} options={chartOptions} />;
      case 'pie':
        return <Pie data={data} options={chartOptions} />;
      case 'line':
        return <Line data={data} options={chartOptions} />;
      default:
        return <Bar data={data} options={chartOptions} />;
    }
  };

  return (
    <div className="chart-container" style={chartStyle}>
      {renderChart()}
    </div>
  );
};

export default ChartComponent;
