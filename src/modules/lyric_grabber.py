from collections import namedtuple
import random
import re
import time

from modules import fetcher
from modules import file_writer
from modules.logger import logger
from modules import metadata

AZLYRICS_URL_BASE = 'azlyrics.com'
GENIUS_URL_BASE = 'genius.com'
LYRICSFREAK_URL_BASE = 'lyricsfreak.com'
LYRICWIKI_URL_BASE = 'lyrics.wikia.com'
METROLYRICS_URL_BASE = 'metrolyrics.com'
MUSIXMATCH_URL_BASE = 'musixmatch.com'

LYRICS_TUPLE = namedtuple('lyrics', ['succeeded', 'artist', 'title', 'lyrics', 'url', 'filepath'])
FILE_TUPLE = namedtuple('state', ['succeeded', 'filepath', 'message'])
ERROR_TUPLE = namedtuple('error', ['succeeded', 'message', 'filepath'])

def get_metadata(get_art, song_filepath):
  return metadata.get_metadata(get_art, song_filepath)

def get_lyrics(approximate, keep_brackets, artist, title, source, song_filepath):

  request_artist = artist
  request_title = title

  if approximate and source != 'lyricwiki' and source != 'metrolyrics':
    request_artist = ''
  if not keep_brackets:
    request_artist = re.sub(r'\((.+)\)', '', request_artist).strip()
    request_title = re.sub(r'\((.+)\)', '', request_title).strip()

  try:
    if source == 'azlyrics':
      time_to_sleep = random.randrange(10, 30)
      time.sleep(time_to_sleep)
      result = fetcher.azlyrics_search_and_scrape_url(request_artist, request_title)
    elif source == 'genius':
      result = fetcher.genius_search_and_scrape_url(request_artist, request_title)
    elif source == 'lyricsfreak':
      result = fetcher.lyricsfreak_search_and_scrape_url(request_title)
    elif source == 'lyricwiki':
      result = fetcher.lyricwiki_search_and_scrape_url(request_artist, request_title)
    elif source == 'metrolyrics':
      result = fetcher.metrolyrics_search_and_scrape_url(request_artist, request_title)
    elif source == 'musixmatch':
      time_to_sleep = random.randrange(10, 30)
      time.sleep(time_to_sleep)
      result = fetcher.musixmatch_search_and_scrape_url(request_artist, request_title)
    else:
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Source not valid! (choose from \'azlyrics\', \'genius\', \'lyricsfreak\', \'lyricwiki\', \'metrolyrics\', \'musixmatch\')')
      return ERROR_TUPLE(False, message, song_filepath)

    if (result is not False):
      lyrics = result.lyrics
      url = result.url
      return LYRICS_TUPLE(True, artist, title, lyrics, url, song_filepath)
    else:
      message = logger.create_message(logger.LOG_LEVEL_INFO, 'No lyrics found for {file}!'.format(file=title))
      return ERROR_TUPLE(False, message, song_filepath)
  except Exception as e:
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Something went horribly wrong getting lyrics for {file}! Error: {error}'.format(file=title, error=e))
    return ERROR_TUPLE(False, message, song_filepath)

def scrape_url(artist, title, url, song_filepath):
  try:
    if AZLYRICS_URL_BASE in url:
      result = fetcher.azlyrics_scrape_url(url, title)
    elif GENIUS_URL_BASE in url:
      result = fetcher.genius_scrape_url(url, title)
    elif LYRICSFREAK_URL_BASE in url:
      result = fetcher.lyricsfreak_scrape_url(url, title)
    elif LYRICWIKI_URL_BASE in url:
      result = fetcher.lyricwiki_scrape_url(url, title)
    elif METROLYRICS_URL_BASE in url:
      result = fetcher.metrolyrics_scrape_url(url, title)
    elif MUSIXMATCH_URL_BASE in url:
      result = fetcher.musixmatch_scrape_url(url, title)
    else:
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Source not valid! (make sure you have a URL from \'AZLyrics\', \'Genius\', \'Lyricsfreak\', \'Lyricwiki\', \'Metrolyrics\', or \'Musixmatch\')')
      return ERROR_TUPLE(False, message, song_filepath)

    if (result is not False):
      lyrics = result.lyrics
      url = result.url
      return LYRICS_TUPLE(True, artist, title, lyrics, url, song_filepath)
    else:
      message = logger.create_message(logger.LOG_LEVEL_INFO, 'No lyrics found for {file}!'.format(file=title))
      return ERROR_TUPLE(False, message, song_filepath)
  except Exception as e:
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Something went horribly wrong getting lyrics for {file}! Error: {error}'.format(file=title, error=e))
    return ERROR_TUPLE(False, message, song_filepath)

def write_file(artist, title, write_info, write_metadata, write_text, lyrics, song_filepath):
  try:
    if lyrics:
      if write_info:
        lyrics = artist + ' - ' + title + '\n\n' + lyrics
      if write_metadata:
        metadata.write_lyrics_to_file(lyrics, song_filepath)
      if write_text:
        file_writer.write_lyrics_to_txt(lyrics, song_filepath)
    else:
      message = logger.create_message(logger.LOG_LEVEL_INFO, 'No lyrics found for file: {file}'.format(file=title))
      return FILE_TUPLE(True, song_filepath, message)
  except Exception as e:
    logger.log(logger.LOG_LEVEL_ERROR, str(e))

  message = logger.create_message(logger.LOG_LEVEL_SUCCESS, 'Got lyrics for file: {file}'.format(file=title))
  return FILE_TUPLE(True, song_filepath, message)