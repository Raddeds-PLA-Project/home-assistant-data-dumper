from flask import abort
from util import log

from .export_db import export_database


def api_root(request, subpath=""):
    
    if subpath == "export/sqlite":
        return export_database()

    if request.path == "/api":
        return {"message": "Data dumper API backend is running!"}

    abort(404)