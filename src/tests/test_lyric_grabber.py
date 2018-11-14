import unittest
from collections import namedtuple
import os

from modules import lyric_grabber

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
    result = lyric_grabber.get_lyrics(approximate=self.approximate,
                                      keep_brackets=self.keep_brackets,
                                      artist='Aaron',
                                      title='A Song',
                                      source='A source that doesn\'t exist',
                                      song_filepath='filepath.mp3')
    self.assertFalse(result.succeeded)
    self.assertEqual(result.message, '[ERROR] ' + 'Source not valid! (choose from \'azlyrics\', \'genius\', \'lyricsfreak\', \'lyricwiki\', \'metrolyrics\', \'musixmatch\')')
    self.assertEqual(result.filepath, 'filepath.mp3')

  def test_get_lyrics(self):
    result = lyric_grabber.get_lyrics(approximate=self.approximate,
                                      keep_brackets=self.keep_brackets,
                                      artist='Portugal. The Man',
                                      title='Feel It Still',
                                      source='genius',
                                      song_filepath='filepath.mp3')
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

  def test_write_metadata(self):
    write_info = True
    write_metadata = False
    write_text = True
    result = lyric_grabber.write_file(artist=self.artist,
                                      title=self.title,
                                      write_info=write_info,
                                      write_metadata=write_metadata,
                                      write_text=write_text,
                                      lyrics=self.lyrics,
                                      song_filepath=self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, self.filepath)
    self.assertEqual(result.message, '[SUCCESS] ' + 'Got lyrics for file: {file}'.format(file=self.title))

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, self.artist + ' - ' + self.title + '\n\n' + self.lyrics)

    os.remove('test_file.txt')

  def test_not_write_info(self):
    write_info = False
    write_metadata = False
    write_text = True
    result = lyric_grabber.write_file(artist=self.artist,
                                      title=self.title,
                                      write_info=write_info,
                                      write_metadata=write_metadata,
                                      write_text=write_text,
                                      lyrics=self.lyrics,
                                      song_filepath=self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, self.filepath)
    self.assertEqual(result.message, '[SUCCESS] ' + 'Got lyrics for file: {file}'.format(file=self.title))

    file = open('test_file.mp3'[:'test_file.mp3'.rfind('.')] + '.txt', 'r')
    result = file.read()
    file.close()
    self.assertEqual(result, self.lyrics)

    os.remove('test_file.txt')

  def test_no_lyrics(self):
    write_info = True
    write_metadata = False
    write_text = True
    lyrics = False
    result = lyric_grabber.write_file(artist=self.artist,
                                      title=self.title,
                                      write_info=write_info,
                                      write_metadata=write_metadata,
                                      write_text=write_text,
                                      lyrics=lyrics,
                                      song_filepath=self.filepath)
    self.assertTrue(result.succeeded)
    self.assertEqual(result.filepath, 'test_file.mp3')
    self.assertEqual(result.message, '[INFO] ' + 'No lyrics found for file: {file}'.format(file=self.title))

if __name__ == '__main__':
  unittest.main()