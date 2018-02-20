import lyric_grabber

import unittest

class TestAZLyrics(unittest.TestCase):
  def test_azlyrics_get_lyrics(self):
    result = lyric_grabber.AZLyrics_get_lyrics('Shake It Off')
    self.assertNotEqual(result, False)

  def test_azlyrics_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_grabber.AZLyrics_get_lyrics('Artist', 'Title')

  def test_azlyrics_nonexistent_title(self):
    result = lyric_grabber.AZLyrics_get_lyrics('thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestLyricWiki(unittest.TestCase):
  def test_lyricwiki_get_lyrics(self):
    result = lyric_grabber.LyricWiki_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_lyricwiki_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_grabber.LyricWiki_get_lyrics('Shake It Off')

  def test_azlyrics_nonexistent_title(self):
    result = lyric_grabber.LyricWiki_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestMusixmatch(unittest.TestCase):
  def test_musixmatch_get_lyrics(self):
    result = lyric_grabber.Musixmatch_get_lyrics('Shake It Off')
    self.assertNotEqual(result, False)

  def test_musixmatch_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_grabber.Musixmatch_get_lyrics('Artist', 'Title')

  def test_musixmatch_nonexistent_title(self):
    result = lyric_grabber.Musixmatch_get_lyrics('thissongshouldn\'texist')
    self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()