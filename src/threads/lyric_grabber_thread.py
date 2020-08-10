from concurrent import futures

try:
  from PyQt5 import QtCore
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from modules.logger import logger
from modules import lyric_grabber
from modules import settings
from threads.states import states

class LyricGrabberThread (QtCore.QThread):
  addFileToList = QtCore.pyqtSignal(['QString', 'QString', bytes, 'QString'])
  notifyComplete = QtCore.pyqtSignal(bool)
  notifyNoMetadata = QtCore.pyqtSignal(list)
  setLyrics = QtCore.pyqtSignal(['QString', 'QString', 'QString'])
  setProgressIcon = QtCore.pyqtSignal(['QString', int])
  interrupt = False

  def __init__(self, parent, filepaths):
    super().__init__()
    self._filepaths = filepaths

    self._settings = settings.Settings()

    self._metadataExecutor = futures.ThreadPoolExecutor(max_workers=20)
    if self._settings.source == 'azlyrics' or self._settings.source == 'musixmatch':
      self._lyricsExecutor = futures.ThreadPoolExecutor(max_workers=2)
    else:
      self._lyricsExecutor = futures.ThreadPoolExecutor(max_workers=10)
    self._fileWritingExecutor = futures.ThreadPoolExecutor(max_workers=10)

    self._metadataResults = []
    self._lyricsResults = []
    self._fileWritingResults = []

    self._songs = []

  def run(self):
    for filepath in self._filepaths:
      self._metadataResults.append(self._metadataExecutor.submit(lyric_grabber.get_metadata,
                                                                 get_art=True,
                                                                 song_filepath=filepath))

    # Create and show items in list as metadata finishes fetching
    for result in futures.as_completed(self._metadataResults):
      try:
        if result.result().succeeded:
          if result.result().art is None:
            self.addFileToList.emit(result.result().artist,
                                    result.result().title,
                                    b'',
                                    result.result().filepath)
          else:
            self.addFileToList.emit(result.result().artist,
                                    result.result().title,
                                    result.result().art,
                                    result.result().filepath)
          self._songs.append(result.result())
        else:
          if not LyricGrabberThread.interrupt:
            self.notifyNoMetadata.emit([result.result().filepath])
          logger.log(logger.LOG_LEVEL_INFO, 'No metadata found: ' + result.result().message)
      except Exception as e:
        if not LyricGrabberThread.interrupt:
          self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        logger.log(logger.LOG_LEVEL_ERROR, 
                   ' Exception occurred while adding file {filepath}: {error}'.format(filepath=result.result().filepath,
                                                                                      error=str(e)))

    for song in self._songs:
      if LyricGrabberThread.interrupt:
        self.exit()
        return
      self.setProgressIcon.emit(result.result().filepath, states.IN_PROGRESS)
      self._lyricsResults.append(self._lyricsExecutor.submit(lyric_grabber.get_lyrics,
                                                             approximate=self._settings.approximate,
                                                             keep_brackets=not self._settings.remove_brackets,
                                                             artist=song.artist,
                                                             title=song.title,
                                                             source=self._settings.source.lower(),
                                                             song_filepath=song.filepath))

    for result in futures.as_completed(self._lyricsResults):
      if LyricGrabberThread.interrupt:
        self.exit()
        return
      try:
        if result.result().succeeded:
          if result.result().lyrics:
            if not LyricGrabberThread.interrupt:
              self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)
              self.setLyrics.emit(result.result().filepath,
                                result.result().lyrics,
                                result.result().url)
              self._fileWritingResults.append(self._fileWritingExecutor.submit(lyric_grabber.write_file,
                                                                             artist=result.result().artist,
                                                                             title=result.result().title,
                                                                             write_info=self._settings.info,
                                                                             write_metadata=self._settings.metadata,
                                                                             write_text=self._settings.text,
                                                                             lyrics=result.result().lyrics,
                                                                             song_filepath=result.result().filepath))
        else:
          if not LyricGrabberThread.interrupt:
            self.setProgressIcon.emit(result.result().filepath, states.ERROR)
          logger.log(logger.LOG_LEVEL_INFO, 'No lyrics found: ' + result.result().message)
      except Exception as e:
        if not LyricGrabberThread.interrupt:
          self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        logger.log(logger.LOG_LEVEL_ERROR,
                   ' Exception occurred while getting lyrics for file {filepath}: {error}'.format(filepath=result.result().filepath,
                                                                                                  error=str(e)))

    for result in futures.as_completed(self._fileWritingResults):
      # Super weird, but this causes crashes in the compiled .app for macOS.
      # Uncomment for testing only.
      # print(result.result().message)
      if not LyricGrabberThread.interrupt:
        self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)

    if not LyricGrabberThread.interrupt:
        self.notifyComplete.emit(True)
