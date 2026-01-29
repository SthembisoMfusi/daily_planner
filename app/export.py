"""
Export module for the Daily Planner App.

Handles exporting mentorship sessions to Excel files.
"""
import os
import pandas as pd
from sqlalchemy.orm import Session, sessionmaker
from .database import get_engine, MentorshipSession, DayLog
from datetime import datetime, timedelta, date

def export_to_excel(start_date: date = None, end_date: date = None, filename: str = None, separate_sheets: bool = True) -> tuple[bool, str]:
    """
    Exports mentorship sessions from the database to an Excel file.

    This function queries the database for sessions within the specified date range 
    and writes them to an Excel file using pandas. It supports data retrieval for 
    specific periods and organizing the data into separate sheets by week.

    Args:
        start_date (date, optional): The start date for filtering sessions. 
                                     If None, includes sessions from the beginning of time. 
                                     Defaults to None.
        end_date (date, optional): The end date for filtering sessions (inclusive). 
                                   If None, checks up to the current date/last entry. 
                                   Defaults to None.
        filename (str, optional): The name of the output Excel file. 
                                  If None, a timestamped filename is generated 
                                  (e.g., "mentorship_log_YYYYMMDD_HHMMSS.xlsx"). 
                                  Defaults to None.
        separate_sheets (bool, optional): Configuration to split data into weekly sheets.
                                          - If True, creates a separate worksheet for each week.
                                          - If False, puts all data into a single "All Sessions" sheet.
                                          Defaults to True.

    Returns:
        tuple[bool, str]: A tuple containing:
                          - bool: True if the export was successful, False otherwise.
                          - str: A success message with the filepath or an error description.
    """
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    
    try:
        with SessionLocal() as db:
            query = db.query(
                DayLog.date,
                MentorshipSession.group_name,
                MentorshipSession.category,
                MentorshipSession.activity_description,
                MentorshipSession.duration_hours,
                MentorshipSession.duration_minutes
            ).join(MentorshipSession).order_by(DayLog.date)

            if start_date:
                query = query.filter(DayLog.date >= start_date)
            
            if end_date:
                # Inclusive of the end date
                query = query.filter(DayLog.date <= end_date)
            
            results = query.all()
    except Exception as e:
        return False, f"Database Error: {str(e)}"
    
    if not results:
        return False, "No data to export for the selected range."

    # Prepare data for DataFrame
    data = []
    for row in results:
        date_obj = row.date
        week_num = date_obj.isocalendar()[1]
        year = date_obj.year
        week_label = f"Week {week_num} - {year}"
        
        data.append({
            "Date": date_obj,
            "Week": week_label,
            "Group Name": row.group_name,
            "Category": row.category,
            "Activity": row.activity_description,
            "Duration": f"{row.duration_hours}h {row.duration_minutes}m"
        })
    
    df = pd.DataFrame(data)
    
    # Ensure exports directory exists
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mentorship_log_{timestamp}.xlsx"
    
    filepath = os.path.join(export_dir, filename)

    # Write to Excel
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if separate_sheets:
                # Separate sheets for each week
                weeks = df['Week'].unique()
                for week in weeks:
                    week_df = df[df['Week'] == week].drop(columns=['Week'])
                    # Sheet name length limit is 31 chars
                    sheet_name = week[:31] 
                    week_df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Single sheet with all data
                df.to_excel(writer, sheet_name="All Sessions", index=False)
        return True, f"Exported to {filepath}"
    except Exception as e:
        return False, str(e)
