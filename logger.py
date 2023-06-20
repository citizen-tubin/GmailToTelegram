import logging
import configparser
import ast

config = configparser.ConfigParser()
config.read('.ini')
log_dir = ast.literal_eval(config.get('SYSTEM', 'LOG_DIR'))
log_level = ast.literal_eval(config.get('SYSTEM', 'LOG_LEVEL'))

log_format = '%(asctime)s %(levelname)s: %(message)s'

logging.basicConfig(filename=log_dir, level=log_level, format=log_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format))

app_logger = logging.getLogger(__name__)
app_logger.addHandler(console_handler)
