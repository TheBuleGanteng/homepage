from django.conf import settings
import logging

# Configure logging for this middleware
logger = logging.getLogger(__name__)

class ValidateHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the full value of the host header
        full_host = request.get_host()
        logger.info(f'Full host value: {full_host}')

        # Split host to remove port number if present
        host = full_host.split(':')[0]

        # Log the processed host value
        logger.info(f'Processed host value: {host}')

        # Proceed with the request processing without modifying ALLOWED_HOSTS
        response = self.get_response(request)
        return response
