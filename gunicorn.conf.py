import os

bind = '0.0.0.0:80'
workers = 1
backlog = 2048
worker_class = "gevent"
daemon = False
debug = True
proc_name = 'gunicorn.proc'
pidfile = '/tmp/gunicorn.pid'
logfile = '/root/gunicorn/debug.log'
loglevel = 'debug'