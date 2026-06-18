from .log_level import LOG_LEVELS

### Retrieve app version from YAML file ###
def _get_app_version() -> str:
	config_path = "config.yaml"

	try:
		with open(config_path, "r", encoding="utf-8") as config_file:
			for line in config_file:
				stripped = line.strip()
				if stripped.startswith("version:"):
					return stripped.split(":", 1)[1].strip().strip('"\'')
	except (OSError, IndexError):
		pass

	return "unknown"
APP_VERSION = _get_app_version()


### DATABASE ###
# Database version. Used for migrations.
DATABASE_VERSION = 3 # DO NOT CHANGE UNLESS MIGRATIONS ARE NOT WORKING


### ENVIRONMENT ###
# These settings should not be changed unless you are running outside of Home Assistant.

# The URL that Data Dumper calls to get data from Home Assistant.
HASS_API_URL = "http://supervisor/core/api"
# The location of the Frontend static files.
BUILT_FRONTEND_PATH = "/frontend/dist"
# The location for the database file
DATABASE_LOCATION = "/data/radded_data_dumper.sqlite3"


### LOGGING ###
# TODO: Change this to Normal before sharing
# Set your log level
# - INSANE -- Logs all SQL and API queries. Great for development testing, but may LEAK KEYS!
# - NORMAL -- Recommended for all users.
# - SILENT -- Logs only errors and warnings.
LOG_LEVEL = LOG_LEVELS.INSANE

