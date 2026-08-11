import sqlite3
from util import log
from util import placeholders
from . import domains
import sys
from .domains.generic import Domain
import json
from datetime import datetime
from time import sleep

class EntityHistoryDatabase:
    def __init__(self):
        ### Initialize SQLite3 database
        # This file goes into the container root. It will be preserved upon uninstall, UNLESS the user selects "remove app data"
        log.info(f"Initializing Database, version {placeholders.DATABASE_VERSION}")
        self.conn = sqlite3.connect(placeholders.DATABASE_LOCATION, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.__is_available = True
        
        # Create migration table
        self.__send_query("""
        CREATE TABLE IF NOT EXISTS DatadumperMigrations (
            version INT PRIMARY KEY,
            migratedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        ### Check database version and handle migrations
        local_db_version = self.__send_query("""
        SELECT MAX(version) FROM DatadumperMigrations;
        """).fetchone()[0]
        
        # First time launch
        if local_db_version is None:
            log.info("Detected first time launch. Creating database...")
            self.__send_query("""
            INSERT INTO DatadumperMigrations (version) VALUES (?);
            """, (int(placeholders.DATABASE_VERSION), ))
        # Unchanged version
        elif local_db_version == placeholders.DATABASE_VERSION:
            log.info("Database version unchanged, skipping creation.")
            return
        # Existing database is newer than application, fail
        elif local_db_version > placeholders.DATABASE_VERSION:
            log.error(f"Database is newer than application! Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}")
            sys.exit(1)
        # Existing database is older than application, perform migration
        elif local_db_version < placeholders.DATABASE_VERSION:
            log.error(f"Database is older than application! Please perform a migration before continuing. Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}")
            sys.exit(1)


        ### Create top level Entity History table
        self.__send_query(LogEntry.create_table()[0])
        log.info("-> Created LogEntry table")

    def get_unlocked(self):
        return self.__is_available
        
    def __send_query(self, query, params = None):
        # Database corruption protection: If another process is using the database, block until it becomes available
        while not self.__is_available:
            log.toomuchinfo("Database is in use by another process.")
            sleep(1)

        # Database has become available! Lock it now
        log.toomuchinfo("Locking database")
        self.__is_available = False

        # Send the message
        log.toomuchinfo(f"Sending SQL: {query}")
        if not params:
            result = self.cur.execute(query)
        else:
            result = self.cur.execute(query, params)
        
        self.conn.commit()

        # Unlock the database
        log.toomuchinfo("Unlocking database")
        self.__is_available = True

        # Return result
        return result

    def insert_complete_entry(self, log_entry):
        # Insert the LogEntry
        entry_data = log_entry.add_entry()
        self.__send_query(entry_data[0], entry_data[1])

        # Commit all queries
        self.conn.commit()
        
    # Gets the time of the newest entry
    def time_of_newest_entry(self):
        result = self.__send_query("""
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

    # Gets the number of entries
    def get_entry_count(self):
        result = self.__send_query("""
        SELECT COUNT(*) FROM EntityHistory;
        """).fetchone()

        # If there are no entries
        if result is None:
            return 0
        
        log.toomuchinfo(f"There are currently {result[0]} entries logged")
        return result[0]


class LogEntry:
    # An entry in the LogEntry database.
        # Timestamp, self explanatory
        # Name
        # FullJSON
        # Icon
    def __init__(self, timestamp: datetime, name: str, fullJSON: dict, icon = None):
        self.timestamp = timestamp
        self.name = name
        self.fullJSON = fullJSON
        self.icon = icon
        
    # Retrieve the SQL to create the table
    @staticmethod
    def create_table():
        ### Create top level entity history table
        # ID: A unique identifier for the particular state change.
        # TimeStamp: The date and time that the event occurred. UTC timezone.
        # Name: Refers to the Name in the Event log. # TODO: Maximum length?
        # fullJSON: The entire JSON of the log entry. # TODO: Maximum length?
        # Icon: MDI ID of icon. Optional.
        return ("""
        CREATE TABLE IF NOT EXISTS EntityHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME NOT NULL,
            Name TEXT NOT NULL,
            FullJSON TEXT NOT NULL,
            Icon TEXT
        );
        """)

    # Retrieves the SQL to create an entry
    # Adding an actual entry needs to be done through the database, since it needs to reference the ID of this Entry
    def add_entry(self):
        if self.icon:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON, Icon) VALUES (?, ?, ?, ?);
            """, (self.timestamp.isoformat(), self.name, json.dumps(self.fullJSON)))
        else:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON) VALUES (?, ?, ?);
            """, (self.timestamp, self.name, json.dumps(self.fullJSON)))