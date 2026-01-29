import flet as ft
from datetime import date, timedelta, datetime
from app.database import get_db, get_sessions_for_day, add_mentorship_session, update_mentorship_session
from app.config import SESSION_CATEGORIES
from app.export import export_to_excel

def main(page: ft.Page):
    """
    Main entry point for the Flet GUI application.

    Args:
        page (ft.Page): The Flet page instance used to render the UI.
    """
    page.title = "Daily Planner"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1000
    page.window_height = 800

    # State
    current_month = date.today().replace(day=1)
    
    # Components
    
    # Weekday Headers (Fixed at top)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(day, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD),
                alignment=ft.Alignment(0, 0),
                expand=True
            ) for day in weekdays
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY
    )
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

    def get_days_in_month(d: date) -> int:
        """
        Calculates the number of days in the month of the given date.

        Args:
            d (date): The date object containing the month and year to check.

        Returns:
            int: The number of days in the month.
        """
        next_month = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        return (next_month - d).days

    def update_calendar():
        """
        Refresh the calendar grid to show days for the current selected month.
        
        This function clears the current grid and repopulates it with:
        - Empty slots for days before the 1st of the month.
        - Buttons for each day of the month, colored green if sessions exist.
        """
        month_label.value = current_month.strftime("%B %Y")
        calendar_grid.controls.clear()
        
        # Empty slots for the start of the month
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
                bgcolor=ft.Colors.GREEN_900 if is_logged else ft.Colors.GREY_800,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            )
            
            calendar_grid.controls.append(
                ft.ElevatedButton(
                    str(d),
                    style=btn_style,
                    on_click=lambda e, date=day_date: open_day_view(date)
                )
            )
        
        page.update()

    def change_month(delta: int):
        """
        Changes the currently viewed month by a given delta.

        Args:
            delta (int): The number of months to move. +1 for next month, -1 for previous.
        """
        nonlocal current_month
        if delta > 0:
            current_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            current_month = (current_month.replace(day=1) - timedelta(days=1)).replace(day=1)
        update_calendar()

    def open_day_view(day_date: date):
        """
        Opens a dialog to view and log sessions for a specific date.

        Args:
            day_date (date): The date to view.
        """
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
        
        # Edit state
        editing_session_id = None
        log_button = ft.ElevatedButton("Log Session", on_click=lambda e: log_session(e), bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
        cancel_edit_btn = ft.TextButton("Cancel Edit", visible=False)

        def reset_form():
            nonlocal editing_session_id
            editing_session_id = None
            group_input.value = ""
            category_dropdown.value = None
            activity_input.value = ""
            hours_input.value = "0"
            minutes_input.value = "0"
            log_button.text = "Log Session"
            log_button.bgcolor = ft.Colors.GREEN_600
            cancel_edit_btn.visible = False
            page.update()

        def load_session_for_edit(session):
            nonlocal editing_session_id
            editing_session_id = session.id
            group_input.value = session.group_name
            category_dropdown.value = session.category
            activity_input.value = session.activity_description
            hours_input.value = str(session.duration_hours)
            minutes_input.value = str(session.duration_minutes)
            
            log_button.text = "Update Session"
            log_button.bgcolor = ft.Colors.ORANGE_700
            cancel_edit_btn.visible = True
            cancel_edit_btn.on_click = lambda e: reset_form()
            page.update()

        def refresh_sessions():
            """
            Fetches sessions for the selected day from the database and updates the list in the dialog.
            """
            session_list.controls.clear()
            db = next(get_db())
            sessions = get_sessions_for_day(db, day_date)
            for s in sessions:
                session_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{s.group_name} - {s.category}"),
                        subtitle=ft.Text(f"{s.activity_description}\nDuration: {s.duration_hours}h {s.duration_minutes}m"),
                        leading=ft.Icon(ft.Icons.EVENT_NOTE),
                        trailing=ft.IconButton(
                            ft.Icons.EDIT, 
                            tooltip="Edit Session",
                            on_click=lambda e, session=s: load_session_for_edit(session)
                        )
                    )
                )
            page.update()

        def log_session(e):
            """
            Callback to log a new session when the 'Log Session' button is clicked.
            
            Validates input and saves the session to the database.
            """
            if not group_input.value or not category_dropdown.value:
                page.snack_bar = ft.SnackBar(ft.Text("Please fill in Group and Category"))
                page.snack_bar.open = True
                page.update()
                return

            try:
                hours_part = int(hours_input.value)
                mins_part = int(minutes_input.value)
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Duration must be numbers"))
                page.snack_bar.open = True
                page.update()
                return

            db = next(get_db())
            
            if editing_session_id:
                update_mentorship_session(
                    db, editing_session_id,
                    group_input.value, 
                    category_dropdown.value, 
                    activity_input.value, 
                    hours_part, mins_part
                )
                msg = "Session Updated!"
            else:
                add_mentorship_session(
                    db, day_date, 
                    group_input.value, 
                    category_dropdown.value, 
                    activity_input.value, 
                    hours_part, mins_part
                )
                msg = "Session Logged!"
            
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
            reset_form()
            refresh_sessions()
            update_calendar() # Update main calendar to show green status
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
                ft.TextButton("Close", on_click=lambda e: (setattr(dlg, 'open', False), page.update())),
                cancel_edit_btn,
                log_button,
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def open_export_dialog(e):
        """
        Opens a dialog to configure and perform data export to Excel.
        """
        # State for date pickers
        start_date_value = current_month
        end_date_value = date.today()

        start_date_text = ft.Text(start_date_value.strftime("%Y-%m-%d"))
        end_date_text = ft.Text(end_date_value.strftime("%Y-%m-%d"))

        def handle_start_change(e):
            nonlocal start_date_value
            if e.control.value:
                start_date_value = e.control.value.date()
                start_date_text.value = start_date_value.strftime("%Y-%m-%d")
                page.update()

        def handle_end_change(e):
            nonlocal end_date_value
            if e.control.value:
                end_date_value = e.control.value.date()
                end_date_text.value = end_date_value.strftime("%Y-%m-%d")
                page.update()

        start_picker = ft.DatePicker(
            on_change=handle_start_change,
            value=start_date_value,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        end_picker = ft.DatePicker(
            on_change=handle_end_change,
            value=end_date_value,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        
        # Register pickers
        page.overlay.append(start_picker)
        page.overlay.append(end_picker)

        def set_range(option):
            nonlocal start_date_value, end_date_value
            today = date.today()
            
            if option == "This Month":
                start_date_value = today.replace(day=1)
                end_date_value = today
            elif option == "Last Month":
                last_month_end = today.replace(day=1) - timedelta(days=1)
                start_date_value = last_month_end.replace(day=1)
                end_date_value = last_month_end
            elif option == "Last 3 Months":
                start_date_value = today - timedelta(days=90)
                end_date_value = today
            elif option == "All Time":
                start_date_value = date(2020, 1, 1)
                end_date_value = today
            
            # Update UI
            start_date_text.value = start_date_value.strftime("%Y-%m-%d")
            end_date_text.value = end_date_value.strftime("%Y-%m-%d")
            # For DatePicker, we don't set value directly like this if it is already open or attached
            # But here we are just updating internal state before opening
            # start_picker.value = start_date_value 
            # end_picker.value = end_date_value
            page.update()

        def export_action(e):
            # Determine if we should use separate sheets
            use_separate_sheets = True
            if (end_date_value - start_date_value).days > 7:
                use_separate_sheets = sheet_option.value == "separate"
            
            success, msg = export_to_excel(
                start_date=start_date_value, 
                end_date=end_date_value,
                separate_sheets=use_separate_sheets
            )
            
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
            dlg.open = False
            page.update()

        # Sheet option selector (only shown if date range > 7 days)
        sheet_option = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="separate", label="Separate sheets per week"),
                ft.Radio(value="single", label="Single sheet with all data")
            ]),
            value="separate"
        )

        # Calculate if we need to show the sheet option
        show_sheet_option = (end_date_value - start_date_value).days > 7

        dlg = ft.AlertDialog(
            title=ft.Text("Export to Excel"),
            content=ft.Column(
                height=400 if show_sheet_option else 300,
                width=400,
                controls=[
                    ft.Text("Select Date Range", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Column([
                            ft.Text("Start Date"),
                            ft.ElevatedButton(
                                "Pick Date",
                                icon=ft.Icons.CALENDAR_MONTH,
                                on_click=lambda _: (setattr(start_picker, "open", True), page.update())
                            ),
                            start_date_text
                        ]),
                        ft.Column([
                            ft.Text("End Date"),
                            ft.ElevatedButton(
                                "Pick Date",
                                icon=ft.Icons.CALENDAR_MONTH,
                                on_click=lambda _: (setattr(end_picker, "open", True), page.update())
                            ),
                            end_date_text
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Text("Quick Select", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        wrap=True,
                        spacing=10,
                        controls=[
                            ft.Chip(label=ft.Text("This Month"), on_click=lambda e: set_range("This Month")),
                            ft.Chip(label=ft.Text("Last Month"), on_click=lambda e: set_range("Last Month")),
                            ft.Chip(label=ft.Text("Last 3 Months"), on_click=lambda e: set_range("Last 3 Months")),
                            ft.Chip(label=ft.Text("All Time"), on_click=lambda e: set_range("All Time")),
                        ]
                    ),
                ] + ([ft.Divider(), ft.Text("Export Options", weight=ft.FontWeight.BOLD), sheet_option] if show_sheet_option else [])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (setattr(dlg, 'open', False), page.update())),
                ft.ElevatedButton("Export", on_click=export_action, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # Layout
    header = ft.Row(
        controls=[
            ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=lambda e: change_month(-1)),
            month_label,
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=lambda e: change_month(1)),
            ft.Container(expand=True), # Spacer
            ft.ElevatedButton("Export", icon=ft.Icons.DOWNLOAD, on_click=open_export_dialog, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(
        ft.Column(
            controls=[
                header,
                ft.Divider(),
                weekday_row,
                calendar_grid
            ],
            expand=True
        )
    )

    update_calendar()
