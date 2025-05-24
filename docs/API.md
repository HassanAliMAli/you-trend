# YouTrend API Documentation

This document provides details about the YouTrend backend API endpoints.

**Base URL**: `/api`

## Authentication

Currently, the API does not require authentication for most endpoints. However, a valid YouTube API key must be configured on the server for the application to function correctly.

## Common Responses

- **Success**: `200 OK`
- **Bad Request**: `400 Bad Request` (e.g., invalid parameters)
- **Not Found**: `404 Not Found` (e.g., report ID does not exist)
- **Internal Server Error**: `500 Internal Server Error`

---

## Trends API

**Prefix**: `/trends`

Endpoints for analyzing YouTube video and channel trends.

### 1. Get Trends (Videos and Analysis)

- **Endpoint**: `GET /`
- **Description**: Fetches trending videos or search results and provides trend analysis.
- **Query Parameters**:
    - `query` (str, optional): Search term for videos. If empty, fetches general trending videos.
    - `category` (str, optional): YouTube video category ID (e.g., '10' for Music).
    - `country` (str, optional): Country code (e.g., 'PK', 'US'). Default: 'PK'.
    - `duration` (str, optional): Video duration filter. Accepted values:
        - 'Short (< 4 minutes)'
        - 'Medium (4-20 minutes)'
        - 'Long (> 20 minutes)'
    - `max_results` (int, optional): Maximum number of results. Default: 10, Max: 50.
    - `order` (str, optional): Sort order. Accepted values: 'viewCount', 'relevance', 'rating', 'date'. Default: 'viewCount'.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Found X videos matching your criteria",
    "data": {
      "videos": [
        // List of ranked video objects
      ],
      "topics": [
        // List of identified topic objects/strings
      ],
      "ideas": [
        // List of generated video idea objects/strings
      ],
      "insights": {
        // Metadata insights object
      }
    }
  }
  ```
- **Example**: `GET /api/trends?query=python%20programming&country=US&max_results=5`

### 2. Get Trending Channels

- **Endpoint**: `GET /channels`
- **Description**: Fetches trending channels based on search parameters.
- **Query Parameters**:
    - `query` (str, optional): Search term for channels.
    - `country` (str, optional): Country code. Default: 'PK'.
    - `max_results` (int, optional): Maximum number of results. Default: 10, Max: 50.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Found X channels matching your criteria",
    "data": {
      "channels": [
        // List of ranked channel objects
      ],
      "subscriber_distribution": {
        // Object describing subscriber distribution
      },
      "posting_frequency": {
        // Object describing posting frequency
      }
    }
  }
  ```
- **Example**: `GET /api/trends/channels?query=tech%20review&country=GB`

### 3. Get Video Categories

- **Endpoint**: `GET /categories`
- **Description**: Fetches available YouTube video categories for a specific region.
- **Query Parameters**:
    - `country` (str, optional): Country code. Default: 'PK'.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Found X video categories",
    "data": {
      "categories": [
        // List of category objects (e.g., {"id": "10", "title": "Music"})
      ]
    }
  }
  ```
- **Example**: `GET /api/trends/categories?country=IN`

---

## Compare API

**Prefix**: `/compare`

Endpoints for comparing YouTube niches.

### 1. Compare Niches

- **Endpoint**: `GET /`
- **Description**: Compares different niches based on their YouTube metrics.
- **Query Parameters**:
    - `niches` (str, required): Comma-separated list of niches to compare (e.g., 'Gaming,Tech,Beauty'). Max 5 niches.
    - `country` (str, optional): Country code. Default: 'PK'.
    - `max_results` (int, optional): Max videos per niche for analysis. Default: 10, Max: 50.
    - `order` (str, optional): Sort order for videos within niches. Default: 'viewCount'.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Successfully compared X niches",
    "data": {
      // Object containing comparison results, typically structured by niche
      // Example:
      // "Gaming": { "avg_views": 100000, "avg_engagement": 0.05, ... },
      // "Tech": { "avg_views": 80000, "avg_engagement": 0.04, ... }
    }
  }
  ```
