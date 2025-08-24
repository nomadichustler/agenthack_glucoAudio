import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the base URL
BASE_URL = "http://localhost:5000"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    # Registration data
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

def test_login(email, password):
    """Test user login"""
    print("\nTesting user login...")
    
    # Login data
    data = {
        "email": email,
        "password": password
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

if __name__ == "__main__":
    # Test registration
    reg_result = test_registration()
    
    # If registration was successful, test login
    if reg_result.get("success"):
        test_login("test@example.com", "password123")
    else:
        # If registration failed because the user already exists, test login anyway
        test_login("test@example.com", "password123")
