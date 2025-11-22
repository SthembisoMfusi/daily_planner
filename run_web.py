import flet as ft
from app.gui import main
from app.database import init_db
import os

if __name__ == "__main__":
    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
    # Run Flet app in web mode
    print("Starting Flet app on http://localhost:8550")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
