from modules import lyric_grabber

import unittest
from collections import namedtuple
import os

class TestMetadata(unittest.TestCase):

  def test_valid_mp3(self):
    get_art = True
    filepath = 'tests/test_files/Re_Your_Brains.mp3'
    result = lyric_grabber.get_metadata(get_art, filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.artist, 'Jonathan Coulton')
    self.assertEqual(result.title, 'Re: Your Brains')
    self.assertIsNotNone(result.art)
    self.assertEqual(result.filepath, filepath)

class TestGetLyrics(unittest.TestCase):
  approximate = False
  keep_brackets = True

  def test_invalid_source(self):
    result = lyric_grabber.get_lyrics(self.approximate, self.keep_brackets, 'Aaron', 'A Song', 'A source that doesn\'t exist', 'filepath.mp3')
    self.assertFalse(result.succeeded)
    self.assertEqual(result.message, '\033[31;1m' + '[ERROR] ' + '\033[0m' + 'Source not valid! (choose from \'azlyrics\', \'genius\', \'lyricsfreak\', \'lyricwiki\', \'metrolyrics\', \'musixmatch\')')
    self.assertEqual(result.filepath, 'filepath.mp3')

  def test_get_lyrics(self):
    result = lyric_grabber.get_lyrics(self.approximate, self.keep_brackets, 'Portugal. The Man', 'Feel It Still', 'genius', 'filepath.mp3')
    self.assertTrue(result.succeeded)
    self.assertEqual(result.artist, 'Portugal. The Man')
    self.assertEqual(result.title, 'Feel It Still')
    self.assertIsNotNone(result.lyrics)
    self.assertIsNot(result.lyrics, False)
    self.assertEqual(result.filepath ,'filepath.mp3')

class TestWriteFile(unittest.TestCase):
  artist = 'Natalia Lafourcade'
  title = 'Tú sí sabes quererme'
  lyrics = 'Corazón, tú sí sabes / Quererme como a mí me gusta'
  filepath = 'test_file.mp3'

  def test_write_info(self):
    write_info = True
    result = lyric_grabber.write_file(self.artist, self.title, write_info, self.lyrics, self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, self.filepath)
    self.assertEqual(result.message, '\033[32;1m' + '[SUCCESS] ' + '\033[0m' + 'Got lyrics for file: {file}'.format(file=self.title))

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, self.artist + ' - ' + self.title + '\n\n' + self.lyrics)

    os.remove('test_file.txt')

  def test_not_write_info(self):
    write_info = False
    result = lyric_grabber.write_file(self.artist, self.title, write_info, self.lyrics, self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, self.filepath)
    self.assertEqual(result.message, '\033[32;1m' + '[SUCCESS] ' + '\033[0m' + 'Got lyrics for file: {file}'.format(file=self.title))

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, self.lyrics)

    os.remove('test_file.txt')

  def test_no_lyrics(self):
    write_info = True
    lyrics = False
    result = lyric_grabber.write_file(self.artist, self.title, write_info, lyrics, self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, 'test_file.mp3')
    self.assertEqual(result.message, '\033[93;1m' + '[INFO] ' + '\033[0m' + 'No lyrics found for file: {file}'.format(file=self.title))

if __name__ == '__main__':
  unittest.main()