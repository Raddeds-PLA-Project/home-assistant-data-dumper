from pathlib import Path

from flask import Flask, redirect
from util import log
from util.placeholders import BUILT_FRONTEND_PATH
from db.db import EntityHistoryDatabase, LogEntry
from hass_api.api import HomeAssistantAPI
from addon_api import api
import datetime
import json

# Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder=BUILT_FRONTEND_PATH)

# Routes
@app.route("/")
def redirect_index():
    return redirect("/index.html")

@app.route("/api")
def api_route():
    return api.api_root()

# Startup
def main():
    log.info("Starting addon...")

    # Initialize database
    app_db = EntityHistoryDatabase()

    # Initialize API connection
    hass_api = HomeAssistantAPI()
    
    # Test database
    print("Inserting test entry")
    app_db.insert_complete_entry(LogEntry(datetime.datetime.now(datetime.UTC), "Test Entry", json.loads('{"name":"Home Assistant","message":"started","icon":"mdi:home-assistant","domain":"homeassistant","when":"2026-06-05T18:12:01.351850+00:00"}')))


### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8099, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()