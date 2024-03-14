import os

CSS_CACHE_ENABLED = True
DEBUG = False # Debug must be false for prod
ALLOWED_HOSTS = ['www.mattmcdonnell.net', 'mattmcdonnell.net', '127.0.0.1', 'localhost', '10.148.*'] # Must be set when DEBUG=False

# Logging configurations
LOG_TO_CONSOLE = True
LOG_TO_FILE = True
USE_GOOGLE_CLOUD_LOGGING = True