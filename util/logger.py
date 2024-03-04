import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger('my_logger')


class Log:
    def __init__(self, class_name):
        self.class_name = class_name

    def get_name(self):
        return self.class_name

    def info(self, message):
        log.info('[{}] {} '.format(self.class_name, message))

    def error(self, message):
        log.error('[{}] {} '.format(self.class_name, message))

    def warning(self, message):
        log.warning('[{}] {} '.format(self.class_name, message))
