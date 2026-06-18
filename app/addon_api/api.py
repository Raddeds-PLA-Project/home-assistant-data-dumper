from flask import abort
from workers.task_worker import TaskWorker
from workers.task_scheduler import TaskScheduler
from util import log, placeholders

from .export_db import export_database
from .worker import worker_root

# Root entry for the API subpath.
def api_root(request, app_db, hass_api, worker : TaskWorker, scheduler : TaskScheduler, subpath=""):

    # Route to worker
    if subpath.startswith("worker/"):
        return worker_root(request, worker, scheduler, subpath)
    
    # Export data
    if subpath == "export/sqlite":
        return export_database()
    
    # App versions
    if subpath == "versions":
        return {
            "app_version": placeholders.APP_VERSION,
            "db_version": placeholders.DATABASE_VERSION
        }

    # Fallback, no subpath
    if request.path == "/api":
        return {"message": "Data dumper API backend is running!"}

    # Fallback, unrecognized subpath
    abort(404)