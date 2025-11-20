import flet as ft
from app.gui import main
from app.database import init_db

if __name__ == "__main__":
    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
    # Run Flet app
    ft.app(target=main)
