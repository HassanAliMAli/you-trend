import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaYoutube, FaChartLine, FaExchangeAlt, FaFileAlt, FaMoon, FaSun, FaBars, FaTimes } from 'react-icons/fa';
import { useTheme } from '../contexts/ThemeContext';
import { useApi } from '../contexts/ApiContext';

const Navbar = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { quotaUsage } = useApi();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // Navigation links
  const navLinks = [
    { path: '/', name: 'Home', icon: <FaYoutube className="mr-1" /> },
    { path: '/trends', name: 'Trends', icon: <FaChartLine className="mr-1" /> },
    { path: '/compare', name: 'Compare', icon: <FaExchangeAlt className="mr-1" /> },
    { path: '/reports', name: 'Reports', icon: <FaFileAlt className="mr-1" /> },
  ];

  return (
    <nav className="bg-white dark:bg-secondary-800 shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between h-16">
          {/* Logo and brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <FaYoutube className="h-8 w-8 text-red-600" />
              <span className="ml-2 text-2xl font-bold text-primary-600 dark:text-primary-400">YouTrend</span>
            </Link>
          </div>

          {/* Desktop menu */}
          <div className="hidden md:flex items-center space-x-4">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-300 ${
                  location.pathname === link.path
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-secondary-700'
                }`}
              >
                {link.icon}
                {link.name}
              </Link>
            ))}

            {/* Quota usage indicator */}
            {quotaUsage && (
              <div className="ml-4 text-sm">
                <div className="flex items-center">
                  <span className="mr-2 text-gray-600 dark:text-gray-300">API Quota:</span>
                  <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        quotaUsage.percentage > 80 ? 'bg-red-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${quotaUsage.percentage}%` }}
                    ></div>
                  </div>
                  <span className="ml-2 text-gray-600 dark:text-gray-300">
                    {Math.round(quotaUsage.percentage)}%
                  </span>
                </div>
              </div>
            )}

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="ml-4 p-2 rounded-full bg-gray-100 dark:bg-secondary-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-secondary-600 transition-colors duration-300"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <FaSun className="h-5 w-5" /> : <FaMoon className="h-5 w-5" />}
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMenu}
              className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-secondary-700 focus:outline-none"
              aria-expanded={isMenuOpen}
            >
              {isMenuOpen ? (
                <FaTimes className="h-6 w-6" />
              ) : (
                <FaBars className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden pb-3 pt-2 px-4">
          <div className="space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center px-3 py-2 rounded-md text-base font-medium ${
                  location.pathname === link.path
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-secondary-700'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                {link.icon}
                {link.name}
              </Link>
            ))}

            {/* Theme toggle in mobile menu */}
            <button
              onClick={toggleTheme}
              className="flex items-center w-full px-3 py-2 rounded-md text-base font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-secondary-700"
            >
              {theme === 'dark' ? (
                <>
                  <FaSun className="mr-1" /> Light Mode
                </>
              ) : (
                <>
                  <FaMoon className="mr-1" /> Dark Mode
                </>
              )}
            </button>

            {/* Quota usage in mobile menu */}
            {quotaUsage && (
              <div className="px-3 py-2 text-sm">
                <div className="flex items-center">
                  <span className="mr-2 text-gray-600 dark:text-gray-300">API Quota:</span>
                  <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        quotaUsage.percentage > 80 ? 'bg-red-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${quotaUsage.percentage}%` }}
                    ></div>
                  </div>
                  <span className="ml-2 text-gray-600 dark:text-gray-300">
                    {Math.round(quotaUsage.percentage)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
