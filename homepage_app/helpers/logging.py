import os
from django.conf import settings
import logging
from logging.handlers import RotatingFileHandler

# Import Google Cloud logging only if USE_GOOGLE_CLOUD_LOGGING is True to avoid errors in environments without Google Cloud dependencies
if getattr(settings, 'USE_GOOGLE_CLOUD_LOGGING', False):
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler

def configure_logging():
    # Set up logging to file
    if getattr(settings, 'LOG_TO_FILE', False):
        # Define the log file path relative to the BASE_DIR
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'app.log')
        # Ensure the logs directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        file_handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logging.getLogger('').addHandler(file_handler)

    # Set up logging to console
    if getattr(settings, 'LOG_TO_CONSOLE', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        logging.getLogger('').addHandler(console_handler)

    # Configure Google Cloud Logging
    if getattr(settings, 'USE_GOOGLE_CLOUD_LOGGING', False):
        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client)
        handler.setLevel(logging.NOTSET)  # Set the logging level for the handler
        logging.getLogger('').addHandler(handler)

    # Set the overall logging level
    logging.getLogger('').setLevel(logging.DEBUG)
