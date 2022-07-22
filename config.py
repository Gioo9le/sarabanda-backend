import configparser
import os

F_HOSTNAME = os.environ.get('F_HOSTNAME', "http://localhost:3000")
B_HOSTNAME = os.environ.get('B_HOSTNAME', "http://localhost:5000")
REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/4")
