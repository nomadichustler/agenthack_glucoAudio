# glucoAudio

A breakthrough application for non-invasive glucose monitoring using voice analysis.

## What is glucoAudio?

glucoAudio is a research project exploring how voice biomarkers might correlate with blood glucose levels. By analyzing subtle changes in voice patterns, the system attempts to estimate glucose levels without the need for traditional invasive methods.

The app uses a multi-agent system built on the Portia SDK to process voice recordings and provide users with glucose estimates and personalized insights.

## Why It Matters

- **Pain-free monitoring**: No more finger pricks or test strips
- **Cost-effective**: Reduces ongoing expenses of traditional monitoring supplies
- **Accessible**: Works on standard smartphones with internet connection
- **Privacy-first**: User data is securely handled with optional cloud storage

## Technical Foundation

- Flask-based Python backend
- Supabase for database storage
- Custom authentication with password hashing
- Claude API for advanced biomarker analysis
- ElevenLabs for voice response synthesis
- Modern responsive frontend with real-time visualizations

## Getting Started

1. Clone the repo:
   ```
   git clone https://github.com/abhisheksonii/agenthacks.git
   cd glucoAudio
   ```

2. Set up your environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # OR
   source venv/bin/activate  # On Unix/macOS
   ```

3. Install what you need:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   # Run the database schema SQL file in your Supabase project
   # You can copy and paste the contents of database_schema_updated.sql
   # into the Supabase SQL Editor
   ```

5. Configure your environment:
   - Create a `.env` file with your API keys:
     - SUPABASE_URL and SUPABASE_ANON_KEY
     - ANTHROPIC_API_KEY
     - ELEVENLABS_API_KEY
     - PORTIA_API_KEY
     - SECRET_KEY (for Flask sessions)

6. Launch the app:
   ```
   python app.py
   ```

7. Visit `http://localhost:5000` in your browser

## Project Layout

```
glucoAudio/
├── app/
│   ├── __init__.py              # App initialization
│   ├── config.py                # Configuration
│   ├── models/                  # Data models
│   ├── agents/                  # Analysis agents
│   ├── routes/                  # API endpoints
│   ├── services/                # Core services
│   │   ├── user_service.py      # Custom authentication
│   │   └── ...                  # Other services
│   ├── static/                  # Frontend assets
│   └── templates/               # HTML templates
├── app.py                       # Entry point
├── database_schema_updated.sql  # Database schema with custom auth
├── README_AUTHENTICATION.md     # Authentication documentation
└── requirements.txt             # Dependencies
```

## Authentication

This project uses a custom authentication system that:
- Stores user credentials in the Supabase database
- Uses bcrypt for secure password hashing
- Manages sessions with Flask's session system

For more details, see [README_AUTHENTICATION.md](README_AUTHENTICATION.md).

## API Reference

- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/profile` - Profile management
- `/auth/change-password` - Password change
- `/api/v1/questionnaire` - Health context submission
- `/api/v1/voice/upload` - Voice sample upload
- `/api/v1/analyze` - Voice analysis
- `/api/v1/results/<session_id>` - Analysis results
- `/api/v1/history` - User history
- `/api/v1/feedback` - User feedback submission

## Important Note

This is an experimental research technology and should not replace medical devices or professional advice. Always consult healthcare professionals for medical decisions.

## License

MIT Licensed - See LICENSE file for details.