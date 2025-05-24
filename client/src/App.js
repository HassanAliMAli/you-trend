import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import TrendsPage from './pages/TrendsPage';
import ComparePage from './pages/ComparePage';
import ReportsPage from './pages/ReportsPage';
import { ApiProvider } from './contexts/ApiContext';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <ApiProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            <Navbar />
            <main className="flex-grow container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/trends" element={<TrendsPage />} />
                <Route path="/compare" element={<ComparePage />} />
                <Route path="/reports" element={<ReportsPage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </ApiProvider>
    </ThemeProvider>
  );
}

export default App;
