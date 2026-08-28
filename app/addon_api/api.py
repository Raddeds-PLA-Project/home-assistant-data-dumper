from flask import abort
from workers.task_worker import TaskWorker
from workers.task_scheduler import TaskScheduler
from util import log, placeholders
from db.db import ApplicationDatabaseManager
from hass_api.api import HomeAssistantAPI

from .export_db import export_root
from .worker_info import worker_root
from .db_info import db_root
from .run import run_root
from .info import info_root

# Root entry for the API subpath.
def api_root(request, app_db: ApplicationDatabaseManager, hass_api: HomeAssistantAPI, worker : TaskWorker, scheduler : TaskScheduler, subpath=""):

    # Manage the workers
    if subpath.startswith("worker/"):
        return worker_root(worker, scheduler, subpath)
    
    # Export data
    if subpath.startswith("export/"):
        return export_root(subpath)
    
    # Manage the database
    if subpath.startswith("db/"):
        return db_root(subpath, app_db)
    
    # Run tasks
    if subpath.startswith("run/"):
        return run_root(subpath, scheduler, app_db, hass_api)
    
    # General info
    if subpath.startswith("info/"):
        return info_root(request, subpath, hass_api)


    # Fallback, no subpath
    if request.path == "/api":
        return {"message": "Data dumper API backend is running!"}
    # Fallback, unrecognized subpath
    abort(404)
