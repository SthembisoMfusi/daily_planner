"""
Daily Planner Application Entry Point.

This script initializes the database and starts the Flet GUI application.
"""
import flet as ft
from app.gui import main
from app.database import init_db

if __name__ == "__main__":
    """
    Main execution block.
    
    1. Initializes the PostgreSQL database connection and tables.
    2. Starts the Flet desktop application loop.
    """
    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
    # Run Flet app
    ft.run(main)
