#!/usr/bin/env bash
# exit on error
set -o errexit

# Install uv if not available (Render uses pip usually)
# But since we have requirements.txt, we can just use pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
