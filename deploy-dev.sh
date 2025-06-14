#!/bin/bash

APP_NAME=polybot
SERVICE_FILE=polybot-dev.service
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
PROJECT_DIR="/home/ubuntu/PolybotServicePython"

# Stop and remove any existing container
echo "Stopping existing container..."
docker stop polybot-container || true
docker rm polybot-container || true

# Build the Docker image
echo "Building Docker image..."
docker build -t polybot-image .

# Set up the environment variable for Telegram Bot Token
echo "Setting Telegram Bot Token environment variable..."
BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)

# Run the Docker container with the Telegram Bot Token
echo "Starting the Docker container..."
docker run -d -p 8889:8889 --name polybot-container -e TELEGRAM_BOT_TOKEN=$BOT_TOKEN polybot-image

echo "Docker container status:"
docker ps -a

# Clean up unused Docker images, containers, and volumes
echo "Cleaning up unused Docker resources..."
docker system prune -f --volumes

# Optionally: You can still have your systemd service if needed to manage it via systemd
echo "Copying service file..."
sudo cp $SERVICE_FILE $SERVICE_PATH

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start $SERVICE_FILE

echo "Service status:"
sudo systemctl status $SERVICE_FILE --no-pager

##!/bin/bash
#
#APP_NAME=polybot
#SERVICE_FILE=polybot-dev.service
#SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
#PROJECT_DIR="/home/ubuntu/PolybotServicePython"
#
#echo "Stopping existing service..."
#sudo systemctl stop $SERVICE_FILE || true
#
#echo "Pulling latest code from GitHub..."
#cd $PROJECT_DIR || exit 1
#git fetch origin dev
#git reset --hard origin/dev
#
#echo "Setting up Python virtual environment..."
#if [ ! -d ".venv" ]; then
#  python3 -m venv .venv
#fi
#
#echo "Activating venv..."
#source .venv/bin/activate
#
#echo "Upgrading pip and installing dependencies..."
#pip install --upgrade pip
#pip install -r requirements.txt
#
#echo "Setting Telegram webhook to HTTPS domain..."
#BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)
#WEBHOOK_URL="https://natalie-bot-dev.fursa.click/$BOT_TOKEN"
#
#curl -s -F "url=$WEBHOOK_URL" \
#     -F "certificate=@polybot/polybot_dev.crt" \
#     https://api.telegram.org/bot$BOT_TOKEN/setWebhook
#
#echo "Copying service file..."
#sudo cp $SERVICE_FILE $SERVICE_PATH
#
#echo "Reloading systemd daemon..."
#sudo systemctl daemon-reload
#
#echo "Starting service..."
#sudo systemctl start $SERVICE_FILE
#
#echo "Service status:"
#sudo systemctl status $SERVICE_FILE --no-pager
