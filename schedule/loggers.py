import sys
import pymongo.monitoring
import bottex


class MongoLogger(pymongo.monitoring.CommandListener):
    logger = bottex.logging.get_logger('mongo')

    def started(self, event):
        self.logger.debug("Command {0.command_name} with request id "
                          "{0.request_id} started on server "
                          "{0.connection_id}".format(event))

    def succeeded(self, event):
        self.logger.debug("Command {0.command_name} with request id "
                          "{0.request_id} on server {0.connection_id} "
                          "succeeded in {0.duration_micros} "
                          "microseconds".format(event))

    def failed(self, event):
        self.logger.debug("Command {0.command_name} with request id "
                          "{0.request_id} on server {0.connection_id} "
                          "failed in {0.duration_micros} "
                          "microseconds".format(event))


def setup_logging(level):
    pymongo.monitoring.register(MongoLogger())
    bottex.logging.add_splitted(sys.stdout, sys.stderr)
    # bottex.logging.add_splitted('logs/debug.log', 'logs/errors.log')
    bottex.logging.set_level(level)
    bottex.logging.set_default_format()
