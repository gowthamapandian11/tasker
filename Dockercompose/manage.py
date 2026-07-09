import subprocess

from datetime import datetime

import sys
 
LOG_FILE = "deployment_report.txt"

COMPOSE_FILE = "docker-compose.yml"
 
 
def log(message):

    """Print and save to text file"""

    print(message)

    with open(LOG_FILE, "a") as f:

        f.write(message + "\n")
 
 
def run(command):

    log(f"\n>>> {' '.join(command)}")
 
    result = subprocess.run(command, capture_output=True, text=True)
 
    if result.stdout:

        log(result.stdout.strip())
 
    if result.stderr:

        log(result.stderr.strip())
 
    if result.returncode != 0:

        log("Command Failed")

        sys.exit(1)
 
    log("Command Success")
 
 
# ---------------- Start ----------------
 
with open(LOG_FILE, "w") as f:

    f.write("========== Docker Compose Deployment ==========\n")

    f.write(f"Start Time : {datetime.now()}\n\n")
 
log("Stopping old containers...")

run(["docker", "compose", "-f", COMPOSE_FILE, "down"])
 
log("Starting containers...")

run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])
 
log("Container Status...")

run(["docker", "compose", "-f", COMPOSE_FILE, "ps"])
 
log(f"\nDeployment Completed : {datetime.now()}")
 