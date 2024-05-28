# This file was added to work with the templates folder in /brokerage and /users to ensure the most recent version of the JS file is used.

from django.conf import settings

def static_version(request):
    return {
        'STATIC_VERSION': settings.STATIC_VERSION,
    }
