# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initialized Git repository and configured remote for `https://github.com/HassanAliMAli/you-trend.git`.
- Created `.gitignore` with common Node.js and Python exclusions.
- Created `CHANGELOG.md`.
- Created API documentation `docs/API.md` (Task 6.1).
- Created Development documentation `docs/DEVELOPMENT.md` (Task 6.2).
- Created User Guide `docs/USER_GUIDE.md` (Task 6.3).
- Configured unified Heroku deployment (Task 5.1).
- Deployed full application to Heroku (Task 5.4).
- Verified all app functionality (Task 7.1).
- Optimized API queries and frontend performance (Task 7.2).
- Finalized all documentation (Task 7.3).

### Changed
- Switched to unified Heroku deployment for frontend and backend.
- Switched backend deployment from Render to Heroku (superseded by unified deployment).
- Amended initial commit to remove `CONVO.md` as per user request.

### Removed
- Render deployment configuration (`server/render.yml`).
- Vercel deployment configuration (`client/vercel.json`).

## [0.1.0] - 2024-07-26
### Added
- Initial project structure with /client, /server, /docs.
- Initial README.md with overview and setup guide.
- Frontend setup with package.json and dependencies (React, Tailwind CSS, Chart.js, Axios).
- Backend setup with requirements.txt and .env.example.
- YouTube API integration in server/utils/youtube_api.py.
- Data processing logic in server/utils/data_processor.py.
- Report generation in server/utils/report_generator.py.
- Redis caching and quota warnings in server/utils/cache.py.
- FastAPI app with modular endpoints in server/main.py.
- React app setup with routing in client/src/App.js.
- Responsive navigation bar with theme toggle in client/src/components/Navbar.js.
- HomePage with search form and feature overview in client/src/pages/HomePage.js.
- Settings page for API key and quota warnings in client/src/pages/Settings.js.
- Reusable chart component in client/src/components/ChartComponent.js.
- Initial backend unit tests in server/tests/test_api.py.
- Initial frontend unit tests for HomePage in client/src/__tests__/Home.test.js.
- Configuration for unified Heroku deployment (Procfile, .buildpacks, FastAPI static serving).
- Deployment of full application to Heroku.
- Created API documentation (`docs/API.md`).
- Created Development documentation (`docs/DEVELOPMENT.md`).
- Created User Guide (`docs/USER_GUIDE.md`).
- Verified all app functionality.
- Optimized API queries and frontend performance.
- Finalized all documentation.

### Changed
- Updated .gitignore with comprehensive list of common ignores.
- Verified existing Tailwind CSS setup.

### Fixed
- N/A

### Removed
- Vercel and Render specific deployment configurations and tasks.