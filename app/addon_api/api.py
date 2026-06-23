from flask import abort
from workers.task_worker import TaskWorker
from workers.task_scheduler import TaskScheduler
from util import log, placeholders

from .export_db import export_root
from .worker_info import worker_root
from .db_info import db_root

# Root entry for the API subpath.
def api_root(request, app_db, hass_api, worker : TaskWorker, scheduler : TaskScheduler, subpath=""):

    # Route to worker
    if subpath.startswith("worker/"):
        return worker_root(request, worker, scheduler, subpath)
    # Export data
    if subpath.startswith("export/"):
        return export_root(subpath)
    # App versions
    if subpath == "versions":
        return {
            "app_version": placeholders.APP_VERSION,
            "db_version": placeholders.DATABASE_VERSION
        }
    # DB
    if subpath.startswith("db/"):
        return db_root(subpath, app_db)

    # Fallback, no subpath
    if request.path == "/api":
        return {"message": "Data dumper API backend is running!"}
    # Fallback, unrecognized subpath
    abort(404)
