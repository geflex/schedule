import logging
import pymongo.monitoring


class MongoLogger(pymongo.monitoring.CommandListener):
    logger = logging.getLogger('mongo')

    def started(self, event):
        self.logger.debug('Command {0.command_name} with request id '
                          '{0.request_id} started on _serve_async '
                          '{0.connection_id}'.format(event))

    def succeeded(self, event):
        self.logger.debug('Command {0.command_name} with request id '
                          '{0.request_id} on _serve_async {0.connection_id} '
                          'succeeded in {0.duration_micros} '
                          'microseconds'.format(event))

    def failed(self, event):
        self.logger.debug('Command {0.command_name} with request id '
                          '{0.request_id} on _serve_async {0.connection_id} '
                          'failed in {0.duration_micros} '
                          'microseconds'.format(event))

def setup_mongo_logging(level):
    pymongo.monitoring.register(MongoLogger())
