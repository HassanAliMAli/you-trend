# TubeTrends - YouTube Trend Analysis Platform

TubeTrends is a web application designed to help content creators and marketers identify and analyze trending topics, videos, and channels on YouTube. It provides insights into what's currently popular, suggests video ideas, and allows for comparative analysis of different niches.

## Features

-   **Trend Discovery**: Find trending videos and topics based on keywords, categories, or regions.
-   **Niche Analysis**: Analyze specific niches for popular content and channels.
-   **Video Idea Generation**: Get suggestions for new video content based on current trends.
-   **Comparative Analysis**: Compare metrics and trends between different videos or channels.
-   **Data Export**: Export trend data and reports in various formats (CSV, PDF, Excel, TXT).
-   **User Accounts**: Secure user registration and login to save preferences and API keys.
-   **Personalized API Key**: Users can securely store their own YouTube Data API v3 key.
-   **Trend Alerts**: (Backend Implemented) Users can subscribe to alerts for specific keywords or niches.
-   **Admin Panel**: (Backend Implemented) Basic user management capabilities for administrators.
-   **Caching**: Utilizes Redis (if available) for caching API responses to improve performance and manage API quota usage.
-   **Rate Limiting**: API endpoints are rate-limited to prevent abuse.
-   **Dockerized**: The application is containerized using Docker for consistent development and deployment.

## Project Structure

```
TubeTrends/
├── client/             # React Frontend Application
│   ├── public/
│   └── src/
├── docs/               # Project Documentation (API, Development, User Guide)
├── server/             # FastAPI Backend Application
│   ├── alembic/        # Database migrations
│   ├── api/            # API endpoint routers
│   ├── crud/           # CRUD operations for database models
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic schemas for data validation
│   ├── utils/          # Utility modules (YouTube API, data processing, etc.)
│   └── main.py         # Main FastAPI application file
├── .dockerignore       # Specifies files to ignore for Docker builds
├── .env.example        # Example environment variables
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── CHANGELOG.md        # Log of changes to the project
├── CONVO.md            # Log of conversation with AI assistant (if applicable)
├── docker-compose.yml  # Docker Compose for local development orchestration
├── Dockerfile          # Dockerfile for building the application image
├── heroku.yml          # Heroku deployment configuration for Docker
├── PRD.md              # Product Requirements Document
├── Procfile            # Heroku Procfile (mainly for buildpack deployments, less relevant for Docker)
├── README.md           # This file
├── requirements.txt    # Python backend dependencies
├── runtime.txt         # Python runtime version for Heroku buildpacks
└── TASKS.md            # Development tasks
```

## Prerequisites

Before you begin, ensure you have the following installed:

-   **Node.js and npm**: For the React frontend (npm is used for building the client in Docker stage 1).
-   **Python 3.11**: For the FastAPI backend (as specified in `runtime.txt` and `Dockerfile`).
-   **Docker**: For containerizing and running the application locally.
-   **Docker Compose**: For orchestrating multi-container applications locally.

## Environment Variables

Create a `.env` file in the project root. This file is used by Docker Compose for local development and serves as a reference for Heroku Config Vars.

**Key Variables (refer to or create `.env.example`):**

-   `SECRET_KEY`: A strong secret key for JWT signing (e.g., `openssl rand -hex 32`).
-   `YOUTUBE_API_KEY`: Your YouTube Data API v3 key (fallback if user doesn't provide one).
-   `DATABASE_URL`: Database connection string. 
    *   Local Docker (SQLite fallback): Leave unset or `sqlite:///./test.db` (creates `/app/server/test.db` in container).
    *   Local Docker (Postgres service): `postgresql://youruser:yourpassword@db:5432/tubetrends_db` (match `docker-compose.yml` service).
    *   Heroku: Provided by Heroku Postgres add-on.
-   `REDIS_HOST`: Redis hostname (e.g., `localhost` or `redis` for Docker Compose service). Defaults to `localhost`.
-   `REDIS_PORT`: Redis port (e.g., `6379`). Defaults to `6379`.
-   `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT lifetime (e.g., `30`). Defaults to `30`.
-   `PORT`: Server listening port (e.g., `8000`). For Heroku, set automatically.

**Example `.env` (local SQLite, no external Redis):**
```
SECRET_KEY=replace_with_a_strong_random_secret_key
YOUTUBE_API_KEY=replace_with_your_youtube_api_key
# DATABASE_URL=  # Leave unset for SQLite in /app/server/test.db inside container
ACCESS_TOKEN_EXPIRE_MINUTES=60
PORT=8000
# REDIS_HOST=localhost # Uncomment if running Redis locally outside compose
# REDIS_PORT=6379
```

## Getting Started Locally with Docker

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url> TubeTrends
    cd TubeTrends
    ```
2.  **Set up `.env` file:** Create `.env` in the project root as described above.
3.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose build
    docker-compose up
    ```
    The application (backend API & frontend) will be at `http://localhost:8000` (or your configured `PORT`).
    API docs: `http://localhost:8000/api/docs`.

4.  **Database Migrations (Alembic - first time/model changes):**
    Execute migrations inside the running `backend` container:
    ```bash
    docker-compose exec backend bash -c "cd server && alembic upgrade head"
    ```
5.  **Stopping the application:**
    ```bash
    docker-compose down
    ```

## Deployment to Heroku (Docker & `heroku.yml`)

This project is configured for deploying to Heroku using its Docker container registry via `heroku.yml`.

1.  **Install Heroku CLI and log in.**
2.  **Create a Heroku app:** `heroku create your-unique-app-name`
3.  **Provision Add-ons:**
    *   PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev -a your-app-name`
    *   Redis: `heroku addons:create heroku-redis:hobby-dev -a your-app-name`
    (Heroku sets `DATABASE_URL`, `REDIS_URL` config vars).
4.  **Set other Heroku Config Vars:**
    ```bash
    heroku config:set SECRET_KEY="your_production_secret_key" -a your-app-name
    heroku config:set YOUTUBE_API_KEY="your_production_youtube_api_key" -a your-app-name
    heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES="60" -a your-app-name
    # PORT is set automatically by Heroku.
    ```
5.  **Deploy:** Ensure `Dockerfile` and `heroku.yml` are committed.
    ```bash
    git push heroku main # Or your deployment branch
    ```
    Heroku uses `heroku.yml` to build the Docker image, run `release` commands (like `alembic upgrade head`), and deploy.

## Development without Docker (Alternative / Backend Only)

(Instructions for frontend development are standard for React applications)

1.  Navigate to `server/` directory.
2.  Create and activate a Python virtual environment (e.g., `python -m venv venv`, `source venv/bin/activate`).
3.  Install dependencies: `pip install -r ../requirements.txt`.
4.  Set environment variables (e.g., in your shell or a `server/.env` file loaded by your IDE).
5.  Run database migrations: `alembic upgrade head` (from `server/` dir).
6.  Run FastAPI app: `python main.py` (from `server/` dir).

## API Endpoints

Refer to the Swagger UI at `/api/docs` when the application is running for detailed API endpoint information.

## Contributing

(Guidelines for contributing can be added here if the project becomes open-source.)

## License

(A license, e.g., MIT, can be specified here.)
