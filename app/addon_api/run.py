from db.db import ApplicationDatabaseManager
from hass_api.api import HomeAssistantAPI
from workers.task_scheduler import TaskScheduler, ScheduleEntry
from workers.data_dumper.data_collection_task import DataCollectionTask
from datetime import datetime, timedelta
from flask import abort

def run_root(subpath, scheduler : TaskScheduler, app_db : ApplicationDatabaseManager, hass_api : HomeAssistantAPI):
    db_subpath = subpath[len("run"):].lstrip("/") if subpath.startswith("run") else ""
    
    # Run data collection right now
    if db_subpath == "collection":
        scheduler.add_schedule_entry(ScheduleEntry(
            queue_time=datetime.now() + timedelta(seconds=2),
            task=DataCollectionTask(app_db, hass_api)
        ))
        return "Added a data collection task"
    
    # Fallback, unrecognized subpath
    abort(404)