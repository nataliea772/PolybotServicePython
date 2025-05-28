#!/bin/bash

APP_NAME=polybot
SERVICE_FILE=polybot-dev.service

echo "Stopping existing service..."
sudo systemctl stop $SERVICE_FILE || true

echo "Pulling latest code from GitHub..."
cd /home/ubuntu/PolybotServicePython || exit 1
git pull origin dev

echo "Activating venv..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Restarting service..."
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_FILE
sudo systemctl status $SERVICE_FILE
