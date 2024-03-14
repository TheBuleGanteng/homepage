import multiprocessing

# The socket to bind
bind = "0.0.0.0:8000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
# 'sync', 'gthread', 'gevent', 'eventlet' are some of the options
# Depending on your application's I/O profile, you might want to experiment with 'gthread' or 'gevent'
worker_class = 'sync'

# Max number of requests a worker will process before restarting
# This can help prevent memory leaks
max_requests = 1000

# How many seconds to wait for the next request on a Keep-Alive HTTP connection
keepalive = 5

# Amount of time a worker will wait for a connection
timeout = 60

# If you're still experiencing timeouts, consider increasing this value

# Log level
# Increasing log level can help diagnose issues; consider setting it to 'debug' temporarily
loglevel = 'debug'

# Path to log file
# Make sure the 'logs' directory exists or adjust the path as necessary
logfile = '/path/to/your/project/logs/gunicorn.log'

# Access log - consider enabling during debugging
accesslog = '/path/to/your/project/logs/access.log'

# Error log
errorlog = '/path/to/your/project/logs/error.log'

# Use this setting to prevent data loss on worker restart
preload_app = False
