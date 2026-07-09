import os
from pathlib import Path

from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv

from routes.members import members_bp
from routes.tasks   import tasks_bp

# ─── App Configuration ────────────────────────────────────────────────────────

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Secret key for flash messages (change this to a random string in production)
app.secret_key = os.getenv("SECRET_KEY")
app.config["LOGGER_URL"] = os.getenv("LOGGER_URL")

# ─── MongoDB Connection ───────────────────────────────────────────────────────

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# Make the database accessible to all blueprints via app.config
app.config["DB"] = db

# ─── Register Blueprints ──────────────────────────────────────────────────────

app.register_blueprint(members_bp)   # handles / and /members
app.register_blueprint(tasks_bp)     # handles /tasks and /report


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Task Tracker running on http://localhost:5000")
    print("Make sure the Logger Service is running on http://localhost:5001")
    app.run(host="0.0.0.0", port=5000, debug=True)
