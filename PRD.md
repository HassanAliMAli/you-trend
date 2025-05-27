Product Requirements Document (PRD) for YouTrend
1. Overview
1.1 Project Name
YouTrend
1.2 Purpose
YouTrend is a standalone web application designed to analyze YouTube trends for any niche (e.g., Gaming, News) to help content creators identify high-performing channels, videos, topics, and actionable video ideas to maximize views. The app uses the YouTube Data API to fetch and process data, offering filters (country, niche, date range), niche comparisons, interactive reports, and exportable visualizations. It aims to provide accurate, real-time trend insights with a secure, lightweight, and fast multi-page dashboard.
1.3 Target Audience

YouTube content creators seeking trending niches and video ideas.
Marketers and analysts researching YouTube performance metrics.
Users in Pakistan (default region) and globally, with English as the UI language.

1.4 Goals

Enable users to analyze YouTube trends by keyword, country, niche, and date range.
Identify top-performing channels, videos, and topics using weighted metrics (views, engagement, etc.).
Suggest related niches and actionable video ideas (e.g., formats, titles, thumbnails).
Provide interactive reports and downloadable files (TXT, CSV, XLSX, PDF) with raw data, insights, and charts.
Ensure a secure, fast, and lightweight app hosted on free-tier services (Vercel/Render).
Optimize YouTube API usage with caching and quota warnings.

2. Functional Requirements
2.1 Core Features
2.1.1 Trend Analysis

Description: Analyze YouTube data for a given keyword (e.g., “Gaming,” “News”) to identify top channels, videos, and topics.
Details:
Channels: Rank by weighted score (30% subscriber count, 40% average video views, 30% posting frequency).
Videos: Rank by weighted score (40% views, 40% engagement rate [likes + comments / views], 20% recency).
Topics/Ideas: Analyze patterns in titles, tags, and descriptions to identify trending formats (e.g., “Fortnite challenges”), ranked by views and engagement.
Related Niches: Suggest niches based on keyword overlap (e.g., “Gaming” → “Esports”) and shared viewership (channels popular in both).



2.1.2 Filters

Description: Allow users to refine trend analysis with multiple filters.
Details:
Country: Dropdown with Pakistan as default, global option, and major countries (e.g., US, UK, India).
Niche: Dropdown with ~20 broad niches (e.g., Gaming, News, Fitness, Vlogs, Education, Tech, Music, Cooking, Travel) and ~100 sub-niches (e.g., FPS Gaming, Political News), sourced from YouTube categories and keyword analysis.
Date Range: Specific start/end dates via date pickers, with a dropdown for focus:
Videos uploaded in the date range.
Videos trending (most viewed) in the date range.
Performance (views/engagement gained) in the date range.


Additional Filters:
Video Duration: Short (<4 min), Medium (4–20 min), Long (>20 min).
Language: Auto-detected (e.g., English, Urdu, Hindi).
Sort Order: By views, engagement, or recency.





2.1.3 Niche Comparison

Description: Compare trends across multiple niches or analyze a single niche.
Details:
Side-by-side metrics for selected niches (e.g., Gaming vs. News: top channels, video views, topic popularity).
Visualizations (e.g., bar charts comparing views).
Option to disable comparison for single-niche analysis.



2.1.4 Actionable Insights

Description: Provide specific video ideas and strategies to maximize views.
Details:
Recommendations (e.g., “Create a 3–5 min Fortnite montage with clickbait thumbnails like ‘INSANE KILLS!’”).
Include estimated view potential (e.g., “High views, medium competition”) and tips for titles, thumbnails, and formats.
Based on analysis of top-performing videos’ titles, tags, and descriptions.



2.1.5 Reports and Visualizations

Description: Offer interactive and downloadable reports with trend data and insights.
Details:
Interactive Reports: Viewable in the app with dynamic tables and charts (updated per user request).
Downloadable Reports: Export in TXT (raw data), CSV (structured data), XLSX (formatted tables), and PDF (insights with charts).
Report Contents:
Raw data: Top channel/video details (e.g., titles, views, subscribers).
Summarized insights: Trends (e.g., “Short-form Gaming videos dominate”).
Charts: Embedded visualizations (e.g., bar charts for top videos).


