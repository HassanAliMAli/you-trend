#!/bin/bash
set -e

# Go to the client directory
cd client

# Install Node.js and npm if not present (Heroku Python buildpack provides nodeenv)
if ! command -v npm &> /dev/null; then
    echo "Node.js and npm not found, installing with nodeenv..."
    pip install nodeenv
    nodeenv -p
fi

# Install frontend dependencies and build
npm install
npm run build 