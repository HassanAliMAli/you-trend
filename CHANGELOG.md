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
- Changed `/api/trends` (main and /channels) and `/api/compare` endpoints from GET to POST, and updated them to use Pydantic models for request bodies to resolve 405 errors from frontend.
- Corrected Pydantic model definitions in `server/api/trends.py` and `server/api/compare.py` to use `pydantic.Field` instead of `fastapi.Query` for request body fields, and ensured POST endpoints explicitly use `Body(...)` for the request model parameter. This resolves 400 and 422 errors.

### Removed
- Render deployment configuration (`server/render.yml`).
- Vercel deployment configuration (`client/vercel.json`).
- Entire backend test infrastructure (`server/tests/` directory and test-specific dependencies from `requirements.txt`) to rely solely on real-time API calls.

### Fixed
- Added `ajv` as a direct dependency (`"ajv": "8.12.0"`) in `client/package.json` to resolve a build error (`Cannot find module 'ajv/dist/compile/codegen'`) during `npm run build` on Heroku Docker deployment.
- Updated `Dockerfile` to install `build-essential`, `pkg-config`, and `libcairo2-dev` in the Python stage to allow successful installation of `pycairo` (a `reportlab` dependency) during Heroku Docker build.
- Changed local module imports in `server/main.py` to use explicit relative paths (e.g., `from .api...`) to fix `ModuleNotFoundError: No module named 'api'` when running with Gunicorn in Docker on Heroku.
- Changed local module imports in `server/api/trends.py`, `server/api/compare.py`, `server/api/reports.py`, `server/api/status.py`, `server/api/users.py`, and `server/api/alerts.py` to use explicit relative paths (e.g., `from ..utils...`) to resolve `ModuleNotFoundError` issues when running with Gunicorn in Docker on Heroku.
- Adjusted `server/gunicorn_conf.py` to use a more conservative number of workers (defaulting to 2, respecting `WEB_CONCURRENCY` if set to 1 or 2) to prevent R14 memory errors on Heroku free dynos.
- Added `email-validator` to `requirements.txt` to resolve Heroku deployment error caused by missing dependency for Pydantic email validation.
- Imported `Depends` from `fastapi` in `server/utils/auth.py` to fix `NameError` during Heroku deployment.
- Moved definition of `oauth2_scheme_optional` before its usage in `server/utils/auth.py` to resolve `NameError`.
- Moved import block for `Session`, `user_crud`, `database`, and `UserModel` to the top of `server/utils/auth.py` to resolve `NameError` for `database`.
- Added `python-multipart` to `requirements.txt` to resolve `RuntimeError` for form data handling in FastAPI.
- Defined `get_current_active_user` function and `oauth2_scheme` in `server/utils/auth.py` to resolve `AttributeError` in `alerts.py`.
- Corrected import in `server/main.py` from `get_redis_client` to `redis_client` and `clear_specific_cache` to `clear_cache` to match `server/utils/cache.py` and resolve `ImportError`.

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
- `CONVO.md` file and all references to maintaining it.

## <Date>

- **MOD**: Updated `