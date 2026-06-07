from flask import send_file
from util import placeholders, log

# Export the SQLite Database file
def export_database():
    log.info("Exporting database")
    return send_file(
        placeholders.DATABASE_LOCATION,
        as_attachment=True,
        download_name="radded_data_dumper.sqlite3",
        mimetype="application/x-sqlite3",
    )