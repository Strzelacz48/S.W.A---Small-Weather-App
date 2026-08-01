# S.W.A---Small-Weather-App

This is an app made as an recruitment exercise for Junior Fullstack Developer position at Supra Brokers S.A.

## Setup

### Option A: Docker (recommended)

Requires Docker and Docker Compose.

```bash
git clone git@github.com:Strzelacz48/S.W.A---Small-Weather-App.git
cd S.W.A---Small-Weather-App
cp .env.example .env
docker compose up --build
```

The app will be available at <http://localhost:8000/>. This starts a Postgres
database alongside the app, waits for it to be ready, and runs migrations
automatically on every startup.

### Option B: Local (without Docker)

Requires Python 3.12 and [Poetry](https://python-poetry.org/).

```bash
git clone git@github.com:Strzelacz48/S.W.A---Small-Weather-App.git
cd S.W.A---Small-Weather-App
cp .env.example .env
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Without a `DATABASE_URL` in `.env`, this falls back to a local SQLite
database (`db.sqlite3`) instead of Postgres.

### Environment variables

Copy `.env.example` to `.env` and adjust as needed. `DJANGO_SECRET_KEY`
should be replaced with a real generated value for anything beyond local
testing:

```bash
poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
