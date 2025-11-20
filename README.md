# Daily Planner App

A modern, terminal-based (soon to be GUI) daily planner application for logging mentorship sessions.

## Setup

1. **Prerequisites**:
   - Python 3.8+
   - PostgreSQL

2. **Installation**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Configuration**:
   - Create a PostgreSQL database named `daily_planner`.
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your database credentials:
     ```
     DATABASE_URL=postgresql://user:password@localhost:5432/daily_planner
     ```
     *Note: If using a Unix socket, use the format: `postgresql://user:password@/daily_planner?host=/run/postgresql`*

4. **Running the App**:
   ```bash
   python main.py
   ```

## Features
- **Calendar View**: Navigate months and select days.
- **Session Logging**: Log group sessions with categories and duration.
- **Excel Export**: Export data to Excel (saved in `exports/` folder).
