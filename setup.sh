#!/bin/bash
# Setup script for Gaming Tournament & League System

echo "Setting up database..."
flask init-db

echo "Seeding test data..."
flask seed-data

echo "Done! Run 'flask run' to start the server."