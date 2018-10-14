from concurrent import futures
import threading

try:
  from PyQt5 import QtCore
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from modules.logger import logger
from modules import lyric_grabber
from modules import settings
from threads.states import states

class SingleLyricGrabberThread (QtCore.QThread):
  setProgressIcon = QtCore.pyqtSignal(int)
  setLyrics = QtCore.pyqtSignal('QString')
  setUrl = QtCore.pyqtSignal('QString')
  lock = threading.Lock()

  def __init__(self, parent, filepath, artist=None, title=None, url=None, source=None):
    super().__init__()

    self._filepath = filepath
    self._artist = artist
    self._title = title
    self._url = url
    self._source = source

    self._settings = settings.Settings()
    self.setProgressIcon.emit(states.NOT_STARTED)

  def run(self):
    self.setProgressIcon.emit(states.IN_PROGRESS)
    with SingleLyricGrabberThread.lock:
      try:
        if self._url is not None: # We have a URL, so scrape the URL
          result = lyric_grabber.scrape_url(artist=self._artist,
                                            title=self._title,
                                            url=self._url,
                                            song_filepath=self._filepath)
        else: # No URL, so fetch based on artist and title
          result = lyric_grabber.get_lyrics(approximate=self._settings.approximate,
                                            keep_brackets=not self._settings.remove_brackets,
                                            artist=self._artist,
                                            title=self._title,
                                            source=self._source.lower(),
                                            song_filepath=self._filepath)

        if result.succeeded:
          self.setUrl.emit(result.url)
          self.setLyrics.emit(result.lyrics)
          result = lyric_grabber.write_file(artist=self._artist,
                                            title=self._title,
                                            write_info=self._settings.info,
                                            write_metadata=self._settings.metadata,
                                            write_text=self._settings.text,
                                            lyrics=result.lyrics,
                                            song_filepath=self._filepath)
          logger.log(logger.LOG_LEVEL_SUCCESS, result.message)
          self.setProgressIcon.emit(states.COMPLETE)
        else:
          self.setProgressIcon.emit(states.ERROR)
        # print(result.lyrics)
      except Exception as e:
        logger.log(logger.LOG_LEVEL_ERROR,
                   ' Exception occurred while getting lyrics for file {filepath}: {error}'.format(self._filepath,
                                                                                                  error=str(e)))