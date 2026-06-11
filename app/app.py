from pathlib import Path
import asyncio
import threading
from flask import Flask, redirect, request
from util import log
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase, LogEntry
from hass_api.api import HomeAssistantAPI
from addon_api import api
from workers import task_worker, test_task


### Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder=BUILT_FRONTEND_PATH)


### Global fields
app_db = None
hass_api = None
worker = None


### Routes
# Frontend
@app.route("/")
def redirect_index():
    return redirect("/index.html")

# Redirect to addon_api
@app.route("/api", defaults={"subpath": ""})
@app.route("/api/<path:subpath>")
def api_route(subpath):
    return api.api_root(request, app_db, hass_api, worker, subpath)

# TODO: This is a test. Now that testing is done, remove this!
@app.route("/test/<data>")
def worker_test(data):
    tt = test_task.TestTask(data)
    worker.add_task(tt)
    return f"Add test task {data}"


### Application startup
# Start Flask
def start_flask():
    app.run(host="0.0.0.0", port=8099, debug=True, use_reloader=False) # TODO: Debug probably isn't the best for production!

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

# Main thread
async def run():
    # Run Flask in a background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Run 
    await worker.start_worker()
    
# Prepare task startup
def main():
    setup()
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        # TODO: Log the task that's shutting down
        log.info(f"Interrupt signal recieved! Shutting down...")
        worker.shutdown()


## Startup methods
# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    