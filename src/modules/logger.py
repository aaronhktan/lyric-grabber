import datetime

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

  def write_to_file(log):
    with open(utils.resource_path('./modules/info.log'), 'r') as fin:
      data = fin.read().splitlines(False)
    with open(utils.resource_path('./modules/info.log'), 'w') as fout:
      cutoff = 1 if len(data) > 1000 else 0
      data.append(log)
      string = '\n'.join(data[cutoff:])
      fout.write(string)

  def log(log_level, message):
    date = datetime.datetime.now()
    timestamp = '[{:04}-{:02}-{:02} {:02}:{:02}:{:02}]'.format(
      date.year, date.month, date.day,
      date.hour, date.minute, date.second)
    if log_level == logger.LOG_LEVEL_SUCCESS:
      pass
      # print('Success!')
      # print(logger.SUCCESS + '[SUCCESS] ' + logger.RESET + message)
      # logger.write_to_file(timestamp + '[SUCCESS] ' + message)
    elif log_level == logger.LOG_LEVEL_ERROR:
      pass
      # print('Error!')
      # print(logger.ERROR + '[ERROR] ' + logger.RESET + message)
      # logger.write_to_file(timestamp + '[ERROR] ' + message)
    elif log_level == logger.LOG_LEVEL_INFO:
      pass
      # print('Info!')
      # print(logger.INFO + '[INFO] ' + logger.RESET + message)
      # logger.write_to_file(timestamp + '[INFO] ' + message)
    elif log_level == logger.LOG_LEVEL_WARNING:
      pass
      # print('Warning!')
      # print(logger.INFO + '[WARNING] ' + logger.RESET + message)
      # logger.write_to_file(timestamp + '[WARNING] ' + message)

  def create_message(log_level, message):
    if log_level == logger.LOG_LEVEL_SUCCESS:
      # return logger.SUCCESS + '[SUCCESS] ' + logger.RESET + message
      return '[SUCCESS] ' + message
    elif log_level == logger.LOG_LEVEL_ERROR:
      # return logger.ERROR + '[ERROR] ' + logger.RESET + message
      return '[ERROR] ' + message
    elif log_level == logger.LOG_LEVEL_INFO:
      # return logger.INFO + '[INFO] ' + logger.RESET + message
      return '[INFO] ' + message
    elif log_level == logger.LOG_LEVEL_WARNING:
      # return logger.INFO + '[WARNING] ' + logger.RESET + message
      return '[WARNING] ' + message