import requests
import os
from datetime import timedelta
from util import log
from util.placeholders import *
import json
from time import sleep


class HomeAssistantAPI:
    def __init__(self):
        ### Initialize connection with Home Assistant API
        log.info("Connecting to Home Assistant API...")

        # Retrieve API key from environment variables
        log.info("Retrieving API key from environment variables...")
        self.__API_TOKEN = None
        try:
            self.__API_TOKEN = os.environ["SUPERVISOR_TOKEN"]
            log.toomuchinfo(f"Your API token is: {self.__API_TOKEN}")
            log.info("Token recieved!")
        except KeyError as e:
            log.error("Token not provided through environment variables. This is expected if you are not running this application within Home Assistant.")
            raise e
        
        # Test connection
        self.conntest()
        
        
    # Tests the API connection to Home Assistant.
    def conntest(self):
        log.info("Testing connection to Home Assistant...")
        count = 0
        while count < 5:
            conntest = self.__request("/")
            if conntest.status_code != 200:
                if count < 5:
                    log.error(f"Connection test to Home Assistant failed! Error {conntest.status_code}. Retrying...")
                    sleep(10)
                    count += 1
                    continue
                else:
                    log.error(f"Connection test to Home Assistant failed! Error {conntest.status_code}.")
                    raise ConnectionError()
            else:
                # Success!
                break
        
        
    # Retrieves a JSON logbook from a specified time range.
    # Formatted as a List of Log objects. See previous notes for the structure of log objects
    def retrieve_log(self, end_time, start_time=None):
        # If the start time is not specified, select 1 day before the end_time
        if not start_time:
            start_time = end_time - timedelta(days=1)

        # Make the request
        log.info(f"Retrieving logs from {start_time.isoformat()} to {end_time.isoformat()}")
        path = f"/logbook/{start_time.isoformat()}?end_time={end_time.isoformat()}"
        request = self.__request(path)

        # Convert the json content and return
        try:
            return json.loads(request.content)
        except json.decoder.JSONDecodeError:
            log.error("Recieved invalid JSON during log retrieval.")
    
            
    # Retrieves the user's list of configured entities.
    def retrieve_entities(self):
        # Make the request
        log.info("Retrieving entity list")
        path = "/states"
        request = self.__request(path)

        try:
            states = json.loads(request.content)
        except json.decoder.JSONDecodeError:
            log.error("Recieved invalid JSON during entity retrieval.")
            return []
        
        # Bit of error checking
        if not isinstance(states, list):
            log.error("Recieved an invalid entity list during entity retrieval.")
            return []

        # Return the list of entity IDs, along with their friendly name, and icon or entity picture if available
        # If there is neither, the icon can be inferred from the entity type
        result = []
        for state in states:
            item = {
                'entity_id': state['entity_id'],
                'friendly_name': state['attributes']['friendly_name']
            }
            # See if there's an icon
            try:
                item['icon'] = state['attributes']['icon']
            except KeyError:
                pass
            # See if there's an entity picture
            try:
                item['entity_picture'] = state['attributes']['entity_picture']
            except KeyError:
                pass
        
        return result


    # Make an API request. This function call allows extra things to be ran when making API calls like the logger.
    def __request(self, path):
        log.toomuchinfo(f"Sending API request: {path}")
        
        # Make the request with token
        request = requests.get(
            HASS_API_URL + path,
            headers = {
                'Authorization': f'Bearer {self.__API_TOKEN}',
                'Content-Type': 'application/json'
            }
        )
        
        # Log response
        try:
            log.toomuchinfo(f"Response: {request.status_code}, {request.content}")
        except AttributeError:
            log.toomuchinfo(f"Response: {request.status_code}, No body")
        
        # Raise warning if response code is not 200 ok
        if request.status_code != 200:
            log.warning(f"Request to Home Assistant failed! Error {request.status_code}")
            # raise ConnectionError()
            
        return request