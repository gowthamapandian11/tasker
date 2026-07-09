"""
models/member.py — Helper functions for the Member data structure.

A Member document in MongoDB looks like:
{
    "_id"       : ObjectId(...),
    "name"      : "John",
    "created_at": datetime(...)
}
"""

from datetime import datetime


def create_member_doc(name: str) -> dict:
    """
    Build a new member document ready to be inserted into MongoDB.

    Args:
        name (str): The team member's full name.

    Returns:
        dict: Member document with name and created_at timestamp.
    """
    return {
        "name": name.strip(),
        "created_at": datetime.now(),
    }
