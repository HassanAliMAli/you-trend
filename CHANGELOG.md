# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initialized Git repository and configured remote for `https://github.com/HassanAliMAli/you-trend.git`.
- Created `.gitignore` with common Node.js and Python exclusions.
- Created `CHANGELOG.md`.
- Deployed frontend to Vercel (Task 5.3).

### Changed
- Amended initial commit to remove `CONVO.md` as per user request.

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
- Vercel deployment configuration for client in client/vercel.json.
- Render deployment configuration for server in server/render.yml.
- Deployed frontend to Vercel.

### Changed
- Updated .gitignore with comprehensive list of common ignores.
- Verified existing Tailwind CSS setup.

### Fixed
- N/A

### Removed
- N/A