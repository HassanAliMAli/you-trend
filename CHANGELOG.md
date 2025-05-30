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
- Re-created `CONVO.md` to log conversation after rollback.
- Added console logging in `client/src/contexts/ApiContext.js` to trace API key availability in `localStorage` upon component mount and during API calls to debug `400 Bad Request` errors.
- Added a `console.log` in `client/src/contexts/ApiContext.js` within the `analyzeTrends` function to output the raw `response.data` received from the backend. This is to help diagnose why "No videos found" is displayed despite a 200 OK response from the `/api/trends` endpoint.

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
- Updated `client/src/contexts/ApiContext.js` to automatically include the stored API key in `analyzeTrends` and `compareNiches` requests.
- Simplified API key retrieval in `analyzeTrends` and `compareNiches` functions within `client/src/contexts/ApiContext.js`. Both functions now consistently use the `getApiKey()` method and feature updated console logging for easier debugging of API key status during requests.

### Removed
- Render deployment configuration (`server/render.yml`).
- Vercel deployment configuration (`client/vercel.json`).
- Entire backend test infrastructure (`server/tests/` directory and test-specific dependencies from `requirements.txt`) to rely solely on real-time API calls.
- Frontend test file `client/src/__tests__/Home.test.js` and its parent directory `client/src/__tests__/` to align with the goal of removing test-specific code.
- All locally added test files (`server/tests/utils/*` and `server/tests/api/*`) due to rollback to commit `96ab9f3`.
- Locally created `CONVO.md` due to rollback (re-created subsequently).
- Deleted `CONVO.md` file as per user request.
- Removed emergency mock data fallback from `compareNiches` function in `client/src/contexts/ApiContext.js` to prevent displaying sample data on API errors.

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
- Added explicit checks in `/api/trends` and `/api/compare` endpoints to ensure a YouTube API key is available (from request, user profile, or environment variable) before attempting to call the YouTube API. If no key is found, a 400 Bad Request error is returned with a clear message. This directly addresses the 'YouTube API key must be provided' errors and makes API key issues easier to diagnose.
- **Note for Frontend**: The `/api/compare` endpoint expects the `niches` field in its POST request body to be a single string with niche keywords separated by commas (e.g., `"gaming,cooking,travel"`). The frontend needs to ensure it sends data in this format to avoid 422 Unprocessable Entity errors.
- Investigated potential mock data usage based on search results. Confirmed that a comment in `server/utils/data_processor.py` mentioning "mock channel objects" was misleading and not indicative of actual mock data usage; the code processes real API data. No other backend mock data was found. Frontend test files and a UI fallback mechanism with sample data structure in `client/src/contexts/ApiContext.js` were noted and await user decision for removal/modification.
- Investigated Heroku logs showing `400 Bad Request` for `/api/trends` and `422 Unprocessable Entity` for `/api/compare`.
  - The `400` error on `/api/trends` is due to the YouTube API key not being found from any available source (request body, user profile, or environment variable). **Action Required**: Ensure the `YOUTUBE_API_KEY` environment variable is set in Heroku app settings as a global fallback. Frontend should also ideally send an `api_key` in the POST request body if provided by the user.
  - The `422` error on `/api/compare` is due to the frontend sending data in a format that doesn't match the `CompareNichesRequestBody` Pydantic model (likely the `niches` field not being a comma-separated string, or other validation failures). **Action Required**: Frontend needs to ensure the `niches` field is a single comma-separated string (e.g., `"gaming,tech"`) and all other required fields are sent correctly.
- In `client/src/contexts/ApiContext.js` `compareNiches` function: converted `niches` array to a comma-separated string, removed GET fallback logic, and ensured mock data generation is removed.
- In `client/src/contexts/ApiContext.js` `analyzeTrends` function: mapped frontend `duration` and `order` values to API-expected formats, ensured `max_results` is an integer, and standardized `country` parameter handling.
- Refactored `requestParams` construction in `analyzeTrends` and `compareNiches` in `client/src/contexts/ApiContext.js` for clarity and to ensure correct API key usage. Added console logging for API key retrieval in these functions for debugging.
- Added more specific console logging in `client/src/contexts/ApiContext.js` for `saveApiKey` and for API key retrieval within `analyzeTrends` and `compareNiches` (using both `getApiKey()` and direct `localStorage.getItem()`) to further diagnose API key issues.
- Refactored `client/src/pages/Settings.js` to correctly use `localStorage` (via `ApiContext` functions like `saveApiKey`, `getApiKey`) instead of `sessionStorage` for API key management. This ensures the API key is persisted correctly and available to other parts of the application.
- Adjusted `Settings.js` to properly use `useApi` hook and interact with `ApiContext` for fetching and displaying quota usage.
- Enhanced API key saving in `client/src/contexts/ApiContext.js`:
  - Added `trim()` to `saveApiKey` to remove leading/trailing whitespace from the API key before saving.
  - Added logging to confirm the API key value immediately after it is set in `localStorage`.
- Added logging in `client/src/pages/Settings.js` within `handleSaveSettings` to display the API key value being passed to `saveApiKey`.
- Removed references to missing `logo192.png` and `logo512.png` from `client/public/manifest.json` to prevent console errors related to these icons.
- Corrected a critical bug where `client/src/utils/api.js` (used by `HomePage.js`) and `client/src/contexts/ApiContext.js` (used by `Settings.js` and API calls) were using different `localStorage` key names (`youtrend_youtube_api_key` vs. `youtube_api_key`) for storing and retrieving the YouTube API key. Standardized to `youtube_api_key` across both files. This resolves inconsistencies in API key detection and usage.
- Corrected the `handleClearApiKey` function in `client/src/components/ApiKeyForm.js` to use the centralized `removeApiKey` utility function. This ensures that the "Remove" button in the API key form correctly targets the `youtube_api_key` in `localStorage`, fixing a bug where it was attempting to remove an outdated key name (`youtrend_youtube_api_key`).
- Corrected a syntax error (`axios.create({x```) in `client/src/contexts/ApiContext.js` that was causing linter errors and potential runtime issues.

### Added
- Added detailed console logging within the `generateRecommendations` function in `client/src/contexts/ApiContext.js` to inspect `data.videos` and `data.topics` just before their `.length` properties are accessed. This is to help diagnose a "Cannot read properties of undefined (reading 'length')" error during trend analysis.

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