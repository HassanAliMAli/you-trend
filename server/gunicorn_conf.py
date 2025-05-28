import os

# Server socket
# Use environment variable for port, default to 8000 if not set.
# Gunicorn will listen on all interfaces (0.0.0.0) by default.
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Worker processes
# Number of worker processes. A common recommendation is (2 * cpu_count) + 1.
# Heroku typically sets WEB_CONCURRENCY environment variable.
workers = int(os.getenv("WEB_CONCURRENCY", os.cpu_count() * 2 + 1 if os.cpu_count() else 3))
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = os.getenv("GUNICORN_ACCESS_LOG_FORMAT", '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"')

# Keep alive settings
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# Timeout settings
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120)) # Heroku recommends 30, but for potentially long report generation, 120 might be safer initially
worker_tmp_dir = "/dev/shm" # For environments with /dev/shm, like many Linux systems including Docker containers

# For debugging, you can enable reload in development, but it's not for production
# reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

print(f"Gunicorn config: workers={workers}, port={port}, loglevel={loglevel}") 