#!/usr/bin/env bash
# Build script for Render deployment

# Install system dependencies
apt-get update
apt-get install -y ffmpeg libsndfile1 curl

# Create output directory
mkdir -p output

# Set Python path
export PYTHONPATH=/opt/render/project/src

echo "Build completed successfully!" 