import sqlite3
from util import log
from util import placeholders
import sys
import json
from datetime import datetime
from time import sleep
from .entity_history import entity_history_db
from .migrations import migrations
from .settings import settings_db

class ApplicationDatabaseManager:
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
            log.warning(f"Database is newer than supported application version! Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}. Please update the application before continuing.")
            sys.exit(0)
            
        # Existing database is older than current, perform migration
        elif local_db_version < placeholders.DATABASE_VERSION:
            log.error(f"Database is out of date! Checking if it can be migrated. Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}")
            migrations.check_migration(local_db_version, placeholders.DATABASE_VERSION, self)
            
        ### Create top level tables
        self.entity_db = entity_history_db.EntityHistoryDatabase(self)
        self.settings_db = settings_db.SettingsDatabase(self)
            
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
        if not params:
            log.toomuchinfo(f"Sending SQL: {query}")
            result = self.cur.execute(query)
        else:
            log.toomuchinfo(f"Sending SQL: {query} | With parameters: {params}")
            result = self.cur.execute(query, params)
        
        self.conn.commit()

        # Unlock the database
        log.toomuchinfo("Unlocking database")
        self.__is_available = True

        # Return result
        return result