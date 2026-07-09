"""
routes/tasks.py — Blueprint for task management and monthly reports.

Routes:
    GET  /tasks                  → Task list (with filters)
    GET  /tasks/add              → Show add-task form
    POST /tasks/add              → Create a new task
    GET  /tasks/<id>/edit        → Show edit-task form
    POST /tasks/<id>/edit        → Update an existing task
    POST /tasks/<id>/delete      → Delete a task
    POST /tasks/<id>/status      → Update task status only
    GET  /report                 → Monthly report page
"""

import os

import requests as http_client
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
from bson import ObjectId
from datetime import datetime

from models.task import (
    create_task_doc, update_task_doc,
    PRIORITY_CHOICES, STATUS_CHOICES
)

# Create the blueprint
tasks_bp = Blueprint("tasks", __name__)

# Logger Service URL — Task Tracker POSTs log events here
LOGGER_URL = os.getenv("LOGGER_URL")


def get_db():
    """Return the MongoDB database instance from the app context."""
    return current_app.config["DB"]


# ─── Logger Integration ───────────────────────────────────────────────────────

def send_log(event_type: str, member_name: str, task_title: str, message: str) -> None:
    """
    Fire-and-forget POST to the Logger Service.
    If the Logger Service is unavailable, the error is silently ignored
    so the Task Tracker continues to work normally.

    Args:
        event_type  (str): e.g. TASK_CREATED, TASK_UPDATED, TASK_DELETED, STATUS_CHANGED
        member_name (str): Name of the member associated with the task.
        task_title  (str): Title of the task.
        message     (str): Human-readable description of the event.
    """
    payload = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service_name": "Task Tracker",
        "event_type":   event_type,
        "member_name":  member_name,
        "task_title":   task_title,
        "message":      message,
    }
    try:
        logger_url = current_app.config.get("LOGGER_URL", LOGGER_URL)
        http_client.post(logger_url, json=payload, timeout=2)
    except Exception:
        # Logger Service is optional — never crash the main app
        pass


# ─── Task List ────────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks")
def task_list():
    """
    GET /tasks
    Show all tasks with optional filters by member, status, and date.
    """
    db = get_db()

    # Build MongoDB filter query from URL parameters
    query = {}
    filter_member = request.args.get("member", "")
    filter_status = request.args.get("status", "")
    filter_date   = request.args.get("date", "")

    if filter_member:
        query["member_name"] = filter_member
    if filter_status:
        query["status"] = filter_status
    if filter_date:
        query["date"] = filter_date

    tasks   = list(db.tasks.find(query).sort("date", -1))
    members = list(db.members.find().sort("name", 1))

    return render_template(
        "task_list.html",
        tasks=tasks,
        members=members,
        statuses=STATUS_CHOICES,
        filter_member=filter_member,
        filter_status=filter_status,
        filter_date=filter_date,
    )


