from pathlib import Path
import asyncio
import threading
from flask import Flask, redirect, request
from util import log, placeholders
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase
from workers.data_dumper.data_collection_task import DataCollectionTask
from hass_api.api import HomeAssistantAPI
from addon_api import api as addon_api
from workers import task_worker, task_scheduler, test_task
from datetime import datetime


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
    return redirect("index.html")

# Redirect to addon_api
@app.route("/api", defaults={"subpath": ""})
@app.route("/api/<path:subpath>")
def api_route(subpath):
    return addon_api.api_root(request, app_db, hass_api, worker, scheduler, subpath)

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
    scheduler.add_schedule_entry(
        task_scheduler.ScheduleEntry(
            queue_time=datetime.now(),
            task=DataCollectionTask(app_db, hass_api),
            daily=True
        )
    )
    
# Prepare task startup
def main():
    setup()
    try:
        # Start background workers
        asyncio.run(run())
        # Run Flask in the foreground
        app.run(host="0.0.0.0", port=8099, debug=False, use_reloader=False)
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
    