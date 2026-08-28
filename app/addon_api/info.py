from flask import abort, send_file
from hass_api.api import HomeAssistantAPI
from util import placeholders, log
import random

# Info root
def info_root(request, subpath, hass_api: HomeAssistantAPI):
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
    
    # Get specific entity icon 
    if info_subpath == "entity_picture":
        # The value from retrieve_entity_icon will be a requests.Response object containing whatever the normal value is for an image
        # I'm going to save this to a tempfile, then return the path of the tempfile
        seed = random.randrange(0, 2**16)
        output_path = f"/tmp/radded/entity_image_{seed}.png"
        icon_path = request.args.get('icon')
        if icon_path == None:
            abort(400, {"error", "missing parameter `icon`"})
            
        try:
            with open(output_path, "wb") as file:
                file.write(hass_api.retrieve_entity_icon(icon_path).content)
            return send_file(output_path)
        except AttributeError:
            abort(404, {"error", "icon not found"})
    
    # Fallback for unrecognized subpath
    abort(404)