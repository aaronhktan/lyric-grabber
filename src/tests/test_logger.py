from modules.logger import logger

import unittest

class TestLogger(unittest.TestCase):
  def test_create_success_message(self):
    message = logger.create_message(logger.LOG_LEVEL_SUCCESS, 'Successful message')
    self.assertEqual(message, '\033[32;1m' + '[SUCCESS] ' + '\033[0m' + 'Successful message')

  def test_create_error_message(self):
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Erroneous message')
    self.assertEqual(message, '\033[31;1m' + '[ERROR] ' + '\033[0m' + 'Erroneous message')

  def test_create_info_message(self):
    message = logger.create_message(logger.LOG_LEVEL_INFO, 'Informational message')
    self.assertEqual(message, '\033[93;1m' + '[INFO] ' + '\033[0m' + 'Informational message')

  def test_create_warning_message(self):
    message = logger.create_message(logger.LOG_LEVEL_WARNING, 'Warning message')
    self.assertEqual(message, '\033[93;1m' + '[WARNING] ' + '\033[0m' + 'Warning message')

  def test_create_multiple_message_same(self):
    message_one = logger.create_message(logger.LOG_LEVEL_ERROR, 'Error message')
    message_two = logger.create_message(logger.LOG_LEVEL_ERROR, 'Error message')
    self.assertEqual(message_one, message_two)

if __name__ == '__main__':
  unittest.main()