# ─── Add Task ─────────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    """
    GET  /tasks/add → Render the add-task form.
    POST /tasks/add → Validate and insert a new task.
    """
    db      = get_db()
    members = list(db.members.find().sort("name", 1))

    if request.method == "POST":
        title     = request.form.get("title", "").strip()
        member_id = request.form.get("member_id", "")

        # Basic validation
        if not title:
            flash("Task title is required.", "error")
            return render_template("add_task.html", members=members,
                                   priorities=PRIORITY_CHOICES, statuses=STATUS_CHOICES)
        if not member_id:
            flash("Please select a team member.", "error")
            return render_template("add_task.html", members=members,
                                   priorities=PRIORITY_CHOICES, statuses=STATUS_CHOICES)

        # Resolve member name
        member = db.members.find_one({"_id": ObjectId(member_id)})
        if not member:
            flash("Selected member not found.", "error")
            return render_template("add_task.html", members=members,
                                   priorities=PRIORITY_CHOICES, statuses=STATUS_CHOICES)

        # Insert the new task
        task_doc = create_task_doc(request.form, member["name"])
        db.tasks.insert_one(task_doc)

        # Notify Logger Service
        send_log(
            event_type="TASK_CREATED",
            member_name=member["name"],
            task_title=title,
            message="Task created successfully."
        )

        flash(f'Task "{title}" created successfully.', "success")
        return redirect(url_for("tasks.task_list"))

    return render_template(
        "add_task.html",
        members=members,
        priorities=PRIORITY_CHOICES,
        statuses=STATUS_CHOICES,
        today=datetime.now().strftime("%Y-%m-%d"),
    )


# ─── Edit Task ────────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    """
    GET  /tasks/<task_id>/edit → Render the edit-task form pre-filled.
    POST /tasks/<task_id>/edit → Validate and update the task.
    """
    db   = get_db()
    task = db.tasks.find_one({"_id": ObjectId(task_id)})

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.task_list"))

    members = list(db.members.find().sort("name", 1))

    if request.method == "POST":
        title     = request.form.get("title", "").strip()
        member_id = request.form.get("member_id", "")

        if not title:
            flash("Task title is required.", "error")
            return render_template("edit_task.html", task=task, members=members,
                                   priorities=PRIORITY_CHOICES, statuses=STATUS_CHOICES)

        # Resolve updated member name
        member = db.members.find_one({"_id": ObjectId(member_id)})
        if not member:
            flash("Selected member not found.", "error")
            return render_template("edit_task.html", task=task, members=members,
                                   priorities=PRIORITY_CHOICES, statuses=STATUS_CHOICES)

        update_fields = update_task_doc(request.form, member["name"])
        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_fields})

        # Notify Logger Service
        send_log(
            event_type="TASK_UPDATED",
            member_name=member["name"],
            task_title=title,
            message="Task updated successfully."
        )

        flash(f'Task "{title}" updated successfully.', "success")
        return redirect(url_for("tasks.task_list"))

    return render_template(
        "edit_task.html",
        task=task,
        members=members,
        priorities=PRIORITY_CHOICES,
        statuses=STATUS_CHOICES,
    )


# ─── Delete Task ──────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    """
    POST /tasks/<task_id>/delete
    Remove a task from MongoDB and log the deletion.
    """
    db   = get_db()
    task = db.tasks.find_one({"_id": ObjectId(task_id)})

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.task_list"))

    db.tasks.delete_one({"_id": ObjectId(task_id)})

    # Notify Logger Service
    send_log(
        event_type="TASK_DELETED",
        member_name=task.get("member_name", "Unknown"),
        task_title=task.get("title", "Unknown"),
        message="Task deleted successfully."
    )

    flash(f'Task "{task["title"]}" deleted.', "success")
    return redirect(url_for("tasks.task_list"))


# ─── Update Status ────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/<task_id>/status", methods=["POST"])
def update_status(task_id):
    """
    POST /tasks/<task_id>/status
    Change only the status field of a task (quick status update).
    """
    db     = get_db()
    task   = db.tasks.find_one({"_id": ObjectId(task_id)})
    new_status = request.form.get("status", "")

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.task_list"))

    if new_status not in STATUS_CHOICES:
        flash("Invalid status value.", "error")
        return redirect(url_for("tasks.task_list"))

    db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": new_status, "updated_at": datetime.now()}}
    )

    # Notify Logger Service
    send_log(
        event_type="STATUS_CHANGED",
        member_name=task.get("member_name", "Unknown"),
        task_title=task.get("title", "Unknown"),
        message=f"Status changed to '{new_status}'."
    )

    flash(f'Status updated to "{new_status}".', "success")
    # Redirect back to the referring page (task list or dashboard)
    return redirect(request.referrer or url_for("tasks.task_list"))


# ─── Monthly Report ───────────────────────────────────────────────────────────

@tasks_bp.route("/report")
def monthly_report():
    """
    GET /report?month=MM&year=YYYY
    Generate an individual monthly report for every team member.

    The report shows:
      - A summary table (total, completed, in-progress, planned, blocked, %)
      - A per-member detailed task breakdown
    """
    db = get_db()

    # Default to current month/year
    now           = datetime.now()
    selected_month= int(request.args.get("month", now.month))
    selected_year = int(request.args.get("year", now.year))

    # Build date prefix for filtering (YYYY-MM)
    month_prefix = f"{selected_year:04d}-{selected_month:02d}"

    # Fetch tasks whose date starts with the selected month
    tasks = list(db.tasks.find({"date": {"$regex": f"^{month_prefix}"}}))

    # Fetch all members
    members = list(db.members.find().sort("name", 1))

    # Build per-member report data
    report = []
    for member in members:
        member_tasks = [t for t in tasks if t.get("member_name") == member["name"]]
        total      = len(member_tasks)
        completed  = sum(1 for t in member_tasks if t["status"] == "Completed")
        in_progress= sum(1 for t in member_tasks if t["status"] == "In Progress")
        planned    = sum(1 for t in member_tasks if t["status"] == "Planned")
        blocked    = sum(1 for t in member_tasks if t["status"] == "Blocked")
        percentage = round((completed / total * 100), 1) if total > 0 else 0.0

        report.append({
            "member_name": member["name"],
            "total":       total,
            "completed":   completed,
            "in_progress": in_progress,
            "planned":     planned,
            "blocked":     blocked,
            "percentage":  percentage,
            "tasks":       sorted(member_tasks, key=lambda t: t.get("date", "")),
        })

    # Build month/year options for the selector (current year ± 1)
    months = [
        (1,"January"),(2,"February"),(3,"March"),(4,"April"),
        (5,"May"),(6,"June"),(7,"July"),(8,"August"),
        (9,"September"),(10,"October"),(11,"November"),(12,"December")
    ]
    years = list(range(now.year - 1, now.year + 2))

    return render_template(
        "monthly_report.html",
        report=report,
        selected_month=selected_month,
        selected_year=selected_year,
        months=months,
        years=years,
        month_label=months[selected_month - 1][1],
    )
