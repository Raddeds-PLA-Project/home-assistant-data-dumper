from db.db import EntityHistoryDatabase
from flask import abort

def db_root(subpath, app_db: EntityHistoryDatabase):
    db_subpath = subpath[len("db"):].lstrip("/") if subpath.startswith("db") else ""

    # List some database info
    if db_subpath == "info":
        newest_entry_time = app_db.time_of_newest_entry()
        return {
            "is_unlocked": app_db.get_locked(), # TODO: This will never show locked since the below requests depend on the database
            "newest_entry_time": newest_entry_time.isoformat() if newest_entry_time else "N/A: No entries",
            "entry_count": app_db.get_entry_count()
        }

    # Fallback, unrecognized subpath
    abort(404)