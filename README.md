➜ kyusa git:(master) ✗ uv run django-admin startproject config .
➜ kyusa git:(master) ✗ uv run python manage.py check
➜ kyusa git:(master) ✗ uv run python manage.py migrate
➜ kyusa git:(master) ✗ uv run python manage.py createsuperuser
➜ kyusa git:(master) ✗ uv run python manage.py createuser

uv run python manage.py collectstatic --noinput
uv run python manage.py startapp core
➜ kyusa git:(master) ✗ openssl rand -hex 32

uv run python -m uvicorn api:app --reload --port 8000
uv run uvicorn api:app --reload --port 8001
uv run python manage.py runserver

Admin: http://127.0.0.1:8000/admin
API: http://127.0.0.1:8001/api/health
API services: http://127.0.0.1:8001/api/services

GET /api/provider/availability – list availability for the logged-in provider.
POST /api/provider/availability – set weekly schedule (replaces existing).
POST /api/provider/availability/exceptions – add date-specific exceptions.
