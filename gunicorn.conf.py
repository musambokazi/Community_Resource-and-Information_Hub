import multiprocessing

# Bind to localhost port 8000
bind = "127.0.0.1:8000"

# Workers optimized for Flask (Sync workers are standard, gevent is better for IO bound)
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Timeout and keepalive
timeout = 30
keepalive = 2

# Logging
errorlog = "logs/error.log"
accesslog = "logs/access.log"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
