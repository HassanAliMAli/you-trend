import React from 'react';
import { FaGithub, FaTwitter, FaYoutube } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white dark:bg-secondary-800 shadow-inner pt-8 pb-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap text-left lg:text-left">
          <div className="w-full lg:w-6/12 px-4">
            <h4 className="text-2xl font-semibold text-gray-700 dark:text-gray-300">YouTrend</h4>
            <h5 className="text-lg mt-0 mb-2 text-gray-600 dark:text-gray-400">
              YouTube trend analysis for content creators
            </h5>
            <div className="mt-6 lg:mb-0 mb-6 flex">
              <button
                className="bg-white text-blue-400 shadow-lg font-normal h-10 w-10 flex items-center justify-center align-center rounded-full outline-none focus:outline-none mr-2"
                type="button"
              >
                <FaTwitter />
              </button>
              <button
                className="bg-white text-red-600 shadow-lg font-normal h-10 w-10 flex items-center justify-center align-center rounded-full outline-none focus:outline-none mr-2"
                type="button"
              >
                <FaYoutube />
              </button>
              <button
                className="bg-white text-gray-900 shadow-lg font-normal h-10 w-10 flex items-center justify-center align-center rounded-full outline-none focus:outline-none mr-2"
                type="button"
              >
                <FaGithub />
              </button>
            </div>
          </div>
          <div className="w-full lg:w-6/12 px-4">
            <div className="flex flex-wrap items-top mb-6">
              <div className="w-full lg:w-4/12 px-4 ml-auto">
                <span className="block uppercase text-gray-700 dark:text-gray-300 text-sm font-semibold mb-2">
                  Useful Links
                </span>
                <ul className="list-unstyled">
                  <li>
                    <a
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm"
                      href="https://developers.google.com/youtube/v3"
                      target="_blank"
                      rel="noreferrer"
                    >
                      YouTube API
                    </a>
                  </li>
                  <li>
                    <a
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm"
                      href="https://fastapi.tiangolo.com/"
                      target="_blank"
                      rel="noreferrer"
                    >
                      FastAPI
                    </a>
                  </li>
                  <li>
                    <a
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm"
                      href="https://react.dev/"
                      target="_blank"
                      rel="noreferrer"
                    >
                      React
                    </a>
                  </li>
                </ul>
              </div>
              <div className="w-full lg:w-4/12 px-4">
                <span className="block uppercase text-gray-700 dark:text-gray-300 text-sm font-semibold mb-2">
                  Other Resources
                </span>
                <ul className="list-unstyled">
                  <li>
                    <button
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm text-left"
                      onClick={() => alert('Terms & Conditions will be available soon.')}
                    >
                      Terms & Conditions
                    </button>
                  </li>
                  <li>
                    <button
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm text-left"
                      onClick={() => alert('Privacy Policy will be available soon.')}
                    >
                      Privacy Policy
                    </button>
                  </li>
                  <li>
                    <button
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-semibold block pb-2 text-sm text-left"
                      onClick={() => alert('Contact form will be available soon.')}
                    >
                      Contact Us
                    </button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <hr className="my-6 border-gray-300 dark:border-gray-700" />
        <div className="flex flex-wrap items-center md:justify-between justify-center">
          <div className="w-full md:w-4/12 px-4 mx-auto text-center">
            <div className="text-sm text-gray-500 dark:text-gray-400 py-1">
              Copyright © {currentYear} YouTrend. All rights reserved.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
