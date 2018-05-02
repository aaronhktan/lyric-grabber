from modules import utils

class logger:

  ERROR = '\033[31;1m' if utils.IS_MAC else ''
  INFO = '\033[93;1m' if utils.IS_MAC else ''
  RESET = '\033[0m' if utils.IS_MAC else ''
  SUCCESS = '\033[32;1m' if utils.IS_MAC else ''

  LOG_LEVEL_SUCCESS = 0
  LOG_LEVEL_ERROR = 1
  LOG_LEVEL_INFO = 2
  LOG_LEVEL_WARNING = 3

  def log(log_level, message):
    if log_level == logger.LOG_LEVEL_SUCCESS:
      pass
      # print('Success!')
      # print(logger.SUCCESS + '[SUCCESS] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_ERROR:
      pass
      # print('Error!')
      # print(logger.ERROR + '[ERROR] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_INFO:
      pass
      # print('Info!')
      # print(logger.INFO + '[INFO] ' + logger.RESET + message)
    elif log_level == logger.LOG_LEVEL_WARNING:
      pass
      # print('Warning!')
      # print(logger.INFO + '[WARNING] ' + logger.RESET + message)

  def create_message(log_level, message):
    if log_level == logger.LOG_LEVEL_SUCCESS:
      return logger.SUCCESS + '[SUCCESS] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_ERROR:
      return logger.ERROR + '[ERROR] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_INFO:
      return logger.INFO + '[INFO] ' + logger.RESET + message
    elif log_level == logger.LOG_LEVEL_WARNING:
      return logger.INFO + '[WARNING] ' + logger.RESET + message