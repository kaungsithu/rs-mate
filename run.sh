#!/bin/bash

# PostgreSQL User and Group Management App
# This script runs a web application for managing PostgreSQL database users and groups

# Default values
DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="0.0.0.0"
DB_PORT="5432"
APP_PORT="50798"

echo "PostgreSQL User and Group Management App"
echo "----------------------------------------"
echo "This application requires superuser privileges to manage PostgreSQL users and groups."
echo "Please provide PostgreSQL connection details:"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dbname)
      DB_NAME="$2"
      shift 2
      ;;
    --user)
      DB_USER="$2"
      shift 2
      ;;
    --password)
      DB_PASSWORD="$2"
      shift 2
      ;;
    --host)
      DB_HOST="$2"
      shift 2
      ;;
    --port)
      DB_PORT="$2"
      shift 2
      ;;
    --app-port)
      APP_PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Connecting to PostgreSQL database: $DB_NAME on $DB_HOST:$DB_PORT as $DB_USER"
echo "Starting web application on port: $APP_PORT"
echo "----------------------------------------"

# Run the application
python app.py --dbname "$DB_NAME" --user "$DB_USER" --password "$DB_PASSWORD" --host "$DB_HOST" --port "$DB_PORT" --app-port "$APP_PORT"