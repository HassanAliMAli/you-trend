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
5. Add the API key to your .env file

### Deployment
- Frontend: Deploy to Vercel
- Backend: Deploy to Render (with Redis for caching)

## Change Log

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
- 2024-07-26 15:20 PKT: [Task 5.1] Configured Vercel deployment for client in client/vercel.json.
- 2024-07-26 15:30 PKT: [Task 5.2] Configured Render deployment for server in server/render.yml.
- 2024-07-26 15:35 PKT: [Task 5.3] Documented frontend deployment to Vercel (manual user step).
- 2024-07-26 15:40 PKT: [Task 5.4] Documented backend and Redis deployment to Render (manual user step).
