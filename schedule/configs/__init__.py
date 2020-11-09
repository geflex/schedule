import datetime
import os

from . import tg, vk

time_started = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
host = os.environ['HOST']
db_url = os.environ['DATABASE_URL']
