from flask import Flask, request, jsonify
from logger import write_log

app = Flask(__name__)


# ─── Required fields for every log entry ───────────────────────────────────────
REQUIRED_FIELDS = [
    "timestamp",
    "service_name",
    "event_type",
    "member_name",
    "task_title",
    "message",
]


@app.route("/log", methods=["POST"])
def receive_log():
    """
    POST /log

    Accepts a JSON body with log data, validates it, then writes it to a
    dated log file.

    Returns:
        200 JSON {"status": "success", "message": "Log recorded."}
        400 JSON {"status": "error",   "message": "<reason>"}
        500 JSON {"status": "error",   "message": "<reason>"}
    """
    data = request.get_json(silent=True)

    # Ensure the request body is valid JSON
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing JSON body."}), 400

    # Check that every required field is present and non-empty
    missing_fields = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Write the log entry to the daily log file
    try:
        write_log(data)
        return jsonify({"status": "success", "message": "Log recorded."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """GET /health — Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "Logger Service"}), 200


if __name__ == "__main__":
    print("Logger Service running on http://localhost:5001")
    app.run(host="0.0.0.0",port=5001, debug=True)