- **Example**: `GET /api/compare?niches=ai,blockchain,web3&country=US`

### 2. Get Niche Metrics

- **Endpoint**: `GET /metrics`
- **Description**: Fetches detailed metrics for a specific niche.
- **Query Parameters**:
    - `niche` (str, required): The niche to analyze (e.g., 'Gaming').
    - `country` (str, optional): Country code. Default: 'PK'.
    - `max_results` (int, optional): Max videos to analyze for the niche. Default: 10, Max: 50.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Successfully analyzed [niche_name] niche",
    "data": {
      "niche": "[niche_name]",
      "metrics": {
        "avg_views": 0,
        "avg_engagement_rate": 0,
        "video_count": 0
      },
      "topics": [ /* List of topics */ ],
      "channels": [ /* List of top 5 channel objects */ ],
      "video_ideas": [ /* List of video ideas */ ]
    }
  }
  ```
- **Example**: `GET /api/compare/metrics?niche=Sustainable%20Living&country=CA`

---

## Reports API

**Prefix**: `/reports`

Endpoints for generating and downloading reports. Report generation is asynchronous.

### 1. Generate Report

- **Endpoint**: `POST /`
- **Description**: Initiates the generation of a report.
- **Request Body**:
  ```json
  {
    "report_type": "trend", // or "compare"
    "format": "pdf", // "txt", "csv", "xlsx", "pdf"
    "data": { /* Data object relevant to the report_type, typically the response from a /trends or /compare call */ },
    "include_charts": true // boolean, optional, relevant for pdf/xlsx
  }
  ```
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Report generation started. Use the download endpoint to retrieve it.",
    "data": {
      "report_id": "unique-report-id",
      "format": "pdf",
      "download_url": "/api/reports/download/unique-report-id"
    }
  }
  ```

### 2. Get Report Status

- **Endpoint**: `GET /status/{report_id}`
- **Description**: Checks the status of a report generation task.
- **Path Parameters**:
    - `report_id` (str, required): The ID of the report.
- **Success Response (`200 OK`)**:
  - If pending:
    ```json
    {
      "status": "pending",
      "message": "Report generation in progress",
      "data": { "report_id": "unique-report-id" }
    }
    ```
  - If completed:
    ```json
    {
      "status": "completed",
      "message": "Report generation completed",
      "data": {
        "report_id": "unique-report-id",
        "format": "pdf",
        "created_at": "iso-timestamp",
        "download_url": "/api/reports/download/unique-report-id"
      }
    }
    ```
  - If error:
    ```json
    {
      "status": "error",
      "message": "Report generation failed: [error message]",
      "data": {
        "report_id": "unique-report-id",
        "created_at": "iso-timestamp"
      }
    }
    ```

### 3. Download Report

- **Endpoint**: `GET /download/{report_id}`
- **Description**: Downloads a generated report.
- **Path Parameters**:
    - `report_id` (str, required): The ID of the report.
- **Success Response (`200 OK`)**:
    - The raw file content (TXT, CSV, XLSX, PDF) with appropriate `Content-Type` and `Content-Disposition` headers for download.
- **Error Responses**:
    - `404 Not Found`: If `report_id` is invalid or report has expired.
    - `400 Bad Request`: If report generation is still in progress.
    - `500 Internal Server Error`: If report generation failed.

---

## Status API

**Prefix**: `/status`

Endpoint for checking API health and configuration.

### 1. Get API Status

- **Endpoint**: `GET /`
- **Description**: Checks the overall health of the API, YouTube API connectivity, and critical configurations.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "ok", // or "warning"
    "message": "API is fully operational", // or a warning message
    "details": {
      "api_health": "ok",
      "youtube_api": "connected", // or "not_configured", "error"
      "configuration": {
        "youtube_api_key": "configured", // or "missing", "configured_but_error"
        "redis": "configured", // or "default"
        "api_secret": "configured" // or "development"
      },
      "youtube_api_error": "Optional error message if connection failed"
    }
  }
  ```
- **Example**: `GET /api/status` 