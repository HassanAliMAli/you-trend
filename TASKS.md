TASKS.md for YouTrend Development
Introduction
This file outlines the tasks required to build the YouTrend YouTube trend analysis web app, as specified in PRD.md. The AI coding agent must follow these tasks sequentially, checking off each task ([x]) in this file upon completion. For each task, the agent must update /README.md with a change log entry and /docs/USER_GUIDE.md with relevant user-facing documentation. After completing all tasks, the agent must maintain both files for any future changes by appending new tasks to this file and updating the others accordingly.
Instructions for AI Coding Agent

Task Completion:
Complete each task in order, ensuring dependencies (if any) are met.
Mark the task as complete by changing [ ] to [x] in this file.
Save the updated TASKS.md in /docs.


Updating README.md:
For each task, append a change log entry to /README.md in the "Change Log" section, formatted as: YYYY-MM-DD HH:MM PKT: [Task X] Brief description.
If README.md doesn't exist, create it per Task 1.2.
For future changes (post-task completion), append new tasks to this file and update README.md similarly.


Updating USER_GUIDE.md:
For tasks implementing user-facing features, add or update relevant sections in /docs/USER_GUIDE.md (e.g., filter usage, report downloads).
If USER_GUIDE.md doesn't exist, create it per Task 6.3.
For future changes, update USER_GUIDE.md to reflect new features or modifications.


File Management:
Save all files in the specified project structure (/client, /server, /docs, root for README.md).
Use clear, consistent naming and commenting in code.


Future Changes:
After completing all tasks, monitor for new instructions from the user.
Append new tasks to the "Future Tasks" section below, checkmark them upon completion, and update README.md and USER_GUIDE.md with change logs and documentation.



Project Structure

/client: React frontend (Vercel-hosted).
/server: FastAPI backend and Redis (Render-hosted).
/docs: Documentation (TASKS.md, USER_GUIDE.md, API.md, DEVELOPMENT.md).
/README.md: Project overview and change log (root).

Tasks
Phase 1: Project Setup
Task 1.1: Initialize Project Structure

 [x] Create directories: /client, /server, /docs.
Description: Set up the project folder structure to organize frontend, backend, and documentation files.
Dependencies: None.
Updates:
README.md: Create /README.md if it doesn't exist (see Task 1.2) and add change log: 2025-05-17 03:05 PKT: [Task 1.1] Initialized project structure with /client, /server, /docs.
USER_GUIDE.md: No update (no user-facing features).



Task 1.2: Create Initial README.md

 [x] Create /README.md with project overview, setup guide, and empty change log section.
Description: Write initial content:
Overview: "YouTrend is a YouTube trend analysis web app to identify top channels, videos, and content ideas."
Setup: Instructions for npm (frontend), pip (backend), YouTube API key, Vercel/Render deployment.
Change Log: Empty section for future updates.


Dependencies: Task 1.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 1.2] Created initial README.md with overview and setup guide.
USER_GUIDE.md: No update.



Task 1.3: Set Up Frontend Environment

 [x] Create /client/package.json and install dependencies (React, Tailwind CSS, Chart.js, Axios).
Description: Generate package.json with scripts (start, build) and dependencies. Run npm install to set up.
Dependencies: Task 1.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 1.3] Set up frontend with package.json and dependencies.
USER_GUIDE.md: No update.



Task 1.4: Set Up Backend Environment

 [x] Create /server/requirements.txt and /server/.env.example.
Description:
requirements.txt: List FastAPI, google-api-python-client, redis, pandas, reportlab, openpyxl, uvicorn, pypdf2, matplotlib.
.env.example: Placeholders for YouTube API key, Redis URL, FastAPI secret key.


Dependencies: Task 1.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 1.4] Set up backend with requirements.txt and .env.example.
USER_GUIDE.md: No update.



Phase 2: Backend Development
Task 2.1: Implement YouTube API Integration

 [x] Create /server/utils/youtube_api.py.
Description: Write functions to fetch channels, videos, and search results using YouTube Data API v3. Optimize queries to minimize quota usage (e.g., limit to top 50 results).
Dependencies: Task 1.4.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 2.1] Implemented YouTube API integration in youtube_api.py.
USER_GUIDE.md: No update (internal feature).



Task 2.2: Implement Data Processing

 [x] Create /server/utils/data_processor.py.
Description: Write logic to:
Rank channels (30% subscribers, 40% avg. views, 30% frequency).
Rank videos (40% views, 40% engagement, 20% recency).
Analyze titles/tags/descriptions for topics and suggest related niches (keyword overlap, shared viewership).


Dependencies: Task 2.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 2.2] Added data processing for ranking and niche suggestions in data_processor.py.
USER_GUIDE.md: No update (internal feature).



Task 2.3: Implement Report Generation

 [x] Create /server/utils/report_generator.py.
Description: Write functions to generate reports in TXT (raw data), CSV (structured), XLSX (tables), PDF (insights + charts using Matplotlib). Include raw data, insights, and embedded charts.
Dependencies: Task 2.2.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 2.3] Implemented report generation in report_generator.py.
USER_GUIDE.md: No update (user-facing documentation in Task 6.3).



