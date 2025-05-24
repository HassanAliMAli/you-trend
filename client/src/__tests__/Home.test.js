import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom'; // For extended Jest matchers

import HomePage from '../pages/HomePage';
import { ApiContext } from '../contexts/ApiContext'; // HomePage might use this
import { ThemeContext } from '../contexts/ThemeContext'; // Or this

// Mock an ApiContext value if HomePage depends on it directly or indirectly
const mockApiContextValue = {
  apiKey: 'test-key',
  setApiKey: jest.fn(),
  apiQuota: { usage: 100, limit: 10000 },
  setApiQuota: jest.fn(),
  // Add other properties HomePage might expect from ApiContext
};

// Mock ThemeContext if needed
const mockThemeContextValue = {
  theme: 'light',
  toggleTheme: jest.fn(),
};

// Helper function to render HomePage with necessary providers
const renderHomePage = (apiContextValue = mockApiContextValue, themeContextValue = mockThemeContextValue) => {
  return render(
    <ApiContext.Provider value={apiContextValue}>
      <ThemeContext.Provider value={themeContextValue}>
        <HomePage />
      </ThemeContext.Provider>
    </ApiContext.Provider>
  );
};

describe('HomePage', () => {
  test('renders the main heading', () => {
    renderHomePage();
    // PRD.md mentions "Welcome to YouTrend" as a heading on the Home Page
    // TASKS.md 3.3 mentions "input form with ... Submit button"
    // We can look for a general heading or a more specific one if known
    const headingElement = screen.getByRole('heading', { name: /analyze trends/i }); 
    expect(headingElement).toBeInTheDocument();
  });

  test('renders keyword input field', () => {
    renderHomePage();
    const keywordInput = screen.getByPlaceholderText(/enter keyword/i);
    expect(keywordInput).toBeInTheDocument();
  });

  test('renders country dropdown', () => {
    renderHomePage();
    // Assuming the dropdown has a label or a default value that can be queried
    // For example, if there's a label "Country:"
    const countryLabel = screen.getByText(/country/i); 
    expect(countryLabel).toBeInTheDocument();
    // More specific tests can be added if we know the select element's role or test-id
  });

  test('renders niche dropdown', () => {
    renderHomePage();
    const nicheLabel = screen.getByText(/niche/i);
    expect(nicheLabel).toBeInTheDocument();
  });

  test('renders date focus dropdown', () => {
    renderHomePage();
    const dateFocusLabel = screen.getByText(/date focus/i);
    expect(dateFocusLabel).toBeInTheDocument();
  });

  test('renders submit button', () => {
    renderHomePage();
    const submitButton = screen.getByRole('button', { name: /analyze trends/i });
    expect(submitButton).toBeInTheDocument();
  });

  test('keyword input updates on change', () => {
    renderHomePage();
    const keywordInput = screen.getByPlaceholderText(/enter keyword/i);
    fireEvent.change(keywordInput, { target: { value: 'test query' } });
    expect(keywordInput.value).toBe('test query');
  });

  // Placeholder for form submission test
  // This would require mocking the Axios call and ApiContext interactions
  test.skip('form submission calls API (requires mocking)', () => {
    // const mockSetResults = jest.fn(); // If results are set in context or state
    // renderHomePage({ ...mockApiContextValue, setAnalysisResults: mockSetResults });
    
    // const keywordInput = screen.getByPlaceholderText(/enter keyword/i);
    // const submitButton = screen.getByRole('button', { name: /analyze trends/i });

    // fireEvent.change(keywordInput, { target: { value: 'gaming' } });
    // // Simulate other field inputs as necessary

    // fireEvent.click(submitButton);

    // expect(axios.post).toHaveBeenCalledWith('/api/trends', expect.any(Object));
    // await waitFor(() => expect(mockSetResults).toHaveBeenCalled());
  });
}); 