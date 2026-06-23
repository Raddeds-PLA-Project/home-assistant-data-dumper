from flask import send_file, abort
from util import placeholders, log

# Export hook
def export_root(subpath=""):
    export_subpath = subpath[len("export"):].lstrip("/") if subpath.startswith("export") else ""

    # Send the pure SQLite DB
    if export_subpath == "sqlite":
        log.info("Exporting database as SQLite...")
        return send_file(
            placeholders.DATABASE_LOCATION,
            as_attachment=True,
            download_name="radded_data_dumper.sqlite3",
            mimetype="application/x-sqlite3",
        )

    # Fallback for unrecognized subpath
    abort(404)