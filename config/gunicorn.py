import multiprocessing
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

NAME = BASE_DIR.name
PREF = BASE_DIR.parent.name

chdir = BASE_DIR
# workers = multiprocessing.cpu_count() * 2 + 1
threads = multiprocessing.cpu_count() * 2 + 1
wsgi_app = 'main:app'
proc_name = f'{NAME} gunner'
worker_class = 'uvicorn.workers.UvicornWorker'
venv = '.env/bin/activate'
bind = f'unix:///usr/share/nginx/sockets/{PREF}_{NAME}.sock'
loglevel = 'info'
accesslog = f'/var/log/{PREF}/{NAME}/access.log'
acceslogformat = '%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s'
errorlog = f'/var/log/{PREF}/{NAME}/error.log'
