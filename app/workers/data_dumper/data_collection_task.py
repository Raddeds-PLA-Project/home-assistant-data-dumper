from workers.task_worker import Task, TaskState
from db.db import EntityHistoryDatabase
from util import log
from hass_api.api import HomeAssistantAPI
from datetime import datetime

class DataCollectionTask(Task):
    def __init__(self, app_db: EntityHistoryDatabase, hass_api : HomeAssistantAPI):
        self.app_db = app_db
        super.init("Logbook API Collection Task", "Logs data from the Home Assistant Logbook API.")
        
    def run(self):
        self.status = TaskState.RUNNING
        
        log.info(f"{self.title} started")
        self._update_description("Determining timerange to log")
        
        # 1. Find last time data was logged
        last_log_time = self.app_db.time_of_newest_entry()
        
        # 2.A. If no entries logged,
        if not last_log_time:
            # We need to find the date of the last logged entry
            pass
        # 2.B. For each day between last logging and now    
        else:
            now = datetime.now()
            days_between = (now.date() - last_log_time.date()).days
        
        # 2. For each day between last logging and now,
        
            # 2.1. Retrieve log from day to day+1
            # 2.2. Save entries for each log
            # 2.3. Set most updated log to date and time of last log
            # 2.4. Continue