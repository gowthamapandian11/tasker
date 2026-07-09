"""
models/task.py — Helper functions for the Task data structure.

A Task document in MongoDB looks like:
{
    "_id"         : ObjectId(...),
    "title"       : "Learn Docker",
    "description" : "Study Docker fundamentals",
    "member_id"   : ObjectId(...),
    "member_name" : "John",
    "date"        : "2026-06-28",
    "priority"    : "High",      # Low | Medium | High
    "status"      : "Planned",   # Planned | In Progress | Completed | Blocked
    "created_at"  : datetime(...),
    "updated_at"  : datetime(...)
}
"""

from datetime import datetime


# Allowed values for priority and status fields
PRIORITY_CHOICES = ["Low", "Medium", "High"]
STATUS_CHOICES   = ["Planned", "In Progress", "Completed", "Blocked"]


def create_task_doc(form_data: dict, member_name: str) -> dict:
    """
    Build a new task document ready to be inserted into MongoDB.

    Args:
        form_data   (dict): Data from the HTML form (title, description,
                            member_id, date, priority, status).
        member_name (str) : Resolved display name of the assigned member.

    Returns:
        dict: Task document with all fields and timestamps.
    """
    now = datetime.now()
    return {
        "title":       form_data.get("title", "").strip(),
        "description": form_data.get("description", "").strip(),
        "member_id":   form_data.get("member_id"),      # stored as string, cast to ObjectId in route
        "member_name": member_name.strip(),
        "date":        form_data.get("date", ""),
        "priority":    form_data.get("priority", "Low"),
        "status":      form_data.get("status", "Planned"),
        "created_at":  now,
        "updated_at":  now,
    }


def update_task_doc(form_data: dict, member_name: str) -> dict:
    """
    Build an update dict (used with $set) for an existing task.

    Args:
        form_data   (dict): Updated form data.
        member_name (str) : Resolved display name of the assigned member.

    Returns:
        dict: Fields to $set on the existing task document.
    """
    return {
        "title":       form_data.get("title", "").strip(),
        "description": form_data.get("description", "").strip(),
        "member_id":   form_data.get("member_id"),
        "member_name": member_name.strip(),
        "date":        form_data.get("date", ""),
        "priority":    form_data.get("priority", "Low"),
        "status":      form_data.get("status", "Planned"),
        "updated_at":  datetime.now(),
    }
