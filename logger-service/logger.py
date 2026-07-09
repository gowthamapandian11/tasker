"""
logger.py — Handles writing log entries to dated log files.

Each log is appended to a file named YYYY-MM-DD.log inside the logs/ directory.
The logs/ directory is created automatically if it does not exist.
"""

import os
from datetime import datetime


# Directory where log files will be stored
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")


def write_log(data: dict) -> None:
    """
    Write a formatted log entry to the appropriate daily log file.

    Args:
        data (dict): Validated log data containing:
            - timestamp     : Event time string (e.g. "2026-06-28 10:30:00")
            - service_name  : Name of the calling service
            - event_type    : Type of event (e.g. TASK_CREATED)
            - member_name   : Name of the team member involved
            - task_title    : Title of the task involved
            - message       : Human-readable description of the event
    """
    # Ensure the logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Determine today's log file name
    today = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(LOGS_DIR, f"{today}.log")

    # Build the formatted log block
    log_entry = (
        f"[{data['timestamp']}] [{data['service_name']}] [{data['event_type']}]\n"
        f"Member : {data['member_name']}\n"
        f"Task   : {data['task_title']}\n"
        f"Message: {data['message']}\n"
        f"----------------------------------------------------\n"
    )

    # Append the log entry to the file (creates file if it doesn't exist)
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
