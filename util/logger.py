import logging
from logging.handlers import TimedRotatingFileHandler
import os
log_name = 'logs/execution.log'

if not os.path.exists('logs'):
    os.makedirs('logs')

log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = TimedRotatingFileHandler(log_name, when='D', interval=1, backupCount=1, encoding='utf-8', delay=False)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO
                    , format='%(asctime)s - %(levelname)s - %(message)s')

log = logging.getLogger('my_logger')
file_handler.doRollover()
log.addHandler(file_handler)

#log.addHandler(console_handler)


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

    def exception(self, message):
        log.exception('[{}] {} '.format(self.class_name, message))
