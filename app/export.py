"""
Export module for the Daily Planner App.

Handles exporting mentorship sessions to Excel files.
"""
import os
import pandas as pd
from sqlalchemy.orm import Session, sessionmaker
from .database import get_engine, MentorshipSession, DayLog
from datetime import datetime, timedelta, date

def export_to_excel(start_date: date = None, end_date: date = None, filename: str = None) -> tuple[bool, str]:
    """
    Exports mentorship sessions to an Excel file.

    Args:
        start_date (date, optional): The start date for the export. Defaults to None (all time).
        end_date (date, optional): The end date for the export. Defaults to None.
        filename (str, optional): The filename for the export. Defaults to "mentorship_log.xlsx".

    Returns:
        tuple[bool, str]: A tuple containing success status (True/False) and a message.
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

    # Write to Excel with separate sheets for each week
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Get unique weeks
            weeks = df['Week'].unique()
            for week in weeks:
                week_df = df[df['Week'] == week].drop(columns=['Week'])
                # Sheet name length limit is 31 chars
                sheet_name = week[:31] 
                week_df.to_excel(writer, sheet_name=sheet_name, index=False)
        return True, f"Exported to {filepath}"
    except Exception as e:
        return False, str(e)
