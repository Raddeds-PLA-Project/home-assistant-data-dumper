from db import ApplicationDatabaseManager
from util import log
from datetime import datetime
import json

class LogEntry:
    # An entry in the LogEntry database.
    # This is being used as a separate class from the EntityHistoryDatabase since it will be extended as I serialize the entry types.
    # I will call a nested chain of supers which will attach together the foreign key entries.
        # Timestamp, self explanatory
        # Name
        # FullJSON
        # Icon
    def __init__(self, timestamp: datetime, name: str, fullJSON: dict, icon = None):
        self.timestamp = timestamp
        self.name = name
        self.fullJSON = fullJSON
        self.icon = icon

    # Retrieves the SQL to create an entry
    # Adding an actual entry needs to be done through the database, since it needs to reference the ID of this Entry
    def add_entry_sql(self):
        if self.icon:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON, Icon) VALUES (?, ?, ?, ?);
            """, (self.timestamp.isoformat(), self.name, json.dumps(self.fullJSON), self.icon))
        else:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON) VALUES (?, ?, ?);
            """, (self.timestamp.isoformat(), self.name, json.dumps(self.fullJSON)))


class EntityHistoryDatabase:
    
    ### The top level entity history table.
    # ID: A unique identifier for the particular state change.
    # TimeStamp: The date and time that the event occurred. UTC timezone.
    # Name: Refers to the Name in the Event log. # TODO: Maximum length?
    # fullJSON: The entire JSON of the log entry.
    # Icon: MDI ID of icon. Optional.
    
    __create_table_sql = """
    CREATE TABLE IF NOT EXISTS EntityHistory (
        ID INTEGER PRIMARY KEY,
        TimeStamp DATETIME NOT NULL,
        Name TEXT NOT NULL,
        FullJSON JSON NOT NULL,
        Icon TEXT
    );
    """
    
    def __init__(self, db: ApplicationDatabaseManager):
        self.db = db
        db.__send_query(self.__create_table_sql)
        log.info("-> Created EntityHistory table")
        
        
    def insert_complete_entry(self, entry: LogEntry):
        # Insert the LogEntry
        entry_data = entry.add_entry_sql()
        self.db.__send_query(entry_data[0], entry_data[1])

        # Commit all queries
        self.db.conn.commit()
        
        
    # Gets the time of the newest entry
    def time_of_newest_entry(self):
        result = self.db.__send_query("""
        SELECT TimeStamp FROM EntityHistory
        ORDER BY TimeStamp DESC
        LIMIT 1;
        """).fetchone()

        # If there are no entries
        if result is None:
            log.toomuchinfo("No entries logged!")
            return None

        log.toomuchinfo(f"Last entry was logged at {result[0]}")
        return datetime.fromisoformat(result[0])
    
    # Gets the time of the oldest entry
    def time_of_oldest_entry(self):
        result = self.db.__send_query("""
        SELECT TimeStamp FROM EntityHistory
        ORDER BY TimeStamp
        LIMIT 1;
        """).fetchone()

        # If there are no entries
        if result is None:
            log.toomuchinfo("No entries logged!")
            return None

        log.toomuchinfo(f"Oldest entry was logged at {result[0]}")
        return datetime.fromisoformat(result[0])

    # Gets the number of entries
    def get_entry_count(self):
        result = self.db.__send_query("""
        SELECT COUNT(*) FROM EntityHistory;
        """).fetchone()

        # If there are no entries
        if result is None:
            return 0
        
        log.toomuchinfo(f"There are currently {result[0]} entries logged")
        return result[0]