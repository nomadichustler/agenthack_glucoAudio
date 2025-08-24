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
        
        # Install build dependencies first
        pip install --no-cache-dir wheel setuptools cython

        # Try installing packages
        if pip install --no-cache-dir -r requirements.txt; then
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

# Ensure we're using Python 3.11
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Update pip
python -m pip install --upgrade pip

# Install packages with retry logic
install_requirements