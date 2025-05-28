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
- Dockerfile for containerizing the backend server.
- `server/gunicorn_conf.py` for Gunicorn configuration.
- `docker-compose.yml` for orchestrating the backend service (with placeholders for DB/Redis).
- Admin endpoints for user management by ID: GET, PUT, DELETE `/api/users/manage/{user_id}`.
- `AlertSubscription` model (`server/models/alert.py`), Pydantic schemas (`server/schemas/alert.py`), and CRUD operations (`server/crud/alert.py`) for Trend Alerts.
- Alembic migration for `alert_subscriptions` table.
- API endpoints for user alert subscriptions: POST, GET (all), GET (specific), PUT, DELETE under `/api/alerts`.
- `server/utils/alert_processor.py` with `check_single_alert_subscription` and `process_all_alerts` for background alert checking.
- APScheduler integration in `server/main.py` to run `process_all_alerts` periodically.
- `slowapi` for basic rate limiting (100 requests/minute/IP) integrated into `server/main.py`.
- `heroku.yml` for Docker-based deployment on Heroku, including release phase for migrations.
- `.dockerignore` file to optimize Docker build context.
- Instructions to `README.md` (summary provided separately) for Docker local development and Heroku Docker deployment.
- SQLite database files (`test.db`, `*.sqlite3`, etc.) to `.gitignore`.

### Changed
- Switched to unified Heroku deployment for frontend and backend.
- Switched backend deployment from Render to Heroku (superseded by unified deployment).
- Amended initial commit to remove `CONVO.md` as per user request.
- Modified `server/utils/youtube_api.py` functions to accept an optional `api_key` argument, falling back to the `YOUTUBE_API_KEY` environment variable if not provided. This ensures API keys are not hardcoded and can be user-supplied.
- Updated `README.md` with clearer instructions for setting the `YOUTUBE_API_KEY` in a root `.env` file.
- Updated `server/models/__init__.py`, `server/schemas/__init__.py`, `server/crud/__init__.py` to include alert-related modules.
- Updated `server/main.py` to include the alerts API router, APScheduler setup, and slowapi rate limiting.
- Updated `requirements.txt` with `APScheduler` and `slowapi`.
- Modified `Dockerfile` to use a multi-stage build, incorporating the React client build into the final image.
- Updated `docker-compose.yml` to use `env_file` for local `.env` loading and removed direct volume mount for `.env`.

### Removed
- Render deployment configuration (`server/render.yml`).
- Vercel deployment configuration (`client/vercel.json`).
- Entire backend test infrastructure (`server/tests/` directory and test-specific dependencies from `requirements.txt`) to rely solely on real-time API calls.

### Fixed
- Added `ajv` as a direct dependency (`"ajv": "8.12.0"`) in `client/package.json` to resolve a build error (`Cannot find module 'ajv/dist/compile/codegen'`) during `npm run build` on Heroku Docker deployment.

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
- Corrected Dockerfile to ensure `alembic.ini` and `gunicorn_conf.py` are correctly handled within the Docker image context.
- Ensured Alembic migration command in `heroku.yml` (`cd server && alembic upgrade head`) targets the correct directory.

### Removed
- Vercel and Render specific deployment configurations and tasks.

## <Date>

- **MOD**: Updated `requirements.txt` with `SQLAlchemy`, `psycopg2-binary`, `alembic`, and `bcrypt` for database integration.
- **ADD**: Initialized Alembic for database migrations (`server/alembic`).
- **MOD**: Configured `server/alembic.ini` and `server/alembic/env.py` to use `DATABASE_URL` from `.env` and target model metadata.
- **ADD**: Created `server/models/base.py` for SQLAlchemy declarative base.
- **ADD**: Created `server/models/user.py` with `User` model including fields for authentication and API key management.
- **ADD**: Created `server/models/__init__.py`.
- **ADD**: Created `server/utils/database.py` for database session management and engine creation, with a fallback to SQLite for local development.
- **ADD**: Generated initial Alembic migration `server/alembic/versions/bccb60026ecb_create_users_table.py` and populated it to create the `users` table.
- **ADD**: Implemented `server/utils/auth.py` with password hashing (bcrypt for byte consistency with User model) and JWT creation/decoding utilities. Includes fallbacks for `SECRET_KEY` and `ACCESS_TOKEN_EXPIRE_MINUTES` from `.env`.
- **ADD**: Implemented `get_current_user_optional` in `server/utils/auth.py` for endpoints allowing optional authentication.
- **ADD**: Implemented user API endpoints in `server/api/users.py` for registration, login (token), fetching/updating current user details (`/me`), and a basic admin endpoint to list users (superuser only).
- **MOD**: Integrated the new `users_router` into `server/main.py`.
- **MOD**: Refactored `server/main.py` to improve CORS, static file serving for React app, global exception handling, and API route prefixing.
- **MOD**: Updated API endpoints in `server/api/trends.py` (`/trends`, `/channels`, `/categories`) and `server/api/compare.py` (`/compare`) to support user-specific API keys. These endpoints now prioritize API key usage: query parameter -> authenticated user's saved key -> system .env key.