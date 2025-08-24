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
        
        # Update pip first
        python -m pip install --upgrade pip
        
        # Try installing packages
        if pip install -r requirements.txt --no-cache-dir; then
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

# Make sure we're using Python 3.11
if command -v python3.11 &> /dev/null; then
    echo "Using Python 3.11"
    python3.11 -m pip install --upgrade pip
else
    echo "Using default Python"
    python -m pip install --upgrade pip
fi

# Install packages with retry logic
install_requirements