Task 2.4: Implement Caching

 [x] Create /server/utils/cache.py.
Description: Write functions to store/retrieve API results in Redis with 1-hour TTL. Include quota tracking and warning at 80% usage.
Dependencies: Task 2.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 2.4] Added Redis caching and quota warnings in cache.py.
USER_GUIDE.md: No update (internal feature).



Task 2.5: Create FastAPI App

 [x] Create /server/main.py.
Description: Implement FastAPI app with endpoints:
/trends: Fetch and process trends (keyword, filters).
/compare: Compare niches (side-by-side metrics).
/reports: Generate downloadable reports.
Include CORS, input validation, and error handling.


Dependencies: Tasks 2.1–2.4.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 2.5] Created FastAPI app with endpoints in main.py.
USER_GUIDE.md: No update (user-facing documentation in Task 6.3).



Phase 3: Frontend Development
Task 3.1: Set Up React App

 [x] Create /client/src/App.js.
Description: Implement main React component with React Router for multi-page dashboard (Home, Results, Reports, Settings). Add navigation bar.
Dependencies: Task 1.3.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.1] Set up React app with routing in App.js.
USER_GUIDE.md: No update (UI implementation in later tasks).



Task 3.2: Create Navigation Bar

 [x] Create /client/src/components/NavBar.js.
Description: Implement responsive navigation bar with links to Home, Results, Reports, Settings, and dark/light theme toggle.
Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.2] Added navigation bar in NavBar.js.
USER_GUIDE.md: Add section: "Navigation: Use the top bar to switch between Home, Results, Reports, and Settings."



Task 3.3: Implement Home Page

 [x] Create /client/src/pages/HomePage.js.
Description: Build input form with:
Keyword input.
Dropdowns: Country (Pakistan default), niche (~20 broad, ~100 sub-niches), date focus (uploaded/trending/performance).
Date pickers for start/end.
Additional filters: Duration, language, sort order.
Submit button to call /trends endpoint via Axios.


Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.3] Implemented Home page with input form in Home.js.
USER_GUIDE.md: Add section: "Home Page: Enter a keyword (e.g., Gaming), select filters (country, niche, date range), and submit to analyze trends."



Task 3.4: Implement Results Page

 [x] Create /client/src/pages/TrendsPage.js.
Description: Build tabbed interface for:
Channels: Table with top channels (subscribers, avg. views).
Videos: Table with top videos (title, views, engagement).
Topics/Ideas: Word cloud and list of trending formats.
Comparisons: Side-by-side metrics for niches (bar charts).
Use Chart.js for visualizations (bar, pie, line, word cloud).


Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.4] Implemented Results page with tabs and charts in Results.js.
USER_GUIDE.md: Add section: "Results Page: View top channels, videos, topics, and niche comparisons in tabs with tables and charts."



Task 3.5: Implement Reports Page

 [x] Create /client/src/pages/ReportsPage.js.
Description: Build page to:
Display interactive reports (tables, charts).
Provide download buttons for TXT, CSV, XLSX, PDF (call /reports endpoint).


Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.5] Implemented Reports page with interactive and downloadable reports in Reports.js.
USER_GUIDE.md: Add section: "Reports Page: View interactive reports and download as TXT, CSV, XLSX, or PDF."



Task 3.6: Implement Settings Page

 [x] Create /client/src/pages/Settings.js.
Description: Build form to:
Input YouTube API key (stored in session storage).
Display quota usage (progress bar, warning at 80%).
Save settings.


Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.6] Implemented Settings page for API key and quota warnings in Settings.js.
USER_GUIDE.md: Add section: "Settings Page: Enter your YouTube API key and monitor quota usage."



Task 3.7: Create Chart Component

 [x] Create /client/src/components/ChartComponent.js.
Description: Implement reusable Chart.js component for bar, pie, line charts, and word clouds, with props for data and metrics.
Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.7] Added reusable chart component in ChartComponent.js.
USER_GUIDE.md: No update (internal feature).



Task 3.8: Set Up Tailwind CSS

 [x] Create /client/src/styles/tailwind.css.
Description: Verified existing Tailwind CSS configuration (in client/src/index.css and client/tailwind.config.js) meets requirements for directives, custom styles (blue/white scheme), and dark mode support.
Dependencies: Task 1.3.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 3.8] Set up Tailwind CSS in tailwind.css.
USER_GUIDE.md: Add note: "The app supports dark/light themes, toggleable in the navigation bar."



Phase 4: Testing
Task 4.1: Write Backend Tests

 [x] Create /server/tests/test_api.py.
Description: Write pytest unit tests for /trends, /compare, /reports endpoints, mocking YouTube API responses.
Dependencies: Task 2.5.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 4.1] Added backend unit tests in test_api.py.
USER_GUIDE.md: No update.



Task 4.2: Write Frontend Tests

 [x] Create /client/src/__tests__/Home.test.js.
