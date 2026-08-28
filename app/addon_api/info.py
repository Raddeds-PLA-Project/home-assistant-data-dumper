from flask import abort
from hass_api.api import HomeAssistantAPI
from util import placeholders

# Info root
def info_root(subpath, hass_api: HomeAssistantAPI):
    info_subpath = subpath[len("info"):].lstrip("/") if subpath.startswith("info") else ""
    
    # Return version info of the app
    if info_subpath == "version":
        return {
            "app_version": placeholders.APP_VERSION,
            "db_version": placeholders.DATABASE_VERSION
        }
        
    # Get HA instance entity list
    if info_subpath == "entities":
        return hass_api.retrieve_entities()
    
    # Fallback for unrecognized subpath
    abort(404)