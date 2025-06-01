#!/bin/bash

echo "Downloading DB..."
curl -L -o api/database.db https://github.com/your-username/your-repo/releases/download/v1.0.0/database.db

echo "Starting server..."
uvicorn main:app --host 0.0.0.0 --port 8000