Visualizations:
Bar charts: Top channels/videos by views or engagement.
Pie charts: Niche/topic popularity (e.g., % of Gaming videos that are FPS).
Line graphs: View/engagement trends over time.
Word clouds: Trending keywords in titles/tags.





2.1.6 Data Updates

Description: Fetch fresh YouTube data per user request, with optimizations.
Details:
Use Redis caching (1-hour TTL) to reduce YouTube API quota usage.
Warn users when nearing quota limit (80% of 10,000 units/day).
Display loading indicators during API requests.



2.2 User Interface (UI)

Type: Multi-page dashboard for usability and developer simplicity.
Pages:
Home: Input keyword, select filters (country, niche, date range, etc.), and submit query.
Results: Tabs for Channels, Videos, Topics/Ideas, and Comparisons, with tables, charts, and insights.
Reports: View interactive reports and download as TXT, CSV, XLSX, or PDF.
Settings: Input YouTube API key and configure preferences (e.g., cache duration).


Design:
Responsive layout with Tailwind CSS.
Dark/light theme toggle.
Blue/white color scheme (customizable via CSS).
Intuitive navigation bar linking all pages.
Loading indicators and error messages for API failures.


Accessibility:
Keyboard-navigable forms and tables.
High-contrast visuals for readability.



2.3 User Experience (UX)

Ease of Use: Simple input form with dropdowns and date pickers, clear results tabs, and one-click report downloads.
Feedback: Quota warnings, success/error messages, and progress bars for long-running queries.
Onboarding: Settings page guides users to input API key, with tooltips explaining filters.

3. Technical Requirements
3.1 Tech Stack

Frontend:
React: For dynamic, responsive UI.
Tailwind CSS: For styling.
Chart.js: For visualizations (bar, pie, line charts, word clouds).
Axios: For API requests.


Backend:
FastAPI: Lightweight, high-performance API.
google-api-python-client: For YouTube Data API integration.
Pandas: For data processing and analysis.
ReportLab: For PDF reports.
OpenPyXL: For XLSX reports.
python-pptx: For PPT reports (optional, excluded due to complexity).
Redis: For caching (1-hour TTL).
Uvicorn: For running FastAPI.


Hosting:
Vercel: Free tier for frontend (React app).
Render: Free tier for backend (FastAPI) and Redis.
Fallback: Heroku Eco tier ($5/month) if Render limits are exceeded.


Other:
PyPDF2: For PDF generation.
Matplotlib: For chart embedding in reports.



3.2 APIs

YouTube Data API v3:
Used for fetching channels, videos, and search results.
User-provided API key (input via Settings page).
Quota: 10,000 units/day, optimized with caching and query limits.
Endpoints: Search, Channels, Videos.



3.3 Security

API Key: Stored client-side (session storage) or encrypted in backend sessions.
Input Validation: Sanitize keyword and filter inputs to prevent injection attacks.
HTTPS: Enforced for all API and hosting services.
CORS: Configured to allow only frontend-backend communication.

3.4 Performance

Caching: Redis stores API results for 1 hour to reduce quota usage.
Query Optimization: Limit API calls (e.g., fetch top 50 results per query).
Lightweight Design: Minimize frontend bundle size (React) and backend resources (FastAPI).
Response Time: Target <2 seconds for most queries (cached) and <5 seconds for uncached.

3.5 Scalability

Free-Tier Limits: Vercel/Render support low-to-moderate traffic; monitor usage to avoid throttling.
Quota Management: Warn users at 80% quota usage; allow manual cache clearing.
Extensibility: Modular code (e.g., separate utils for API, processing) for adding features (e.g., new filters).

4. Non-Functional Requirements
4.1 Reliability

Graceful error handling for API failures (e.g., quota exceeded, invalid key).
Fallback to cached data if API requests fail.
Unit tests for critical backend (API endpoints) and frontend (form rendering).

4.2 Maintainability

Modular project structure: /client (frontend), /server (backend), /docs (documentation).
Clear comments in code and detailed documentation (README, API, DEVELOPMENT).
Environment variables for configuration (e.g., API key, Redis URL).

4.3 Usability

Intuitive UI with minimal learning curve.
Tooltips for complex filters (e.g., date range focus).
Responsive design for desktop and mobile.

