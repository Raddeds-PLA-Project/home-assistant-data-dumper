from db import EntityHistoryDatabase
from util import log

def check_migration(old_version: int, new_version: int, db: EntityHistoryDatabase):
    # Upgrade from version 1 to version 2.
    # The main change here was creating settings, no changes are needed here 
    if old_version == 1:
        db.__send_query("""INSERT INTO DatadumperMigrations (version) VALUES (?);""", (2, ))
        log.info("Updated from version 1 to version 2.")
        
    # Update from version 2 (placeholder for the future)
    if old_version == 2:
        pass
    
    log.info("Migration completed!")
        