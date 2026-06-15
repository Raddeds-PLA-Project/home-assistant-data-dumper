from flask import abort
from workers.task_scheduler import TaskScheduler
from workers.task_worker import TaskWorker

# API entries for the Task Worker and Task Scheduler
# This will be called for all API routes that start with "worker"
def worker_root(request, worker : TaskWorker, scheduler : TaskScheduler, subpath=""):
    worker_subpath = subpath[len("worker"):].lstrip("/") if subpath.startswith("worker") else ""
    
    
    # List tasks from TaskWorker
    if worker_subpath == "tasks":
        return {
            "status": str(worker.state),
            "tasks": worker.list_tasks()
        }
        
    # List schedule from TaskSchedule
    if worker_subpath == "schedule":
        return {
            "schedule": scheduler.list_schedule_entries()
        }
        
    # Fallback, unrecognized subpath
    abort(404)