from flask import abort
from workers.task_worker import TaskWorker
from util import log

from .export_db import export_database


def api_root(request, app_db, hass_api, worker : TaskWorker, subpath=""):

    # List tasks
    if subpath == "worker/tasks":
        return {
            "status": str(worker.state),
            "tasks": worker.list_tasks()
        }
    
    # Export data
    if subpath == "export/sqlite":
        return export_database()

    # Fallback, no subpath
    if request.path == "/api":
        return {"message": "Data dumper API backend is running!"}

    # Fallback, unrecognized subpath
    abort(404)