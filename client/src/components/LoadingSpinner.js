import React from 'react';
import { FaSpinner } from 'react-icons/fa';

const LoadingSpinner = ({ size = 'md', color = 'primary', fullScreen = false, message = 'Loading...' }) => {
  // Size classes
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  // Color classes
  const colorClasses = {
    primary: 'text-primary-600 dark:text-primary-400',
    secondary: 'text-secondary-600 dark:text-secondary-400',
    white: 'text-white'
  };

  // Determine classes based on props
  const spinnerClasses = `${sizeClasses[size] || sizeClasses.md} ${colorClasses[color] || colorClasses.primary} animate-spin`;

  // If fullScreen, render a full-screen overlay
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 dark:bg-gray-900/80 z-50 flex flex-col items-center justify-center">
        <FaSpinner className={`${sizeClasses.xl} ${colorClasses[color] || colorClasses.primary} animate-spin`} />
        {message && (
          <p className="mt-4 text-gray-700 dark:text-gray-300 font-medium">{message}</p>
        )}
      </div>
    );
  }

  // Otherwise, render inline
  return (
    <div className="flex items-center justify-center">
      <FaSpinner className={spinnerClasses} />
      {message && (
        <span className="ml-2 text-gray-700 dark:text-gray-300">{message}</span>
      )}
    </div>
  );
};

export default LoadingSpinner;
