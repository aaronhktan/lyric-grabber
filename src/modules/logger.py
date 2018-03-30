class logger:

  ERROR = '\033[31;1m'
  INFO = '\033[93;1m'
  RESET = '\033[0m'
  SUCCESS = '\033[32;1m'

  LOG_LEVEL_SUCCESS = 0
  LOG_LEVEL_ERROR = 1
  LOG_LEVEL_INFO = 2
  LOG_LEVEL_WARNING = 3

  def log(log_level, message):
    if log_level == logger.LOG_LEVEL_SUCCESS:
      print(logger.SUCCESSS + '[SUCCESS] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_ERROR:
      print(logger.ERROR + '[ERROR] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_INFO:
      print(logger.INFO + '[INFO] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_WARNING:
      print(logger.INFO + '[WARNING] ' + logger.RESET + message)

  def create_message(log_level, message):
    if log_level == logger.LOG_LEVEL_SUCCESS:
      return logger.SUCCESS + '[SUCCESS] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_ERROR:
      return logger.ERROR + '[ERROR] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_INFO:
      return logger.INFO + '[INFO] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_WARNING:
      return logger.INFO + '[WARNING] ' + logger.RESET + message