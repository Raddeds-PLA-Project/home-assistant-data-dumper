from workers.task_worker import Task, TaskState
from db.db import EntityHistoryDatabase, LogEntry
from util import log
from hass_api.api import HomeAssistantAPI
from datetime import datetime, timedelta

class DataCollectionTask(Task):
    def __init__(self, app_db: EntityHistoryDatabase, hass_api : HomeAssistantAPI):
        self.app_db = app_db
        self.hass_api = hass_api
        super().__init__("Logbook API Collection Task", "Logs data from the Home Assistant Logbook API.")
        
    def run(self):
        self.status = TaskState.RUNNING
        
        log.info(f"{self.title} started")
        self._update_description("Determining timerange to log")
        
        # 1. Find last time data was logged
        checked_range_begin = self.app_db.time_of_newest_entry()
        logbook_dump = []
        checked_range_end = datetime.now()
        
        # 2. If no entries logged,
        if not checked_range_begin:
            # This is an empty database = first data dump.
            # Since we know that Home Assistant's logbook ranges only 10 days, we can collect those 10 days and store them
            # TODO: If this ever changes or becomes adjustable, We might want a dynamic form of this.
            checked_range_begin = checked_range_end - timedelta(days = 11)
            self._update_description(f"First datadump! Dumping the earliest 11 days from logbook. ({checked_range_begin} to {checked_range_end})")
        else:
            self._update_description(f"Dumping from ({checked_range_begin} to {checked_range_end})")

        # 3. Log from the beginning of range to now
        logbook_dump = self.hass_api.retrieve_log(checked_range_end, checked_range_begin)
        
        # 4. For each entry in the log, convert it into a database entry and save
        entry_count = len(logbook_dump)
        written_entries = 0
        for entry in logbook_dump:
            self.app_db.insert_complete_entry(DataCollectionTask.create_log_entry_from_json(entry))
            written_entries += 1
            self._update_description(f"Dump completed! Writing {written_entries}/{entry_count} entries to database")

        # 5. Done!
        log.info(f"{self.title} completed")
        self._update_description(f"Finished data dump, imported {written_entries} logs from {checked_range_begin} to {checked_range_end}")
        self.status = TaskState.COMPLETED

    @staticmethod
    def create_log_entry_from_json(json_data):
        # Check for icon

        return LogEntry(
            timestamp = datetime.fromisoformat(json_data['when']),
            name = json_data['name'],
            fullJSON = json_data,
            icon = json_data['icon'] if 'icon' in json_data else None
        )