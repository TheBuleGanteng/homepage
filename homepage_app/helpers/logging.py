import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings

def setup_logging():
    # Set up logging to file
    if getattr(settings, 'LOG_TO_FILE', False):
        file_handler = RotatingFileHandler(settings.LOG_FILE_PATH, maxBytes=10000, backupCount=1)
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

    logging.getLogger('').setLevel(logging.INFO)
