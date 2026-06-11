import sqlite3
from util import log
from util import placeholders
from . import domains
import sys
from .domains.generic import Domain
import json
from datetime import datetime

class EntityHistoryDatabase:
    def __init__(self):
        ### Initialize SQLite3 database
        # This file goes into the container root. It will be preserved upon uninstall, UNLESS the user selects "remove app data"
        log.info("Creating database...")
        self.conn = sqlite3.connect(placeholders.DATABASE_LOCATION)
        self.cur = self.conn.cursor()
        
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
            self.__send_query(f"""
            INSERT INTO DatadumperMigrations (version) VALUES ({placeholders.DATABASE_VERSION});
            """)
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
        self.__send_query(LogEntry.create_table())
        log.info("-> Created LogEntry table")

        
    def __send_query(self, query):
        log.toomuchinfo(f"Sending SQL: {query}")
        return self.cur.execute(query)

    def insert_complete_entry(self, log_entry):
        # Insert the LogEntry
        self.__send_query(log_entry.add_entry())

        # Commit all queries
        self.conn.commit()


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
        return """
        CREATE TABLE IF NOT EXISTS EntityHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME NOT NULL,
            Name TEXT NOT NULL,
            FullJSON TEXT NOT NULL,
            Icon TEXT
        );
        """

    # Retrieves the SQL to create an entry
    # Adding an actual entry needs to be done through the database, since it needs to reference the ID of this Entry
    def add_entry(self):
        if self.icon:
            return f"""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON, Icon) VALUES (
                '{self.timestamp.isoformat()}',
                '{self.name}',
                '{json.dumps(self.fullJSON)}',
                '{self.icon}'
            );
            """
        else:
            return f"""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON) VALUES (
                '{self.timestamp}',
                '{self.name}',
                '{json.dumps(self.fullJSON)}'
            );
            """