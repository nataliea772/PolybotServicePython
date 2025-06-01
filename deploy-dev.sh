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

echo "Starting ngrok..."
# Kill any previous ngrok process
pkill ngrok || true

# Start ngrok in background
$PROJECT_DIR/ngrok http 8443 > /dev/null &
NGROK_PID=$!
echo "ngrok started with PID $NGROK_PID"

# Wait a bit to ensure ngrok is up
sleep 5

# Fetch the ngrok public URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
if [ -z "$NGROK_URL" ]; then
  echo "Error: Could not retrieve ngrok URL."
  exit 1
fi

echo "ngrok public URL is: $NGROK_URL"

# Set Telegram webhook
export $(cat .env | xargs)
BOT_TOKEN=$TELEGRAM_BOT_TOKEN
WEBHOOK_URL="$NGROK_URL/$BOT_TOKEN"

echo "Setting Telegram webhook to: $WEBHOOK_URL"
curl -s -X POST https://api.telegram.org/bot$BOT_TOKEN/setWebhook -d "url=$WEBHOOK_URL"

echo "Copying service file..."
sudo cp $SERVICE_FILE $SERVICE_PATH

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start $SERVICE_FILE

echo "Service status:"
sudo systemctl status $SERVICE_FILE --no-pager