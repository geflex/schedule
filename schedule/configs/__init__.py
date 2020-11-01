from . import tg, vk
import os
import datetime


time_started = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
host = os.environ.get('HOST', None)
db_url = os.environ.get('DATABASE_URL')
