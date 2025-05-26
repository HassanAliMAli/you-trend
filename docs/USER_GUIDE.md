# YouTrend User Guide

Welcome to YouTrend! This guide will help you understand and use the YouTrend application to analyze YouTube trends, find niche ideas, and generate reports.

## Table of Contents

1.  [Overview](#overview)
2.  [Getting Started](#getting-started)
    *   [Accessing the Application](#accessing-the-application)
    *   [Navigation](#navigation)
3.  [Core Features](#core-features)
    *   [Home Page: Analyzing Trends](#home-page-analyzing-trends)
        *   [Keyword Input](#keyword-input)
        *   [Filters](#filters)
    *   [Results Page: Understanding the Data](#results-page-understanding-the-data)
        *   [Top Channels Tab](#top-channels-tab)
        *   [Top Videos Tab](#top-videos-tab)
        *   [Topics/Ideas Tab](#topicsideas-tab)
        *   [Comparisons Tab](#comparisons-tab)
    *   [Reports Page: Downloading Your Analysis](#reports-page-downloading-your-analysis)
    *   [Settings Page: Configuration](#settings-page-configuration)
        *   [YouTube API Key](#youtube-api-key)
        *   [Quota Usage](#quota-usage)
4.  [Troubleshooting](#troubleshooting)
    *   [Quota Errors](#quota-errors)
    *   [Invalid Inputs](#invalid-inputs)
    *   [No Results Found](#no-results-found)
5.  [Change Log](#change-log)

---

## 1. Overview

YouTrend is a web application designed for content creators, marketers, and anyone interested in understanding YouTube trends. It allows you to:

*   Analyze trends based on keywords, countries, niches, and specific date ranges.
*   Identify top-performing channels and videos with a weighted scoring system.
*   Discover trending topics and get suggestions for content ideas and related niches.
*   Compare the performance of different niches.
*   Generate and download comprehensive reports in various formats (TXT, CSV, XLSX, PDF).

---

## 2. Getting Started

### Accessing the Application

Once deployed, you can access YouTrend via the URL provided by Heroku (e.g., `https://your-app-name.herokuapp.com`).

### Navigation

The application features a responsive navigation bar at the top of the page with the following links:

*   **Home:** The main page for inputting your search criteria and starting an analysis.
*   **Results:** Displays the analysis results in various tabs (channels, videos, topics, comparisons).
*   **Reports:** Allows you to view and download generated reports.
*   **Settings:** Configure your YouTube API key and monitor API quota usage.
*   **Theme Toggle:** A switch (often represented by a sun/moon icon) to toggle between light and dark themes for the application interface.

---

## 3. Core Features

### Home Page: Analyzing Trends

The Home page is your starting point for trend analysis.

#### Keyword Input

*   **Keyword:** Enter the primary keyword or topic you want to analyze (e.g., "sustainable living", "gaming tutorials", "AI in healthcare"). This is a required field.

#### Filters

Refine your search using the following filters:

*   **Country:** Select the country for which you want to see trends. Defaults to Pakistan (PK). *Available countries depend on YouTube API support.*
*   **Niche:** Choose a broad niche (e.g., Technology, Beauty, Education) and optionally a sub-niche to narrow down your search. *The list of niches is predefined within the application.*
*   **Date Focus:**
    *   `Uploaded`: Focus on videos based on their upload date.
    *   `Trending`: Focus on currently trending videos (as determined by YouTube's algorithms).
    *   `Performance`: Focus on overall video performance over time.
*   **Date Range (Start/End Date):** Specify a period for the analysis. Leave blank to use default ranges or if not applicable to the selected `Date Focus`.
*   **Duration:** Filter videos by length:
    *   `Any`: Include videos of all durations.
    *   `Short`: Videos under 4 minutes.
    *   `Medium`: Videos between 4 and 20 minutes.
    *   `Long`: Videos over 20 minutes.
*   **Language:** Filter videos by their primary language (using ISO 639-1 codes, e.g., `en` for English, `es` for Spanish).
*   **Sort Order:** Determine how results from the YouTube API are initially sorted (e.g., by relevance, view count, date). This influences the raw data fetched before YouTrend applies its own ranking.

Click the **"Analyze Trends"** (or similar) button to submit your query. The application will then fetch data from the YouTube API, process it, and display the results on the Results page.

### Results Page: Understanding the Data

The Results page presents the findings of your analysis in a tabbed interface, often using tables and charts for visualization.

#### Top Channels Tab

*   Displays a table of top-performing channels related to your query.
*   Metrics include: Channel Title, Subscriber Count, Average Views per Video, Upload Frequency, and a YouTrend Weighted Score.
*   You can usually sort the table by clicking on column headers.

#### Top Videos Tab

*   Shows a table of top-performing videos.
*   Metrics include: Video Title, Channel Title, View Count, Engagement (likes, comments), Recency, and a YouTrend Weighted Score.
*   Sortable by column headers.

#### Topics/Ideas Tab

*   **Word Cloud:** A visual representation of frequently occurring keywords and topics in the titles, descriptions, and tags of analyzed videos.
*   **Trending Formats/Ideas:** A list of suggested video ideas, content formats, or related niches based on the analysis.

#### Comparisons Tab

*   If you initiated a niche comparison (either from the Home page or a dedicated comparison feature), this tab will show side-by-side metrics for the selected niches.
*   Often uses bar charts or tables to visualize differences in average views, engagement, top channel counts, etc.

Visualizations (charts) are interactive. You can often hover over chart elements to see detailed values.

### Reports Page: Downloading Your Analysis

This page allows you to generate and download detailed reports of your trend analysis.

*   **Interactive View:** Some reports might be viewable directly on the page with interactive tables and charts.
*   **Download Options:** You can typically download reports in the following formats:
    *   **TXT:** Raw data dump.
    *   **CSV:** Comma-Separated Values, suitable for spreadsheets.
    *   **XLSX:** Microsoft Excel format, with structured tables and potentially embedded charts.
    *   **PDF:** Portable Document Format, often including insights, summaries, and charts.

To generate a report, you might need to select the report type and confirm the data set (e.g., from your most recent analysis on the Results page).

### Settings Page: Configuration

Manage application settings here.

#### YouTube API Key

*   **Input API Key:** You need to provide your own YouTube Data API v3 key for the application to fetch data.
*   Enter your key in the provided field and save it. The key is typically stored in your browser's session storage for security and convenience during your session.
*   *Refer to the `README.md` or `docs/DEVELOPMENT.md` for instructions on obtaining a YouTube API key.*

#### Quota Usage

*   The YouTube Data API has daily usage quotas (typically 10,000 units for new projects).
*   This section displays your current quota usage:
    *   **Progress Bar:** Visual representation of used quota.
    *   **Warning:** A warning message will appear if your usage approaches the limit (e.g., at 80%).
*   Monitoring your quota is important to avoid interruptions in service.

Click **"Save Settings"** to apply any changes.

---

## 4. Troubleshooting

### Quota Errors

*   **Symptom:** Application stops fetching new data, or you see an error message related to API limits.
*   **Cause:** You have exceeded your daily YouTube Data API quota.
*   **Solution:**
    1.  Check your quota usage on the Settings page or in your Google Cloud Console.
    2.  Wait for the quota to reset (usually daily).
    3.  If you consistently hit the limit, you might need to request a quota increase from Google or optimize your search queries to be less frequent or less demanding.

### Invalid Inputs

*   **Symptom:** Error messages upon submitting a form on the Home page or Settings page.
*   **Cause:** You may have entered data in an incorrect format (e.g., invalid date, non-numeric value where expected) or missed a required field.
*   **Solution:** Review the input fields, check for any specific formatting requirements (like `YYYY-MM-DD` for dates), and ensure all required fields are filled.

### No Results Found

*   **Symptom:** The Results page is empty or shows a "no results" message after a search.
*   **Cause:**
    *   Your search query (keyword + filters) might be too specific or target a very new/obscure topic with limited content on YouTube.
    *   There might be a temporary issue with the YouTube API.
    *   Ensure your API key is correctly entered and active.
*   **Solution:**
    1.  Try broadening your search criteria (e.g., use a more general keyword, remove some filters, expand the date range).
    2.  Verify your API key in Settings.
    3.  Check the API status endpoint (if available, see `docs/API.md`) or try again later.

---

## 5. Change Log

*(This section will be updated by the development team as new features or significant changes are made to the application.)*

- YYYY-MM-DD HH:MM PKT: Initial user guide created.

---

If you encounter issues not covered here, please refer to other documentation or contact the development team if applicable. 