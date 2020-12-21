import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

from sqlalchemy import create_engine

from bottex2.platforms.tg import TgTransport
from bottex2.platforms.vk import VkTransport

from bottex2.ext.logging import Logging
from bottex2.ext.users import Users
from bottex2.sqlalchemy import SQLAlchemy
from bottex2.logging import logger
from bottex2.server import Server

from test_app import logic
from schedule import configs


logger.setLevel(logging.DEBUG)
logging = Logging(logger)

engine = create_engine(configs.db_url)
db = SQLAlchemy(engine)
users = Users(db)


def main():
    transports = [
        TgTransport(token=configs.tg.token),
        VkTransport(token=configs.vk.token, group_id=configs.vk.group_id),
    ]
    middlewares = [
        users.Middleware,
        logging.Middleware
    ]
    bottex = Server(transports, logic.router, middlewares)
    bottex.serve_forever()


if __name__ == '__main__':
    main()
