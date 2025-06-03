#!/bin/bash

APP_NAME=polybot
SERVICE_FILE=polybot-prod.service
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
PROJECT_DIR="/home/ubuntu/PolybotServicePython"

echo "Stopping existing service..."
sudo systemctl stop $SERVICE_FILE || true

echo "Pulling latest code from GitHub..."
cd $PROJECT_DIR || exit 1
git pull origin main

echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

echo "Activating venv..."
source .venv/bin/activate

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Copying service file..."
sudo cp $SERVICE_FILE $SERVICE_PATH

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start $SERVICE_FILE

echo "Service status:"
sudo systemctl status $SERVICE_FILE --no-pager
