#!/bin/bash

APP_NAME=polybot
SERVICE_FILE=polybot-dev.service
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
PROJECT_DIR="/home/ubuntu/PolybotServicePython"

echo "Stopping existing service..."
sudo systemctl stop $SERVICE_FILE || true

echo "Pulling latest code from GitHub..."
cd $PROJECT_DIR || exit 1
git pull origin dev

echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

echo "Activating venv..."
source .venv/bin/activate

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting Telegram webhook to HTTPS domain..."
BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)
WEBHOOK_URL="https://natalie-bot-dev.fursa.click/$BOT_TOKEN"

curl -s -F "url=$WEBHOOK_URL" \
     -F "certificate=@/etc/nginx/ssl/polybot_dev.crt" \
     https://api.telegram.org/bot$BOT_TOKEN/setWebhook

echo "Copying service file..."
sudo cp $SERVICE_FILE $SERVICE_PATH

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start $SERVICE_FILE

echo "Service status:"
sudo systemctl status $SERVICE_FILE --no-pager
