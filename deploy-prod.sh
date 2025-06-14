#!/bin/bash

# Define the application name and the Docker image
APP_NAME=polybot
IMAGE_NAME=polybot-image
CONTAINER_NAME=polybot-container

# Stop the existing container (if it exists)
echo "Stopping existing container..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

# Pull the latest code from GitHub (if you're using Git for the app)
echo "Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the Docker container with environment variables
echo "Starting the container..."
docker run -d -p 8889:8889 --name $CONTAINER_NAME \
  -e TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN} \
  -e BOT_APP_URL=${BOT_APP_URL} \
  $IMAGE_NAME

# Check the container status
echo "Service status:"
docker ps --filter "name=$CONTAINER_NAME"
