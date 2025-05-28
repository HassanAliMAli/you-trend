# STAGE 1: Build React frontend
FROM node:18-alpine as client-builder

WORKDIR /app/client

# Copy client package.json and package-lock.json (or yarn.lock)
COPY client/package.json client/package-lock.json* ./
# If using yarn, copy yarn.lock instead of package-lock.json*

# Install client dependencies
RUN npm install --legacy-peer-deps

# Copy client source code
COPY ./client ./ 

# Build client
RUN npm run build

# STAGE 2: Build Python backend and serve frontend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app

WORKDIR $APP_HOME

# Install build dependencies for packages like pycairo
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./server ./server
# alembic.ini is in server/, so it's copied with the line above.
# The previous `COPY alembic.ini .` was likely incorrect as alembic.ini is not at the project root.

# Copy built client static files from client-builder stage
COPY --from=client-builder /app/client/build ./client/build

# Expose the port the app runs on
EXPOSE 8000

# Copy Gunicorn configuration
COPY ./server/gunicorn_conf.py ./server/gunicorn_conf.py

# Command to run the application using Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "server/gunicorn_conf.py", "server.main:app"] 