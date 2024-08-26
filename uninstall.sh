#!/bin/bash

SERVICE_NAME="wireguard-monitoring"

# Stop the service
echo "Stopping the service $SERVICE_NAME"
sudo systemctl stop $SERVICE_NAME.service

# Disable the service to prevent it from starting on boot
echo "Disabling the service $SERVICE_NAME"
sudo systemctl disable $SERVICE_NAME.service

# Remove the systemd service file
SERVICE_FILE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
echo "Removing the service file $SERVICE_FILE_PATH"
sudo rm -f $SERVICE_FILE_PATH

# Reload systemd to apply the changes
echo "Reloading systemd"
sudo systemctl daemon-reload

# Check if the service has been successfully removed
if systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
    echo "Failed to remove $SERVICE_NAME.service"
else
    echo "$SERVICE_NAME.service has been successfully removed"
fi
