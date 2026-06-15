from workers.task_worker import Task, TaskState
from 
from util import log

class DataCollectionTask(Task):
    def __init__(self, app_db: EntityHistoryDatabase):
        super.init("Logbook API Collection Task", "Logs data from the Home Assistant Logbook API.")
        
    def run(self):
        self.status = TaskState.RUNNING
        
        log.info(f"{self.title} started")
        
        # 1. Find last time data was logged
        # 2. For each day between last logging and now,
            # 2.1. Retrieve log from day to day+1
            # 2.2. Save entries for each log
            # 2.3. Set most updated log to date and time of last log
            # 2.4. Continue