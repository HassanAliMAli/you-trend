import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import { WordCloudController, WordElement } from 'chartjs-chart-wordcloud';

// Register Chart.js components and controllers, including WordCloud
Chart.register(...registerables, WordCloudController, WordElement);

const ChartComponent = ({ type, data, options, chartId }) => {
  const chartRef = useRef(null); // Ref for the canvas element
  const chartInstance = useRef(null); // Ref for the chart instance

  useEffect(() => {
    // Destroy existing chart instance before creating a new one
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Create new chart instance if canvas ref and data are available
    if (chartRef.current && data) {
      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {
        type: type, // e.g., 'bar', 'pie', 'line', 'wordCloud'
        data: data, // Chart.js data object
        options: options, // Chart.js options object
      });
    }

    // Cleanup: Destroy chart instance when component unmounts or dependencies change
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null; // Ensure it's cleaned up for next render
      }
    };
  }, [type, data, options]); // Re-create chart if type, data, or options change

  // Generate a unique ID for the canvas if not provided, to avoid conflicts
  const canvasId = chartId || `chart-${Math.random().toString(36).substr(2, 9)}`;

  return <canvas ref={chartRef} id={canvasId} aria-label={`${type} chart`}></canvas>;
};

export default ChartComponent;
