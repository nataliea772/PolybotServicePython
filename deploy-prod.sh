#!/bin/bash
set -e

echo "Updating source code..."
cd /home/ubuntu/polybot
git checkout main
git pull origin main

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Restarting the prod service..."
sudo systemctl daemon-reexec
sudo systemctl restart polybot-prod.service
