import os

PROJECT_PATH = os.path.dirname(__file__)
os.makedirs(os.path.join(PROJECT_PATH, 'logs'), exist_ok=True)

bind = "{host}:{port}".format(host='127.0.0.1', port=29606)

workers = 1
# worker_class = 'eventlet'
proc_name = "darioflat"
errorlog = os.path.join(PROJECT_PATH, 'logs', 'gerror.log')
accesslog = os.path.join(PROJECT_PATH, 'logs', 'gaccess.log')
