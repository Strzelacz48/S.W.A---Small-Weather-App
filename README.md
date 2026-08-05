# S.W.A — Small Weather App

A contact management app built with Django, made as a recruitment exercise
for the Junior Fullstack Developer position at Supra Brokers S.A. Contacts
can be searched, added, edited, deleted, imported/exported as CSV, and each
one shows live weather for its city.

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
automatically on every startup — including a data migration that seeds four
default contact statuses (New, In Progress, Lost, Outdated), so there's
nothing to set up manually before adding contacts.

To access the admin panel at <http://localhost:8000/admin/>, create a
superuser in a second terminal while the containers are running:

```bash
docker compose exec web python manage.py createsuperuser
```

### Option B: Local (without Docker)

Requires Python 3.12 and [Poetry](https://python-poetry.org/).

```bash
git clone git@github.com:Strzelacz48/S.W.A---Small-Weather-App.git
cd S.W.A---Small-Weather-App
cp .env.example .env
poetry install
poetry run python manage.py migrate
poetry run python manage.py createsuperuser  # optional, for /admin/
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

### Running tests

```bash
poetry run pytest
```

## Usage

- **Contact list** — <http://localhost:8000/> — search-free list view with
  add/edit/delete, CSV import/export, sorting by last name or date added,
  and per-contact weather.
- **Admin panel** — <http://localhost:8000/admin/> — manage contacts and
  contact statuses directly (requires a superuser, see Setup above).
- **REST API** — `/api/contacts/` — `GET`/`POST`/`PUT`/`DELETE`, browsable
  in a regular browser at that URL.

## Approach

I used Poetry to manage dependencies instead of a plain `requirements.txt`
file, mainly to get some practice with it and keep things organized.

Contact statuses (New, In Progress, etc.) are their own model instead of
being hardcoded in Python, so they can be added or renamed from the admin
panel without touching the code, like the brief asked for.

For weather, I first look up the city's coordinates using Nominatim and
save them to the database, so the same city never has to be looked up
twice. Then I fetch the actual weather from Open-Meteo and cache it for 45
minutes so the app isn't hitting those APIs on every single page load. The
weather loads in with a small JavaScript request after the page itself has
already loaded, so the contact list doesn't feel slow while it waits on an
external API.

Forms are validated in two places: JavaScript checks things like email
format and phone length before you're even allowed to submit, but Django
also checks everything again on the server (including that phone/email
aren't already used), in case JavaScript is off or someone sends a request
straight to the server.

CSV import and export use the exact same columns, so exporting your
contacts and importing that same file back in works without errors. When
importing, each row goes through the same validation as the normal "Add
Contact" form, so if one row is bad (bad email, duplicate, unknown status)
it just gets skipped with a reason instead of failing the whole file.

The icons are just SVGs copied from Tabler Icons (they're free/MIT
licensed), loaded through a small custom template tag I made so I can
write `{% icon "name" %}` instead of pasting the whole SVG every time I
need one.

## Extra features I added on top of the requirements

- Docker + docker-compose setup (Postgres + the app in one command).
- Weather caching, so it doesn't spam the weather API on every page load.
- CSV export, on top of the required import.
- A few automated tests (`poetry run pytest`) for the model constraints,
  the list view/sorting, and the API.
- A confirmation modal before deleting a contact, instead of just deleting
  right away.

## Known limitations

- There's no login system, so all contacts are shared and visible to
  anyone who has access to the app. This was one of the optional bonus
  tasks in the brief and I didn't get to it.
- The weather column needs internet access to
  `nominatim.openstreetmap.org` and `api.open-meteo.com`. If a city can't
  be found or the network is down, that row just shows "Unavailable"
  instead of breaking the whole page.
