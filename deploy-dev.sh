#!/bin/bash

APP_NAME=polybot
SERVICE_FILE=polybot-dev.service
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
REPO_PATH="/home/ubuntu/PolybotServicePython"
VENV_PATH="$REPO_PATH/.venv"

echo "Stopping existing service..."
sudo systemctl stop $SERVICE_FILE || true

echo "Pulling latest code from GitHub..."
cd $REPO_PATH || exit 1
git pull origin dev

echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv $VENV_PATH
fi

echo "Activating venv..."
source $VENV_PATH/bin/activate

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r polybot/requirements.txt

echo "Writing service file..."
cat <<EOF | sudo tee $SERVICE_PATH > /dev/null
[Unit]
Description=Polybot Dev Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$REPO_PATH
EnvironmentFile=$REPO_PATH/.env
ExecStart=$VENV_PATH/bin/python3 -m polybot.app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting service..."
sudo systemctl enable $SERVICE_FILE
sudo systemctl start $SERVICE_FILE

echo "Service status:"
sudo systemctl status $SERVICE_FILE --no-pager
