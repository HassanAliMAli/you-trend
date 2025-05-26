# API Documentation

This document provides details about the YouTrend backend API endpoints.

## Base URL

The API is hosted at `[Your Heroku App URL]/api` (replace `[Your Heroku App URL]` with the actual URL after deployment).

## Authentication

The YouTube Data API v3 key is required for fetching data. This key is configured on the backend and not directly exposed via these endpoints.

## Endpoints

### 1. `/trends`

- **Method:** `POST`
- **Description:** Fetches and analyzes YouTube trends based on specified criteria.
- **Request Body (JSON):**
  ```json
  {
    "keyword": "string (required)",
    "country": "string (optional, default: 'PK')",
    "niche": "string (optional)",
    "date_focus": "string (optional, enum: ['uploaded', 'trending', 'performance'], default: 'trending')",
    "start_date": "string (optional, format: 'YYYY-MM-DD')",
    "end_date": "string (optional, format: 'YYYY-MM-DD')",
    "duration": "string (optional, enum: ['any', 'short', 'medium', 'long'])",
    "language": "string (optional, ISO 639-1 code, e.g., 'en')",
    "sort_order": "string (optional, enum: ['relevance', 'viewCount', 'date', 'rating'])"
  }
  ```
- **Success Response (200 OK):**
  - **Content:** JSON object containing ranked channels, videos, topics, and suggested niches.
  ```json
  {
    "channels": [
      {
        "id": "string",
        "title": "string",
        "subscriberCount": "integer",
        "videoCount": "integer",
        "viewCount": "integer",
        "avg_views_per_video": "float",
        "upload_frequency_per_month": "float",
        "weighted_score": "float"
      }
      // ... more channels
    ],
    "videos": [
      {
        "id": "string",
        "title": "string",
        "channelTitle": "string",
        "viewCount": "integer",
        "likeCount": "integer",
        "commentCount": "integer",
        "publishedAt": "string (ISO 8601 date-time)",
        "duration": "string (ISO 8601 duration)",
        "recency_score": "float",
        "engagement_score": "float",
        "weighted_score": "float"
      }
      // ... more videos
    ],
    "topics": ["string", ...],
    "suggested_niches": ["string", ...]
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Invalid input parameters.
  - `422 Unprocessable Entity`: Validation error.
  - `500 Internal Server Error`: Server-side error or YouTube API issue.

### 2. `/compare`

- **Method:** `POST`
- **Description:** Compares metrics for up to two niches.
- **Request Body (JSON):**
  ```json
  {
    "niche1": "string (required)",
    "niche2": "string (optional)",
    "country": "string (optional, default: 'PK')",
    "date_focus": "string (optional, enum: ['uploaded', 'trending', 'performance'], default: 'trending')",
    "start_date": "string (optional, format: 'YYYY-MM-DD')",
    "end_date": "string (optional, format: 'YYYY-MM-DD')"
  }
  ```
- **Success Response (200 OK):**
  - **Content:** JSON object with comparison data.
  ```json
  {
    "niche1_data": {
      "total_videos": "integer",
      "avg_views": "float",
      "avg_likes": "float",
      "avg_comments": "float",
      "top_channels": [ /* as in /trends */ ]
    },
    "niche2_data": { // if niche2 was provided
      "total_videos": "integer",
      "avg_views": "float",
      "avg_likes": "float",
      "avg_comments": "float",
      "top_channels": [ /* as in /trends */ ]
    }
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Invalid input parameters.
  - `422 Unprocessable Entity`: Validation error.
  - `500 Internal Server Error`: Server-side error.

### 3. `/reports`

- **Method:** `POST`
- **Description:** Generates and allows download of analysis reports.
- **Request Body (JSON):**
  ```json
  {
    "report_type": "string (required, enum: ['txt', 'csv', 'xlsx', 'pdf'])",
    "keyword": "string (required if data not already generated from /trends)",
    // ... include other filter parameters from /trends if generating new data
    "trend_data": "object (optional, provide data from a previous /trends call to generate report from it)"
  }
  ```
- **Success Response (200 OK):**
  - **Content:** The requested report file (e.g., `text/plain`, `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/pdf`).
  - **Headers:** `Content-Disposition: attachment; filename="report.[type]"`
- **Error Responses:**
  - `400 Bad Request`: Invalid input parameters or missing data.
  - `422 Unprocessable Entity`: Validation error.
  - `500 Internal Server Error`: Error during report generation.

### 4. `/status`

- **Method:** `GET`
- **Description:** Checks the API status and YouTube API quota usage.
- **Success Response (200 OK):**
  ```json
  {
    "status": "ok",
    "youtube_api_quota": {
      "used": "integer",
      "limit": "integer", // Typically 10,000 units per day for new projects
      "percentage_used": "float"
    },
    "redis_status": "connected" // or "disconnected" / "error"
  }
  ```
- **Error Responses:**
  - `500 Internal Server Error`: If Redis is down or another critical error occurs.

## Rate Limiting

- The API uses YouTube Data API v3, which has its own quota limits (typically 10,000 units/day for a new project).
- Caching is implemented (1-hour TTL) to reduce redundant API calls.
- The `/status` endpoint provides quota usage information.

## Error Handling

- Standard HTTP status codes are used.
- Error responses include a JSON body with a "detail" field explaining the error:
  ```json
  { "detail": "Error message describing the issue." }
  ``` 