5. Deliverables

Source Code:

Frontend (/client):
package.json: Dependencies and scripts.
src/App.js: Main app with routing.
src/pages/Home.js: Input form and filters.
src/pages/Results.js: Results tabs with tables/charts.
src/pages/Reports.js: Interactive reports and downloads.
src/pages/Settings.js: API key input and quota warnings.
src/components/NavBar.js: Navigation bar.
src/components/ChartComponent.js: Reusable chart component.
src/styles/tailwind.css: Styling.
vercel.json: Vercel config.


Backend (/server):
requirements.txt: Python dependencies.
main.py: FastAPI app with endpoints.
utils/youtube_api.py: YouTube API functions.
utils/data_processor.py: Data analysis and insights.
utils/report_generator.py: Report exports.
utils/cache.py: Redis caching.
.env.example: Environment variable template.




Documentation:

docs/README.md: Project overview and setup guide.
docs/API.md: Backend API endpoint details.
docs/DEVELOPMENT.md: Project structure and workflow.


Configuration:

server/render.yml: Render hosting config.


Optional:

server/tests/test_api.py: Backend unit tests.
client/src/__tests__/Home.test.js: Frontend unit tests.
docker-compose.yml: Local development setup.
Makefile: Task automation.


Setup Guide:

Instructions for:
Installing dependencies (npm, pip).
Configuring YouTube API key.
Deploying to Vercel (frontend) and Render (backend/Redis).
Running locally for testing.


Included in docs/README.md.


Format:

Delivered as a ZIP file structure in an <xaiArtifact> tag.
Clear file hierarchy (/client, /server, /docs) for AI coding agent.



6. Constraints and Assumptions
6.1 Constraints

YouTube API Quota: 10,000 units/day limits broad queries. Mitigated by 1-hour Redis caching and optimized queries.
Free-Tier Hosting: Vercel/Render free tiers may throttle under high traffic. Monitor usage and consider Heroku Eco ($5/month) if needed.
Data Accuracy: Limited to public YouTube data (titles, tags, views, etc.). Real-time trends may reflect data from the past few days.
Export Complexity: PDF reports with charts are resource-intensive. Use lightweight libraries (ReportLab, Matplotlib).
Language: English-only UI, as specified.

6.2 Assumptions

User provides a valid YouTube API key via the Settings page.
Traffic remains within Vercel/Render free-tier limits (low-to-moderate usage).
AI coding agent can process modular code with clear comments and documentation.
Niche list (~20 broad, ~100 sub-niches) is sufficient for “almost all niches,” supplemented by dynamic keyword analysis.
1-hour cache TTL balances freshness and quota efficiency.

7. Success Criteria

Functionality: App accurately identifies top channels, videos, and topics for any keyword, with functional filters and comparisons.
Usability: Users can input keywords, apply filters, view results, and download reports in <5 minutes.
Performance: Most queries respond in <5 seconds (cached: <2 seconds).
Actionable Insights: Suggestions (e.g., video formats, titles) align with high-performing trends, helping users plan content.
Reliability: App handles API errors gracefully and maintains uptime on Vercel/Render.
Quota Management: Users receive warnings at 80% quota usage, and caching prevents exhaustion.

8. Timeline (For AI Coding Agent)

Backend: 2–3 days (API integration, data processing, reports).
Frontend: 2–3 days (dashboard, charts, UI).
Testing/Optimization: 1–2 days (error handling, quota management).
Documentation/Setup: 1 day.
Total: ~7–10 days, assuming efficient AI agent execution.

9. Future Enhancements

Support for additional platforms (e.g., X posts for trend validation).
Multi-language UI (e.g., Urdu for Pakistan users).
Advanced filters (e.g., video resolution, monetization status).
User authentication to save preferences or API keys.
Real-time trend alerts via email or notifications.

10. References

YouTube Data API v3: https://developers.google.com/youtube/v3
Vercel Documentation: https://vercel.com/docs
Render Documentation: https://render.com/docs
FastAPI Documentation: https://fastapi.tiangolo.com
React Documentation: https://reactjs.org


Approval: This PRD is designed to meet all specified requirements for YouTrend. Please confirm to proceed with implementation.
