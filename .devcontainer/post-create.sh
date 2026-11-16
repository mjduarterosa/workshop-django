#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment ready. Run: python manage.py runserver 0.0.0.0:8000"