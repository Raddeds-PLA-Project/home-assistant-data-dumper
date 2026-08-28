class SettingsData:
    # The main settings table.
    # This will be a key-value pairing with a controlled addition.
    
    def create_table_json():
        # The table itself is simple, since I'm treating it as a key-value relationship.
        # Since lists can be included, I will add a many tag so that it's more obvious there can be more than one
        return ("""
        CREATE TABLE IF NOT EXISTS ApplicationSettings (
            ID INTEGER PRIMARY KEY,
            Key TEXT NOT NULL,
            Many BOOLEAN NOT NULL,
            Value JSON NOT NULL
        );
        """)
        
    def add_entity_blacklist_item(item):
        # Creates an entity blacklist item
        return ("""
        INSERT INTO ApplicationSettings (Key, Many, Value) VALUES (?, ?, ?);
        """, ("entity_blacklist_item", True, item))
        
    def retrieve_entity_blacklist_items():
        