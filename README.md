# Moviemind API

FastAPI backend for the Moviemind film recommendation platform.

## Features

- 🎬 Movie catalog with filtering, sorting, and search
- 🔍 Cosine similarity-based recommendations
- ❤️ User favorites management
- 🚫 "Not interested" filtering
- 📝 Data error feedback system
- 🔐 Supabase authentication

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database + Auth
- **NumPy** - Cosine similarity calculations
- **Pydantic** - Data validation
- **pytest** - Testing framework

## Project Structure

```
moviemind.api/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Supabase client
│   ├── dependencies.py      # Auth dependencies
│   ├── schemas.py           # Pydantic models
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── movies.py        # Movie endpoints
│   │   ├── preferences.py   # Favorites/Not-interested
│   │   └── feedback.py      # Data error reports
│   └── services/
│       ├── movie_service.py      # Movie + recommendations
│       ├── auth_service.py       # Auth logic
│       ├── preference_service.py # User preferences
│       └── feedback_service.py   # Feedback handling
├── sql/                     # SQL scripts for Supabase
├── tests/                   # pytest tests
├── Dockerfile              # Railway deployment
└── requirements.txt
```

## Setup

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit with your Supabase credentials
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run SQL scripts** in Supabase SQL Editor:
   - `sql/01_create_tables.sql`
   - `sql/02_enable_rls.sql`
   - `sql/03_create_indexes.sql`

4. **Run locally:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Open API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Current user

### Movies
- `GET /api/movies` - List movies (paginated, filterable)
- `GET /api/movies/search?q=` - Search movies
- `GET /api/movies/{id}` - Movie details
- `GET /api/movies/{id}/recommendations` - Similar movies
- `GET /api/movies/genres` - Available genres
- `GET /api/movies/decades` - Available decades

### User Preferences
- `GET /api/favorites` - List favorites
- `POST /api/favorites` - Add favorite
- `DELETE /api/favorites/{movie_id}` - Remove favorite
- `GET /api/not-interested` - List not-interested
- `POST /api/not-interested` - Mark not-interested
- `DELETE /api/not-interested/{movie_id}` - Remove

### Feedback
- `POST /api/feedback` - Report data error

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Deployment (Railway)

1. Push code to a GitHub repository
2. Connect repository to Railway
3. Set environment variables in Railway dashboard
4. Railway will auto-build using `Dockerfile`
