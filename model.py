from flask import Flask, request, jsonify
from flask_cors import CORS
import sched
import time
import threading

app = Flask(__name__)
CORS(app)

scheduler = sched.scheduler(time.time, time.sleep)
jobs = {}

def func(name: str, duration: int):
    """Simulates job execution."""
    print(f"[{time.strftime('%H:%M:%S')}] Starting: {name}")
    time.sleep(duration)  # Simulate execution time
    print(f"[{time.strftime('%H:%M:%S')}] Finished: {name}")

    # Mark job as executed and remove it
    if name in jobs:
        del jobs[name]

def task_wrapper(name, duration):
    """Wrapper function to execute jobs in a separate thread."""
    thread = threading.Thread(target=func, args=(name, duration))
    thread.start()

def add_job(name: str, prio: int, duration: int = 5):
    """Adds a job to the scheduler."""
    event = scheduler.enter(3, prio, task_wrapper, argument=(name, duration))
    jobs[name] = {"event": event, "executed": False}
    print(f'Job "{name}" added with priority {prio}')
    return event

def delete_job(name: str):
    """Removes a job if it exists."""
    if name in jobs:
        try:
            scheduler.cancel(jobs[name]["event"])  # Cancel scheduled job
            del jobs[name]
            return True
        except ValueError:
            print(f'Job "{name}" has already executed or does not exist.')
    return False

def execute_job(name: str):
    """Manually executes a job."""
    if name in jobs:
        threading.Thread(target=func, args=(name, 5)).start()
        return True
    return False

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """Returns the list of pending jobs."""
    job_list = [{"name": name, "priority": data["event"].priority} for name, data in jobs.items()]
    return jsonify(job_list)

@app.route('/jobs', methods=['POST'])
def create_job():
    """Adds a new job."""
    data = request.json
    name = data.get("name")
    priority = data.get("priority", 1)

    if not name:
        return jsonify({"error": "Job name is required"}), 400

    if name in jobs:
        return jsonify({"error": "Job already exists"}), 400

    add_job(name, priority)
    return jsonify({"message": f"Job '{name}' added successfully"}), 201

@app.route('/jobs/<name>', methods=['DELETE'])
def remove_job(name):
    """Deletes a job by name."""
    if delete_job(name):
        return jsonify({"message": f"Job '{name}' deleted successfully"}), 200
    return jsonify({"error": "Job not found"}), 404

@app.route('/jobs/<name>/execute', methods=['POST'])
def start_execution(name):
    """Starts execution of a specific job."""
    if execute_job(name):
        return jsonify({"message": f"Job '{name}' execution started"}), 200
    return jsonify({"error": "Job not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
