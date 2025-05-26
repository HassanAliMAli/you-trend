# YouTrend

YouTrend is a YouTube trend analysis web app designed to identify top channels, videos, and content ideas. It helps content creators discover trending niches and optimize their YouTube strategy with data-driven insights.

## Overview

This application provides the following features:
- Analyze YouTube trends by keyword, country, niche, and date range
- Identify top-performing channels, videos, and topics using weighted metrics
- Suggest related niches and actionable video ideas
- Generate interactive reports and downloadable files (TXT, CSV, XLSX, PDF)
- Secure and lightweight app with optimized YouTube API usage

## API Endpoints

- `/api/trends` - For analyzing YouTube trends (search and analyze trending videos and channels)
- `/api/compare` - For comparing different niches and their metrics
- `/api/reports` - Generate and download analysis reports
- `/api/status` - For checking API status

## Setup

### Frontend (React)
```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Backend (FastAPI)
```bash
# Navigate to server directory
cd server

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env and add your YouTube API key

# Start development server
uvicorn main:app --reload
```

### YouTube API Key
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create API credentials
5. Add the API key to your `.env` file in the `server` directory and configure it as a Heroku config var.

### Deployment
- The entire application (React frontend and FastAPI backend) is deployed to Heroku.
- The FastAPI backend serves the built static files of the React frontend.
- Requires Heroku CLI and Git.
- Ensure you have a `Procfile` at the root of your project and a `.buildpacks` file specifying Node.js and Python buildpacks.
- Redis is used for caching and should be configured as a Heroku add-on (e.g., Heroku Redis).

```bash
# Build the frontend (if not done automatically by Heroku buildpack)
cd client
npm install
npm run build
cd ..

# Heroku Deployment Steps (general outline)
# 1. Login to Heroku
heroku login

# 2. Create a new Heroku app (or use an existing one)
heroku create your-app-name

# 3. Set necessary Heroku config vars (e.g., YOUTUBE_API_KEY, REDIS_URL, FASTAPI_SECRET_KEY)
heroku config:set YOUTUBE_API_KEY="your_key"
heroku config:set REDIS_URL="your_redis_url_from_addon"
# ... other vars

# 4. Add Heroku buildpacks (if .buildpacks file is not used or needs override)
heroku buildpacks:add heroku/nodejs --index 1
heroku buildpacks:add heroku/python --index 2

# 5. Push your code to Heroku
git push heroku main # or your default branch

# 6. Open your app
heroku open
```

## Change Log

- 2024-07-27 HH:MM PKT: Switched to unified Heroku deployment for frontend and backend.
- 2024-07-27 HH:MM PKT: Switched backend deployment from Render to Heroku (superseded by unified deployment).
- 2025-05-22 05:10 PKT: [Task 1.1] Initialized project structure with /client, /server, /docs
- 2025-05-22 05:12 PKT: [Task 1.2] Created initial README.md with overview and setup guide
- 2025-05-22 05:13 PKT: [Task 1.3] Set up frontend with package.json and dependencies
- 2025-05-22 05:14 PKT: [Task 1.4] Set up backend with requirements.txt and .env.example
- 2025-05-22 05:40 PKT: [Task 2.1] Implemented YouTube API integration in youtube_api.py
- 2025-05-22 05:42 PKT: [Task 2.2] Implemented data processing logic in data_processor.py
- 2025-05-22 05:45 PKT: [Task 2.3] Implemented report generation in report_generator.py
- 2025-05-22 06:21 PKT: [Task 2.4] Added Redis caching and quota warnings in cache.py
- 2025-05-22 06:22 PKT: [Task 2.5] Created FastAPI app with modular endpoints in main.py
- 2025-05-22 06:26 PKT: [Task 3.1] Set up React app with routing in App.js
- 2025-05-22 06:27 PKT: [Task 3.2] Added responsive navigation bar with theme toggle in Navbar.js
- 2025-05-22 06:28 PKT: [Task 3.3] Implemented HomePage with search form and feature overview
- 2024-07-26 14:50 PKT: [Task 3.6] Implemented Settings page for API key and quota warnings in Settings.js
- 2024-07-26 14:55 PKT: [Task 3.7] Added reusable chart component in ChartComponent.js
- 2024-07-26 15:00 PKT: [Task 3.8] Verified existing Tailwind CSS setup (client/src/index.css and tailwind.config.js).
- 2024-07-26 15:10 PKT: [Task 4.1] Added initial backend unit tests in server/tests/test_api.py and updated requirements.
- 2024-07-26 15:15 PKT: [Task 4.2] Added initial frontend unit tests for HomePage in client/src/__tests__/Home.test.js.
- 2024-07-27 HH:MM PKT: [Task 5.1] Configured unified Heroku deployment.
- 2024-07-26 15:30 PKT: N/A (Backend Heroku config covered by unified deployment)
- 2024-07-26 16:00 PKT: N/A (Frontend Vercel deployment replaced by unified Heroku)
- 2024-07-27 HH:MM PKT: [Task 5.4] Deployed full application to Heroku.
- 2024-07-27 HH:MM PKT: [Task 6.1] Created API documentation in API.md.
- 2024-07-27 HH:MM PKT: [Task 6.2] Created development documentation in DEVELOPMENT.md.
- 2024-07-27 HH:MM PKT: [Task 6.3] Created user guide in USER_GUIDE.md.
- 2024-07-27 HH:MM PKT: [Task 7.1] Verified all app functionality.
- 2024-07-27 HH:MM PKT: [Task 7.2] Optimized API queries and frontend performance.
- 2024-07-27 HH:MM PKT: [Task 7.3] Finalized all documentation.
