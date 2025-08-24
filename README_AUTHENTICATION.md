# Custom Authentication for glucoAudio

This document explains how to set up and use the custom authentication system for glucoAudio.

## Overview

Instead of using Supabase's built-in authentication, this application implements a custom authentication system that:

1. Stores user credentials directly in the Supabase database
2. Uses bcrypt for secure password hashing
3. Maintains session state using Flask sessions

## Database Setup

1. Run the updated database schema SQL file to create the necessary tables:

```bash
psql -U your_postgres_user -d your_database_name -f database_schema_updated.sql
```

Or copy and paste the SQL commands from `database_schema_updated.sql` into the Supabase SQL Editor.

### Key Changes from Original Schema

- Created a custom `users` table with email and password_hash fields
- Modified foreign key references to point to the new users table
- Added password hashing and verification functions
- Updated Row Level Security (RLS) policies to work with the custom authentication

## Environment Variables

Make sure your `.env` file includes:

```
# Supabase Configuration
SUPABASE_URL="your-supabase-url"
SUPABASE_ANON_KEY="your-supabase-anon-key"

# API Keys
ANTHROPIC_API_KEY="your-anthropic-api-key"
ELEVENLABS_API_KEY="your-elevenlabs-api-key"
PORTIA_API_KEY="your-portia-api-key"

# Flask Configuration
SECRET_KEY="your-secure-random-string-for-flask-sessions"
PORT=5000

# Environment (development, testing, production)
FLASK_ENV="development"
```

The `SECRET_KEY` is particularly important as it's used to encrypt session data.

## Authentication Flow

### Registration

1. User submits email and password via the registration form
2. The password is hashed using bcrypt
3. A new user record is created in the `users` table
4. A corresponding profile record is created in the `profiles` table
5. User is logged in automatically (session is created)

### Login

1. User submits email and password via the login form
2. The system retrieves the user record by email
3. The password is verified against the stored hash using bcrypt
4. If successful, user data is stored in the session
5. The last_login timestamp is updated

### Session Management

- User ID and email are stored in Flask's session
- Session data is encrypted using the SECRET_KEY
- Sessions expire when the browser is closed (default behavior)
- The `/auth/logout` route clears the session

## Security Considerations

- Passwords are hashed using bcrypt with a cost factor of 12
- SQL injection is prevented by using parameterized queries
- CSRF protection is provided by Flask's built-in mechanisms
- Session data is encrypted
- Row Level Security (RLS) policies restrict data access

## API Endpoints

### Authentication

- `POST /auth/register`: Register a new user
- `POST /auth/login`: Log in an existing user
- `POST /auth/logout`: Log out the current user
- `GET/PUT /auth/profile`: Get or update user profile
- `POST /auth/change-password`: Change user password

### Data Access

All API endpoints now check for authentication using Flask sessions. The user ID is retrieved from:

1. The session (`session.get('user_id')`)
2. Request parameters (as a fallback)

## Testing

To test the authentication system:

1. Register a new user via the registration form or API
2. Log in with the registered credentials
3. Access protected routes (should succeed)
4. Log out
5. Try accessing protected routes again (should fail)

## Troubleshooting

- **Login Fails**: Check that the user exists in the database and the password is correct
- **Session Not Persisting**: Ensure the SECRET_KEY is set correctly
- **Database Access Issues**: Verify that RLS policies are correctly configured
- **Password Hashing Errors**: Make sure bcrypt is installed and working properly
