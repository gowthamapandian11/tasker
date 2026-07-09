"""
routes/members.py — Blueprint for team member management and the dashboard.

Routes:
    GET  /              → Dashboard (stats + task table with filters)
    GET  /members       → List all team members
    POST /members/add   → Add a new team member
    POST /members/<id>/delete → Delete a team member
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from datetime import datetime

from models.member import create_member_doc

# Create the blueprint
members_bp = Blueprint("members", __name__)


def get_db():
    """Return the MongoDB database instance from the app context."""
    return current_app.config["DB"]


# ─── Dashboard ────────────────────────────────────────────────────────────────

@members_bp.route("/")
def dashboard():
    """
    GET /
    Display the main dashboard:
      - Summary stat cards (total, completed, in-progress, planned, blocked)
      - Filters by member, status, and date
      - Full task table matching the active filters
    """
    db = get_db()

    # Build the filter query from URL parameters
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

    # Fetch all tasks matching the filter
    tasks = list(db.tasks.find(query).sort("created_at", -1))

    # Compute overall stats (unfiltered)
    all_tasks  = list(db.tasks.find())
    total      = len(all_tasks)
    completed  = sum(1 for t in all_tasks if t["status"] == "Completed")
    in_progress= sum(1 for t in all_tasks if t["status"] == "In Progress")
    planned    = sum(1 for t in all_tasks if t["status"] == "Planned")
    blocked    = sum(1 for t in all_tasks if t["status"] == "Blocked")

    # Fetch member list for the filter dropdown
    members = list(db.members.find().sort("name", 1))

    stats = {
        "total":       total,
        "completed":   completed,
        "in_progress": in_progress,
        "planned":     planned,
        "blocked":     blocked,
    }

    return render_template(
        "dashboard.html",
        tasks=tasks,
        stats=stats,
        members=members,
        filter_member=filter_member,
        filter_status=filter_status,
        filter_date=filter_date,
    )


# ─── Members List ─────────────────────────────────────────────────────────────

@members_bp.route("/members")
def members_list():
    """
    GET /members
    Display all team members and an inline form to add new ones.
    """
    db      = get_db()
    members = list(db.members.find().sort("name", 1))
    return render_template("members.html", members=members)


# ─── Add Member ───────────────────────────────────────────────────────────────

@members_bp.route("/members/add", methods=["POST"])
def add_member():
    """
    POST /members/add
    Validate and insert a new team member into MongoDB.
    """
    db   = get_db()
    name = request.form.get("name", "").strip()

    if not name:
        flash("Member name cannot be empty.", "error")
        return redirect(url_for("members.members_list"))

    # Check for duplicate names (case-insensitive)
    existing = db.members.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        flash(f'Member "{name}" already exists.', "error")
        return redirect(url_for("members.members_list"))

    db.members.insert_one(create_member_doc(name))
    flash(f'Member "{name}" added successfully.', "success")
    return redirect(url_for("members.members_list"))


# ─── Delete Member ────────────────────────────────────────────────────────────

@members_bp.route("/members/<member_id>/delete", methods=["POST"])
def delete_member(member_id):
    """
    POST /members/<member_id>/delete
    Remove a team member from MongoDB.
    """
    db     = get_db()
    member = db.members.find_one({"_id": ObjectId(member_id)})

    if not member:
        flash("Member not found.", "error")
        return redirect(url_for("members.members_list"))

    db.members.delete_one({"_id": ObjectId(member_id)})
    flash(f'Member "{member["name"]}" deleted.', "success")
    return redirect(url_for("members.members_list"))
