from dotenv import load_dotenv
import os
import sys

# Add the current directory to the path so Python can find the app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_env_vars = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'ANTHROPIC_API_KEY',
    'PORTIA_API_KEY'
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please create a .env file with these variables or set them in your environment.")
    sys.exit(1)

# Import and create the Flask app
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))