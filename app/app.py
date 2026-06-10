from pathlib import Path

from flask import Flask, redirect, request
from util import log
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase, LogEntry
from hass_api.api import HomeAssistantAPI
from addon_api import api
from workers import task_worker, test_task
import asyncio


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
    return api.api_root(request, subpath)

# TODO: This is a test
@app.route("/test/<data>")
def worker_test(data):
    tt = test_task.TestTask(data)
    worker.add_task(tt)
    return f"Started test task {data}"

@app.route("/start")
def start():
    asyncio.run(worker.start_worker())
    return "Worker completed"

### Application startup
# Startup
def main():
    log.info("Starting addon...")

    # Initialize database
    global app_db
    app_db = EntityHistoryDatabase()

    # Initialize API connection
    global hass_api
    hass_api = HomeAssistantAPI()
    
    # Initialize TaskWorker
    global worker
    worker = task_worker.TaskWorker()
    


## Startup methods
# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8099, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()