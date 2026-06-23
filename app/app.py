from pathlib import Path
import asyncio
import threading
from flask import Flask, redirect, request
from util import log, placeholders
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase
from workers.data_dumper import data_collection_task
from hass_api.api import HomeAssistantAPI
from addon_api import api as addon_api
from workers import task_worker, task_scheduler, test_task
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
    return addon_api.api_root(request, app_db, hass_api, worker, scheduler, subpath)

# Tests
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
        queue_time = datetime.datetime.fromisoformat(time),
        task = test_task.TestTask(name)
    )
    scheduler.add_schedule_entry(ts)
    return f"Added schedule entry {name} for {time}"

# TODO: Test to get log entry
@app.route("/logtest/<timestart>/<timeend>")
def log_entry_test(timestart, timeend):
    return hass_api.retrieve_log(end_time=datetime.datetime.fromisoformat(timeend), start_time=datetime.datetime.fromisoformat(timestart))

# TODO: Test to force data collection
@app.route("/forcedata")
def force_data_collection():
    worker.add_task(data_collection_task.DataCollectionTask(app_db=app_db, hass_api=hass_api))
    return "Added a data collection task"

### Application startup

# Initialization
def setup():
    log.info(f"Starting Radded's Home Assistant Data Dumper: Version {placeholders.APP_VERSION}")

    # Initialize database
    global app_db
    app_db = EntityHistoryDatabase()

    # Initialize API connection
    global hass_api
    hass_api = HomeAssistantAPI()
    
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
    task_worker_thread.name = "Task-Worker-Thread"
    task_worker_thread.start()
    
    # Run Scheduler in a background thread
    def start_scheduler():
        asyncio.run(scheduler.start_scheduler())
    task_scheduler_thread = threading.Thread(target = start_scheduler, daemon=True)
    task_scheduler_thread.name = "Task-Scheduler-Thread"
    task_scheduler_thread.start()
    
    # Run data collection nightly
    
# Prepare task startup
def main():
    setup()
    try:
        # Start background workers
        asyncio.run(run())
        # Run Flask in the foreground
        app.run(host="0.0.0.0", port=8099, debug=True, use_reloader=False) # TODO: Debug probably isn't the best for production!
        # TODO: Make port customizable in HA Settings
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
    