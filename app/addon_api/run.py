from workers.task_scheduler import TaskScheduler

def run_root(subpath, scheduler : TaskScheduler):
    db_subpath = subpath[len("db"):].lstrip("/") if subpath.startswith("db") else ""
    
    # Run data collection right now
    if db_subpath == "collection":
        