"""Constants for the myFlight Home Assistant integration."""

DOMAIN = "myflight"

CONF_API_KEY = "api_key"
CONF_USERNAME = "username"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_AIRPORT = "airport"
CONF_TRACK_REGISTRATION = "track_registration"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 60

API_STATUS_PATH = "/api/ha/status"
API_PUSH_PATH = "/api/ha/push"

SERVICE_REFRESH = "refresh"
