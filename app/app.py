from pathlib import Path

from flask import Flask, redirect, request
from util import log
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase, LogEntry
from hass_api.api import HomeAssistantAPI
from addon_api import api
import datetime
import json


### Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder=BUILT_FRONTEND_PATH)


### Global fields
app_db = None
hass_api = None


### Routes
@app.route("/")
def redirect_index():
    return redirect("/index.html")

@app.route("/api", defaults={"subpath": ""})
@app.route("/api/<path:subpath>")
def api_route(subpath):
    return api.api_root(request, subpath)


### Application startup
# Startup
def main():
    log.info("Starting addon...")

    # Initialize database
    app_db = EntityHistoryDatabase()

    # Initialize API connection
    hass_api = HomeAssistantAPI()


## Startup methods
# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8099, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()