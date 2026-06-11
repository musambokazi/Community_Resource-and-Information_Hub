import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = "0.0.0.0:8000"

# ── Workers ───────────────────────────────────────────────────────────────────
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2

# ── Timeout / Keep-alive ──────────────────────────────────────────────────────
timeout = 30
keepalive = 5
graceful_timeout = 30

# ── Logging (relative to backend/ working dir) ────────────────────────────────
errorlog  = "../logs/error.log"
accesslog = "../logs/access.log"
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# ── Security ──────────────────────────────────────────────────────────────────
limit_request_line        = 4094
limit_request_fields      = 100
limit_request_field_size  = 8190

# ── Process naming ────────────────────────────────────────────────────────────
proc_name = "community_hub"
