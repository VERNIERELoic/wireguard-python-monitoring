#!/bin/bash

SERVICE_NAME="wireguard"

SCRIPT_PATH="/home/ubuntu/wireguard-python-monitoring/wireguard-monitoring.py"
WORKING_DIR="/home/ubuntu/"
PYTHON_PATH="/usr/bin/python3"

USER_NAME="ubuntu"

SERVICE_FILE_CONTENT="[Unit]
Description=WireGuard Monitoring Service
After=network.target

[Service]
ExecStart=$PYTHON_PATH $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER_NAME
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"

# Create the systemd service file
SERVICE_FILE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
echo "Creating the systemd service file at $SERVICE_FILE_PATH"
echo "$SERVICE_FILE_CONTENT" | sudo tee $SERVICE_FILE_PATH

# Reload systemd to recognize the new service
echo "Reloading systemd"
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling the service $SERVICE_NAME"
sudo systemctl enable $SERVICE_NAME.service

# Start the service
echo "Starting the service $SERVICE_NAME"
sudo systemctl start $SERVICE_NAME.service

# Display the status of the service
echo "Status of the service $SERVICE_NAME:"
sudo systemctl status $SERVICE_NAME.service
