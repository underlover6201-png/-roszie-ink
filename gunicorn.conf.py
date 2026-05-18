"""Gunicorn 生產設定"""
import multiprocessing

# Worker 數量 = CPU 核心 x 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

bind = "0.0.0.0:8000"
user = "www-data"
group = "www-data"

# 日誌
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 效能
preload_app = True
max_requests = 1000
max_requests_jitter = 100
