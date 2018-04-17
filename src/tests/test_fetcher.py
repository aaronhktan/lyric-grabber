import unittest

from modules import fetcher

class TestAZLyrics(unittest.TestCase):
  def test_azlyrics_get_lyrics(self):
    result = fetcher.azlyrics_search_and_scrape_url('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_azlyrics_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.azlyrics_search_and_scrape_url('Title')

  def test_azlyrics_nonexistent_title(self):
    result = fetcher.azlyrics_search_and_scrape_url('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestGenius(unittest.TestCase):
  def test_genius_get_lyrics(self):
    result = fetcher.genius_search_and_scrape_url('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_genius_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.genius_search_and_scrape_url('Shake it Off')

  def test_genius_nonexistent_title(self):
    result = fetcher.genius_search_and_scrape_url('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestLyricsFreak(unittest.TestCase):
  def test_lyricsfreak_get_lyrics(self):
    result = fetcher.lyricsfreak_search_and_scrape_url('Shake It Off')
    self.assertNotEqual(result, False)

  def test_lyricwiki_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.lyricsfreak_search_and_scrape_url('Taylor Swift', 'Shake It Off')

  def test_azlyrics_nonexistent_title(self):
    result = fetcher.lyricsfreak_search_and_scrape_url('thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestLyricWiki(unittest.TestCase):
  def test_lyricwiki_get_lyrics(self):
    result = fetcher.lyricwiki_search_and_scrape_url('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_lyricwiki_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.lyricwiki_search_and_scrape_url('Shake It Off')

  def test_lyricwiki_nonexistent_title(self):
    result = fetcher.lyricwiki_search_and_scrape_url('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestMetrolyrics(unittest.TestCase):
  def test_metrolyrics_get_lyrics(self):
    result = fetcher.metrolyrics_search_and_scrape_url('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_metrolyrics_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.metrolyrics_search_and_scrape_url('Title')

  def test_metrolyrics_nonexistent_title(self):
    result = fetcher.metrolyrics_search_and_scrape_url('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

class TestMusixmatch(unittest.TestCase):
  def test_musixmatch_get_lyrics(self):
    result = fetcher.musixmatch_search_and_scrape_url('Taylor Swift', 'Shake It Off')
    self.assertNotEqual(result, False)

  def test_musixmatch_incorrect_parameters(self):
    with self.assertRaises(TypeError):
      result = fetcher.musixmatch_search_and_scrape_url('Title')

  def test_musixmatch_nonexistent_title(self):
    result = fetcher.musixmatch_search_and_scrape_url('Aaron', 'thissongshouldn\'texist')
    self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()