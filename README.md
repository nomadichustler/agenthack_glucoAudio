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
- **AI-powered**: Uses advanced machine learning models for accurate analysis

## Technical Stack

### Backend
- **Framework**: Flask (Async) with Gunicorn + Gevent workers
- **Database**: Supabase with custom authentication
- **AI/ML**: 
  - Claude API for biomarker analysis
  - Transformers for voice processing
  - PyTorch (CPU) for model inference
- **Voice**: 
  - Librosa for audio processing
  - ElevenLabs for voice synthesis
- **Agent System**: Portia SDK for multi-agent orchestration

### Frontend
- **UI**: Modern responsive design with custom CSS
- **JavaScript**: Vanilla JS with Web Audio API
- **Visualization**: Dynamic charts for glucose trends
- **Real-time**: WebSocket support for live updates

## Getting Started

### Local Development

1. Clone the repo:
   ```bash
   git clone https://github.com/abhisheksonii/agenthacks.git
   cd glucoAudio
   ```

2. Set up your environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   - Copy `env.example` to `.env`
   - Fill in required API keys:
     ```
     SUPABASE_URL=your-supabase-url
     SUPABASE_ANON_KEY=your-supabase-key
     ANTHROPIC_API_KEY=your-anthropic-key
     ELEVENLABS_API_KEY=your-elevenlabs-key
     PORTIA_API_KEY=your-portia-key
     SECRET_KEY=your-secure-random-string
     ```

5. Set up database:
   - Use Supabase SQL Editor
   - Run schema from `database_schema_updated.sql`

6. Run the application:
   ```bash
   python app.py
   ```

7. Visit `http://localhost:5000`

### Production Deployment (Render)

1. Fork/clone the repository

2. In Render dashboard:
   - Create a new Web Service
   - Connect your repository
   - Select Python environment
   - Environment variables:
     - Set all API keys as mentioned above
     - Set `PYTHON_VERSION=3.11.0`

3. The deployment will use:
   - `build.sh` for dependency installation
   - `render.yaml` for service configuration
   - Gunicorn with gevent workers for production serving

## Project Structure

```
glucoAudio/
├── app/
│   ├── __init__.py              # App initialization
│   ├── config.py                # Configuration
│   ├── models/                  # Data models
│   │   ├── user.py             # User model
│   │   ├── prediction.py       # Glucose predictions
│   │   ├── feedback.py         # User feedback
│   │   └── voice_session.py    # Recording sessions
│   ├── agents/                  # Analysis agents
│   │   ├── audio_processor.py  # Voice processing
│   │   ├── claude_inference.py # AI analysis
│   │   └── voice_synthesis.py  # Response generation
│   ├── routes/                  # API endpoints
│   │   ├── api.py             # Core API routes
│   │   ├── auth.py            # Authentication
│   │   └── main.py            # Web routes
│   ├── services/               # Business logic
│   │   ├── anthropic_service.py # Claude integration
│   │   ├── elevenlabs_service.py # Voice synthesis
│   │   ├── supabase_service.py  # Database operations
│   │   └── user_service.py      # Auth service
│   ├── static/                 # Frontend assets
│   └── templates/              # HTML templates
├── app.py                      # Entry point
├── build.sh                    # Build script
├── render.yaml                 # Deployment config
├── requirements.txt            # Dependencies
└── README_AUTHENTICATION.md    # Auth details
```

## API Reference

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET/PUT /auth/profile` - Profile management
- `POST /auth/change-password` - Password change

### Core Features
- `POST /api/v1/questionnaire` - Health context submission
- `POST /api/v1/voice/upload` - Voice sample upload
- `POST /api/v1/analyze` - Voice analysis
- `GET /api/v1/results/<session_id>` - Analysis results
- `GET /api/v1/history` - User history
- `POST /api/v1/feedback` - User feedback submission

## Security & Privacy

- Custom authentication system with bcrypt password hashing
- Secure session management
- Row Level Security (RLS) in Supabase
- CSRF protection
- Encrypted data storage
- Optional data retention controls

For detailed authentication information, see [README_AUTHENTICATION.md](README_AUTHENTICATION.md).

## Important Notice

This is an experimental research technology and should not replace medical devices or professional advice. Always consult healthcare professionals for medical decisions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT Licensed - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the development team
- Check documentation in the repository