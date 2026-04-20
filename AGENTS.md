# Hammarby Supporterklubb - Agent Instructions

## Quick Start

```bash
# Setup (auto-creates venv, installs deps, configures env)
./start.sh

# Run tests
pytest -v

# Run with coverage
pytest --cov=backend --cov-report=term-missing

# Start dev server
source venv/bin/activate && python backend/app.py
```

## Architecture

- **Flask app factory**: `backend/app:create_app()` - use this for gunicorn/production
- **Routes**: Single blueprint in `backend/routes/__init__.py` (all routes defined here)
- **Models**: `backend/models.py` - User model with JSON file storage (not database)
- **Data storage**: News stored as JSON files in `backend/data/news/nyhet_XXXX.json`
- **Templates**: `frontend/templates/` - app uses relative path `../frontend/templates`
- **Static files**: `frontend/static/` - app uses relative path `../frontend/static`

## Key Commands

| Task | Command |
|------|---------|
| Run all tests | `pytest -v` |
| Run single test file | `pytest tests/test_authentication.py -v` |
| Run single test | `pytest tests/test_pages.py::TestHomePage::test_home_page_loads -v` |
| Run failed tests only | `pytest --lf` |
| Coverage report | `pytest --cov=backend --cov-report=html` |
| Start dev server | `python backend/app.py` |
| Production server | `gunicorn --bind 0.0.0.0:5000 --workers 4 backend.app:create_app()` |
| Stop server | `./stop.sh` |

## Testing Notes

- Tests use fixtures in `tests/conftest.py` - available: `app`, `client`, `test_user`, `test_news_data`, `test_image`
- `test_user` fixture creates admin user: username=`testuser`, password=`TestPassword123!`
- Image upload test limit is **10KB** (code says 100MB but tests expect 10KB)
- Session timeout is 30 minutes (configurable via `PERMANENT_SESSION_LIFETIME`)
- Max file upload is 16MB (per `MAX_CONTENT_LENGTH` in app.py)

## Authentication

- Login route: `/admin/login` (POST with `username` and `password` fields)
- Logout route: `/admin/logout`
- Admin decorator: `@admin_required` checks `current_user.role == 'admin'`
- Passwords hashed with bcrypt in `User` model
- User data stored in `backend/data/users.json`

## News System

- News files: `backend/data/news/nyhet_XXXX.json` (zero-padded 4-digit IDs)
- News content stored as Quill Delta JSON format
- Categories: `allmänt`, `sport`, `medlemmar`, `stipendium`
- CRUD routes: `/admin/news/create`, `/admin/news/<id>/edit`, `/admin/news/<id>/delete`

## Image Upload

- Upload route: `/admin/news/upload` (POST with `image` field)
- Allowed extensions: `jpg`, `jpeg`, `png`, `gif`, `webp` (not `bmp`)
- Images resized to max 1920x1080, saved as JPEG with quality=85
- Unique filenames use UUID: `{original_name}_{uuid}.jpg`
- Upload folder: `backend/uploads/`

## Branding

- **Hammarby green**: `#00833e` (primary), `#1f561c` (dark variant)
- Club motto: "Första och främsta!"

## Environment Variables

Set in `.env` (created by `./start.sh`):
- `SECRET_KEY` - **Must change in production**
- `FLASK_ENV` - `development` or `production`
- `FLASK_DEBUG` - `1` or `0`
- `PORT` - Default `5000`

## HAProxy/Proxy

- `ProxyFix` already configured in `app.py` for production behind reverse proxy
- Handles `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Forwarded-Prefix`

## Common Gotchas

1. **Template paths**: Use `../frontend/templates` relative to `backend/app.py`
2. **News ID generation**: Uses `max(existing_ids) + 1` from JSON files
3. **Quill Delta**: News content may be stored as ops array or escaped JSON string - code handles both
4. **Test file size limit**: Upload tests expect 10KB limit, not 16MB from config
5. **User model**: Uses JSON file storage, not SQLAlchemy database
