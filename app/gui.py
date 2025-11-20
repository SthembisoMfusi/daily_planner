import flet as ft
from datetime import date, timedelta, datetime
from app.database import get_db, get_sessions_for_day, add_mentorship_session
from app.config import SESSION_CATEGORIES
from app.export import export_to_excel

def main(page: ft.Page):
    """
    Main entry point for the Flet GUI.
    """
    page.title = "Daily Planner"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1000
    page.window_height = 800

    # State
    current_month = date.today().replace(day=1)
    
    # Components
    calendar_grid = ft.GridView(
        expand=True,
        runs_count=7,
        max_extent=120,
        child_aspect_ratio=1.0,
        spacing=10,
        run_spacing=10,
    )
    
    month_label = ft.Text(
        value="", 
        size=24, 
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    def get_days_in_month(d: date):
        next_month = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        return (next_month - d).days

    def update_calendar():
        month_label.value = current_month.strftime("%B %Y")
        calendar_grid.controls.clear()
        
        # Weekday headers
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in weekdays:
            calendar_grid.controls.append(
                ft.Container(
                    content=ft.Text(day, color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center
                )
            )
        
        # Empty slots
        start_weekday = current_month.weekday()
        for _ in range(start_weekday):
            calendar_grid.controls.append(ft.Container())
            
        # Days
        days_in_month = get_days_in_month(current_month)
        db = next(get_db())
        
        for d in range(1, days_in_month + 1):
            day_date = current_month.replace(day=d)
            sessions = get_sessions_for_day(db, day_date)
            is_logged = len(sessions) > 0
            
            btn_style = ft.ButtonStyle(
                bgcolor=ft.colors.GREEN_900 if is_logged else ft.colors.SURFACE_VARIANT,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            )
            
            calendar_grid.controls.append(
                ft.ElevatedButton(
                    text=str(d),
                    style=btn_style,
                    on_click=lambda e, date=day_date: open_day_view(date)
                )
            )
        
        page.update()

    def change_month(delta):
        nonlocal current_month
        if delta > 0:
            current_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            current_month = (current_month.replace(day=1) - timedelta(days=1)).replace(day=1)
        update_calendar()

    def open_day_view(day_date):
        # Form Controls
        group_input = ft.TextField(label="Group Number or Name", expand=True)
        category_dropdown = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option(c) for c in SESSION_CATEGORIES],
            expand=True
        )
        activity_input = ft.TextField(label="Activity Description", multiline=True, min_lines=2)
        hours_input = ft.TextField(label="Hours", value="0", width=100)
        minutes_input = ft.TextField(label="Minutes", value="0", width=100)
        
        session_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)

        def refresh_sessions():
            session_list.controls.clear()
            db = next(get_db())
            sessions = get_sessions_for_day(db, day_date)
            for s in sessions:
                session_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{s.group_name} - {s.category}"),
                        subtitle=ft.Text(f"{s.activity_description}\nDuration: {s.duration_hours}h {s.duration_minutes}m"),
                        leading=ft.Icon(ft.icons.EVENT_NOTE),
                    )
                )
            page.update()

        def log_session(e):
            if not group_input.value or not category_dropdown.value:
                page.snack_bar = ft.SnackBar(ft.Text("Please fill in Group and Category"))
                page.snack_bar.open = True
                page.update()
                return

            try:
                h = int(hours_input.value)
                m = int(minutes_input.value)
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Duration must be numbers"))
                page.snack_bar.open = True
                page.update()
                return

            db = next(get_db())
            add_mentorship_session(
                db, day_date, 
                group_input.value, 
                category_dropdown.value, 
                activity_input.value, 
                h, m
            )
            
            # Clear inputs
            group_input.value = ""
            activity_input.value = ""
            hours_input.value = "0"
            minutes_input.value = "0"
            
            refresh_sessions()
            update_calendar() # Update main calendar to show green status
            page.snack_bar = ft.SnackBar(ft.Text("Session Logged!"))
            page.snack_bar.open = True
            page.update()

        refresh_sessions()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Sessions for {day_date.strftime('%A, %B %d')}"),
            content=ft.Column(
                width=500,
                controls=[
                    session_list,
                    ft.Divider(),
                    ft.Text("Log New Session", weight=ft.FontWeight.BOLD),
                    ft.Row([group_input, category_dropdown]),
                    activity_input,
                    ft.Row([hours_input, minutes_input]),
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.close(dlg)),
                ft.ElevatedButton("Log Session", on_click=log_session, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE),
            ],
        )
        page.open(dlg)

    def open_export_dialog(e):
        weeks_input = ft.TextField(label="Number of Weeks", value="1", width=100)
        
        def export_action(e):
            try:
                weeks = int(weeks_input.value)
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Invalid number of weeks"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Export starting from current month view (first day)
            # Or maybe just "From Today"? Let's do "From Today" for simplicity as requested "how many weeks"
            # But user might want past data.
            # Let's assume "From the start of the currently viewed month" is a good default, 
            # or just "All data" if we don't filter. 
            # The user asked "choose how many weeks they want to make an excel file for".
            # Implicitly this implies "recent" or "upcoming". 
            # Let's use the `current_month` as the start date.
            
            success, msg = export_to_excel(start_date=current_month, num_weeks=weeks)
            
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
            page.close(dlg)
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Export to Excel"),
            content=ft.Column(
                height=100,
                controls=[
                    ft.Text(f"Exporting starting from {current_month.strftime('%B %Y')}"),
                    weeks_input
                ]
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                ft.ElevatedButton("Export", on_click=export_action, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE),
            ],
        )
        page.open(dlg)

    # Layout
    header = ft.Row(
        controls=[
            ft.IconButton(ft.icons.CHEVRON_LEFT, on_click=lambda e: change_month(-1)),
            month_label,
            ft.IconButton(ft.icons.CHEVRON_RIGHT, on_click=lambda e: change_month(1)),
            ft.Container(expand=True), # Spacer
            ft.ElevatedButton("Export", icon=ft.icons.DOWNLOAD, on_click=open_export_dialog, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(
        ft.Column(
            controls=[
                header,
                ft.Divider(),
                calendar_grid
            ],
            expand=True
        )
    )

    update_calendar()