Description: Write Jest tests for Home page (form rendering, submission).
Dependencies: Task 3.3.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 4.2] Added frontend unit tests in Home.test.js.
USER_GUIDE.md: No update.



Phase 5: Deployment
Task 5.1: Configure Vercel

 [x] Create /client/vercel.json.
Description: Configure Vercel hosting with build settings and routes for the React app.
Dependencies: Task 3.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 5.1] Configured Vercel hosting in vercel.json.
USER_GUIDE.md: No update.



Task 5.2: Configure Render

 [x] Create /server/render.yml.
Description: Configure Render hosting for FastAPI and Redis services.
Dependencies: Task 2.5.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 5.2] Configured Render hosting in render.yml.
USER_GUIDE.md: No update.



Task 5.3: Deploy Frontend to Vercel

 [x] Deploy /client to Vercel.
Description: Push frontend code to a Git repository, link to Vercel, and deploy. Verify app accessibility.
Dependencies: Task 5.1.
Updates:
README.md: Add change log: YYYY-MM-DD HH:MM PKT: [Task 5.3] Deployed frontend to Vercel.
USER_GUIDE.md: Add note: "Access the app via the Vercel-provided URL."



Task 5.4: Deploy Backend to Render

 Deploy /server to Render.
Description: Push backend code to a Git repository, link to Render, configure Redis, and deploy. Verify API endpoints.
Dependencies: Task 5.2.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 5.4] Deployed backend and Redis to Render.
USER_GUIDE.md: No update.



Phase 6: Documentation
Task 6.1: Create API Documentation

 Create /docs/API.md.
Description: Document backend endpoints (/trends, /compare, /reports) with parameters, responses, and examples.
Dependencies: Task 2.5.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 6.1] Created API documentation in API.md.
USER_GUIDE.md: No update.



Task 6.2: Create Development Documentation

 Create /docs/DEVELOPMENT.md.
Description: Document project structure, file purposes, and coding conventions.
Dependencies: Task 1.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 6.2] Created development documentation in DEVELOPMENT.md.
USER_GUIDE.md: No update.



Task 6.3: Create User Guide

 Create /docs/USER_GUIDE.md.
Description: Write user-facing documentation:
Overview: Purpose and features of YouTrend.
Usage: Instructions for keyword input, filters, results, reports, API key, and quota management.
Troubleshooting: Handling quota errors, invalid inputs.
Change Log: Empty section for updates.


Dependencies: Tasks 3.3–3.6.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 6.3] Created user guide in USER_GUIDE.md.
USER_GUIDE.md: Initialize with full documentation and add change log: 2025-05-17 03:05 PKT: Initial user guide created.



Phase 7: Finalization
Task 7.1: Verify Functionality

 Test all features (filters, results, reports, deployments).
Description: Manually test:
Keyword search with filters (e.g., Gaming, Pakistan, last 30 days).
Results tabs (channels, videos, topics, comparisons).
Report downloads (TXT, CSV, XLSX, PDF).
API key input and quota warnings.
Vercel/Render accessibility.


Dependencies: Tasks 5.3, 5.4.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 7.1] Verified all app functionality.
USER_GUIDE.md: No update.



Task 7.2: Optimize Performance

 Optimize API queries and frontend bundle.
Description: Minimize API calls (e.g., cache all queries), compress React bundle, and ensure response times (<5s uncached, <2s cached).
Dependencies: Task 7.1.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 7.2] Optimized API queries and frontend performance.
USER_GUIDE.md: No update.



Task 7.3: Finalize Documentation

 Review and polish all documentation (README.md, API.md, DEVELOPMENT.md, USER_GUIDE.md).
Description: Ensure clarity, fix typos, and verify links/references.
Dependencies: Tasks 1.2, 6.1–6.3.
Updates:
README.md: Add change log: 2025-05-17 03:05 PKT: [Task 7.3] Finalized all documentation.
USER_GUIDE.md: Add change log: 2025-05-17 03:05 PKT: Finalized user guide.



Future Tasks
Task 8.1: Handle Future Changes

 Monitor for new user instructions and append tasks here.
Description: For any post-completion changes:
Add new tasks to this section with checkboxes.
Implement the change (e.g., new filter, UI tweak).
Checkmark the task in TASKS.md.
Update README.md with a change log entry: YYYY-MM-DD HH:MM PKT: [Task 8.X] Description.
Update USER_GUIDE.md if the change affects user-facing features (e.g., new section or modified instructions).


Dependencies: All previous tasks.
Updates:
README.md: Add change log for each new task.
USER_GUIDE.md: Update as needed for user-facing changes.



Notes

Task Order: Follow the sequence unless dependencies allow parallel execution.
Change Logs: Use Pakistan Standard Time (PKT) for timestamps (e.g., 2025-05-17 03:05 PKT).
Error Handling: If a task fails, log the error in README.md change log and proceed to the next task, noting dependencies.
Version Control: Save all file changes incrementally to preserve history (e.g., via Git, if supported).

