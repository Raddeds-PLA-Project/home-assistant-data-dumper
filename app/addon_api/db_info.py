from db.db import EntityHistoryDatabase
from flask import abort

def db_root(subpath, app_db: EntityHistoryDatabase):
    db_subpath = subpath[len("db"):].lstrip("/") if subpath.startswith("db") else ""

    # List some database info
    if db_subpath == "info":
        db_unlocked = app_db.get_unlocked()
        if not db_unlocked:
            return {
                "is_unlocked": db_unlocked,
                "newest_entry_time": "N/A: DB is locked",
                "entry_count": "N/A: DB is locked"
            }
        else:
            newest_entry_time = app_db.time_of_newest_entry()
            oldest_entry_time = app_db.time_of_oldest_entry()
            return {
                "is_unlocked": db_unlocked,
                "newest_entry_time": newest_entry_time.isoformat() if newest_entry_time else "N/A: No entries",
                "oldest_entry_time": oldest_entry_time.isoformat() if oldest_entry_time else "N/A: No entries",
                "entry_count": app_db.get_entry_count()
            }

    # Fallback, unrecognized subpath
    abort(404)