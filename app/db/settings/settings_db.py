from db import ApplicationDatabaseManager
from util import log

class SettingsDatabase:
    # The main settings table.
    # This will be a key-value pairing. This class will control which types of keys and values can be added.
    __create_table_sql = """
    CREATE TABLE IF NOT EXISTS ApplicationSettings (
        ID INTEGER PRIMARY KEY,
        Key TEXT NOT NULL,
        Many BOOLEAN NOT NULL,
        Value JSON NOT NULL
    );
    """


    # Retrieve the DBM, Create the table
    def __init__(self, db: ApplicationDatabaseManager):
        self.db = db
        self.db.__send_query(self.__create_table_sql)
        log.info("-> Created SettingsDatabase Table table")


    # Create an entity blacklist key item
    def add_entity_blacklist_item(self, entity):
        # Creates an entity blacklist item
        self.db.__send_query("""
        INSERT INTO ApplicationSettings (Key, Many, Value) VALUES (?, ?, ?);
        """, ("entity_blacklist_item", True, entity))

        
    def retrieve_entity_blacklist_items(self):
        pass