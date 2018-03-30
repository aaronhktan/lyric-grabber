from modules import lyric_fetcher

import unittest

class TestAZLyrics(unittest.TestCase):
  def test_azlyrics_get_lyrics(self):
    result = lyric_fetcher.AZLyrics_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_azlyrics_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.AZLyrics_get_lyrics('Title')

  def test_azlyrics_nonexistent_title(self):
    result = lyric_fetcher.AZLyrics_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestGenius(unittest.TestCase):
  def test_genius_get_lyrics(self):
    result = lyric_fetcher.Genius_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_genius_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.Genius_get_lyrics('Shake it Off')

  def test_genius_nonexistent_title(self):
    result = lyric_fetcher.Genius_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestLyricsFreak(unittest.TestCase):
  def test_lyricsfreak_get_lyrics(self):
    result = lyric_fetcher.LyricsFreak_get_lyrics('Shake It Off')
    self.assertNotEqual(result, False)

  def test_lyricwiki_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.LyricsFreak_get_lyrics('Taylor Swift', 'Shake It Off')

  def test_azlyrics_nonexistent_title(self):
    result = lyric_fetcher.LyricsFreak_get_lyrics('thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestLyricWiki(unittest.TestCase):
  def test_lyricwiki_get_lyrics(self):
    result = lyric_fetcher.LyricWiki_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_lyricwiki_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.LyricWiki_get_lyrics('Shake It Off')

  def test_lyricwiki_nonexistent_title(self):
    result = lyric_fetcher.LyricWiki_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestMetrolyrics(unittest.TestCase):
  def test_metrolyrics_get_lyrics(self):
    result = lyric_fetcher.Metrolyrics_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_metrolyrics_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.Metrolyrics_get_lyrics('Title')

  def test_metrolyrics_nonexistent_title(self):
    result = lyric_fetcher.Metrolyrics_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestMusixmatch(unittest.TestCase):
  def test_musixmatch_get_lyrics(self):
    result = lyric_fetcher.Musixmatch_get_lyrics('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_musixmatch_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = lyric_fetcher.Musixmatch_get_lyrics('Title')

  def test_musixmatch_nonexistent_title(self):
    result = lyric_fetcher.Musixmatch_get_lyrics('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()