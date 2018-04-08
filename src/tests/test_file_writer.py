from modules import file_writer

import os
import unittest

class TestFileWrite(unittest.TestCase):
  def test_write_file(self):
    result = file_writer.write_lyrics_to_txt('Testing 123', 'test_file.mp3')
    self.assertEqual(result, True)

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, 'Testing 123')

    os.remove('test_file.txt')

  def test_write_strange_characters(self):
    result = file_writer.write_lyrics_to_txt('qéêàÇïú我的天啊עִבְרִית', 'test_file.mp3')
    self.assertEqual(result, True)

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, 'qéêàÇïú我的天啊עִבְרִית')

    os.remove('test_file.txt')


if __name__ == '__main__':
    unittest.main()