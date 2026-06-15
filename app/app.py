from pathlib import Path
import asyncio
import threading
from flask import Flask, redirect, request
from util import log
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase, LogEntry
from hass_api.api import HomeAssistantAPI
from addon_api import api
from workers import task_worker, test_task, task_scheduler
import datetime


### Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder=BUILT_FRONTEND_PATH)


### Global fields
app_db = None
hass_api = None
worker = None
scheduler = None


### Routes
# Frontend
@app.route("/")
def redirect_index():
    return redirect("/index.html")

# Redirect to addon_api
@app.route("/api", defaults={"subpath": ""})
@app.route("/api/<path:subpath>")
def api_route(subpath):
    return api.api_root(request, app_db, hass_api, worker, scheduler, subpath)

# TODO: Test to create tasks
@app.route("/task/<data>")
def worker_test(data):
    tt = test_task.TestTask(data)
    worker.add_task(tt)
    return f"Add test task {data}"

# TODO: Test to schedule tasks
@app.route("/schedule/<time>/<name>")
def scheduler_test(time, name):
    ts = task_scheduler.ScheduleEntry(
        queue_at = datetime.datetime.fromisoformat(time),
        task = test_task.TestTask(name)
    )
    scheduler.add_schedule_entry(ts)
    return f"Added schedule entry {name} for {time}"


### Application startup

# Initialization
def setup():
    log.info("Starting addon...")

    # Initialize database
    # global app_db
    # app_db = EntityHistoryDatabase()

    # # Initialize API connection
    # global hass_api
    # hass_api = HomeAssistantAPI()
    
    # Initialize TaskWorker
    global worker
    worker = task_worker.TaskWorker()
    
    # Initialize TaskScheduler
    global scheduler
    scheduler = task_scheduler.TaskScheduler(worker)

# Main thread
async def run():
    # Run Task worker in a background thread
    def start_task_worker():
        asyncio.run(worker.start_worker())
    task_worker_thread = threading.Thread(target = start_task_worker, daemon=True)
    task_worker_thread.start()
    
    # Run Scheduler in a background thread
    def start_scheduler():
        asyncio.run(scheduler.start_scheduler())
    task_scheduler_thread = threading.Thread(target = start_scheduler, daemon=True)
    task_scheduler_thread.start()
    
# Prepare task startup
def main():
    setup()
    try:
        # Start background workers
        asyncio.run(run())
        # Run Flask in the foreground
        app.run(host="0.0.0.0", port=8099, debug=True, use_reloader=False) # TODO: Debug probably isn't the best for production!
    except KeyboardInterrupt:
        # TODO: Log the task that's shutting down
        log.info("Interrupt signal recieved! Shutting down...")
        worker.shutdown()
        scheduler.shutdown()


## Startup methods
# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    