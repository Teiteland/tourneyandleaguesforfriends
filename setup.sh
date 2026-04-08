#!/bin/bash
# Setup script for Gaming Tournament & League System

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Initializing database migrations..."
flask db init

echo "Creating initial migration..."
flask db migrate -m "Initial migration"

echo "Applying migrations..."
flask db upgrade

echo "Seeding test data..."
flask seed-data

echo "Done! Run 'flask run' to start the server."
