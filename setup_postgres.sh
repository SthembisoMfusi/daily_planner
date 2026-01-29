#!/bin/bash
set -e

echo "Installing PostgreSQL..."
# Install PostgreSQL and contrib package
apt-get update
apt-get install -y postgresql postgresql-contrib libpq-dev

# Start and enable the service
echo "Starting PostgreSQL service..."
systemctl start postgresql
systemctl enable postgresql

# Create User and Database
echo "Configuring Database..."
# check if user exists, if not create
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='daily_planner'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER daily_planner WITH PASSWORD 'daily_planner';"

# check if db exists, if not create
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='daily_planner'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE daily_planner OWNER daily_planner;"

# Grant privileges (optional but good)
sudo -u postgres psql -c "ALTER USER daily_planner CREATEDB;"

echo "------------------------------------------------"
echo "PostgreSQL setup complete!"
echo "Database: daily_planner"
echo "User:     daily_planner"
echo "Password: daily_planner"
echo "------------------------------------------------"
echo "Please update your .env file with:"
echo "DATABASE_URL=postgresql://daily_planner:daily_planner@localhost:5432/daily_planner"
