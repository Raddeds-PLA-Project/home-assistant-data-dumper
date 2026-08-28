from datetime import datetime
import json

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
    def create_table_json():
        ### Create top level entity history table
        # ID: A unique identifier for the particular state change.
        # TimeStamp: The date and time that the event occurred. UTC timezone.
        # Name: Refers to the Name in the Event log. # TODO: Maximum length?
        # fullJSON: The entire JSON of the log entry.
        # Icon: MDI ID of icon. Optional.
        return ("""
        CREATE TABLE IF NOT EXISTS EntityHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME NOT NULL,
            Name TEXT NOT NULL,
            FullJSON JSON NOT NULL,
            Icon TEXT
        );
        """)

    # Retrieves the SQL to create an entry
    # Adding an actual entry needs to be done through the database, since it needs to reference the ID of this Entry
    def add_entry_json(self):
        if self.icon:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON, Icon) VALUES (?, ?, ?, ?);
            """, (self.timestamp.isoformat(), self.name, json.dumps(self.fullJSON), self.icon))
        else:
            return ("""
            INSERT INTO EntityHistory (TimeStamp, Name, FullJSON) VALUES (?, ?, ?);
            """, (self.timestamp.isoformat(), self.name, json.dumps(self.fullJSON)))