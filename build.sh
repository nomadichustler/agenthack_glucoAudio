#!/usr/bin/env bash
set -e

# Maximum number of retries
MAX_RETRIES=3
RETRY_DELAY=5

# Function to install requirements with retry logic
install_requirements() {
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "Attempt $attempt of $MAX_RETRIES: Installing Python packages..."
        if pip install -r requirements.txt; then
            echo "Package installation successful!"
            return 0
        fi
        echo "Package installation failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
    echo "Failed to install packages after $MAX_RETRIES attempts"
    return 1
}

# Ensure pip is up to date
python -m pip install --upgrade pip

# Install packages with retry logic
install_requirements
