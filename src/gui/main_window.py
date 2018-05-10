from concurrent import futures
import os
import subprocess
import sys
import threading

try:
  from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from gui import about_dialog
from gui import appearance
from gui import detail_dialog
from gui import error_dialog
from gui import settings_dialog
from gui import update_dialog
from modules.logger import logger
from modules import lyric_grabber
from modules import settings
from modules import utils

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class states:
  NOT_STARTED = 0
  ERROR = 1
  IN_PROGRESS = 2
  COMPLETE = 3

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
    if self._settings.get_source() == 'azlyrics' or self._settings.get_source() == 'musixmatch':
      self._lyricsExecutor = futures.ThreadPoolExecutor(max_workers=3)
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
                                                             approximate=self._settings.get_approximate(),
                                                             keep_brackets=not self._settings.get_remove_brackets(),
                                                             artist=song.artist,
                                                             title=song.title,
                                                             source=self._settings.get_source().lower(),
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
                                                                             write_info=self._settings.get_info(),
                                                                             write_metadata=self._settings.get_metadata(),
                                                                             write_text=self._settings.get_text(),
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
          result = lyric_grabber.get_lyrics(approximate=self._settings.get_approximate(),
                                            keep_brackets=not self._settings.get_remove_brackets(),
                                            artist=self._artist,
                                            title=self._title,
                                            source=self._source.lower(),
                                            song_filepath=self._filepath)

        if result.succeeded:
          self.setUrl.emit(result.url)
          self.setLyrics.emit(result.lyrics)
          result = lyric_grabber.write_file(artist=self._artist,
                                            title=self._title,
                                            write_info=self._settings.get_info(),
                                            write_metadata=self._settings.get_metadata(),
                                            write_text=self._settings.get_text(),
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

class QWidgetItem (QtWidgets.QWidget):
  dialog = None;

  def __init__(self, parent):
    super().__init__(parent)

    # Set parent
    self.parent = parent

    # Add progress label
    self._progressLabel = QtWidgets.QLabel()
    self._progressLabel.setFixedWidth(15)
    self._progressLabel.setAlignment(QtCore.Qt.AlignCenter)

    # Add album art label
    self._albumArtLabel = QtWidgets.QLabel()
    self._albumArtLabel.setFixedWidth(80)
    self._albumArtLabel.setFixedHeight(80)
    self._albumArtLabel.setMargin(0)

    # Add title and artist text labels
    self._textTitleLabel = QtWidgets.QLabel()
    self._textTitleLabel.setFont(appearance.MEDIUM_FONT)
    self._textArtistLabel = QtWidgets.QLabel()
    self._textArtistLabel.setFont(appearance.SMALL_FONT)
    if utils.IS_WINDOWS:
      self._textArtistLabel.setStyleSheet('color: dimgrey')

    self._textVBoxLayout = QtWidgets.QVBoxLayout()
    self._textVBoxLayout.addWidget(self._textTitleLabel)
    self._textVBoxLayout.addWidget(self._textArtistLabel)
    self._textVBoxLayout.setSpacing(0)
    # For testing purposes
    # self._textTitleQLabel.setStyleSheet('''
    #     background: rgb(0, 0, 255);
    # ''')
    # self._textArtistQLabel.setStyleSheet('''
    #     background: rgb(255, 0, 0);
    # ''')

    # Add buttons
    self._lyricsButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/lyrics.png')), 'View Lyrics')
    self._lyricsButton.setFocusPolicy(QtCore.Qt.NoFocus)
    if utils.IS_MAC:
      self._lyricsButton.pressed.connect(lambda: self._lyricsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/lyrics_inverted.png'))))
      self._lyricsButton.released.connect(lambda: self._lyricsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/lyrics.png'))))
    self._lyricsButton.clicked.connect(lambda: self.openDetailDialog())
    if utils.IS_MAC:
      self._openButton = QtWidgets.QPushButton('Open in Finder')
    elif utils.IS_WINDOWS:
      self._openButton = QtWidgets.QPushButton('Open in Explorer')
    else:
      self._openButton = QtWidgets.QPushButton('Open in File Browser')
    self._openButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._openButton.setFixedWidth(self._lyricsButton.minimumSizeHint().width()+50)
    self._lyricsButton.setFixedWidth(self._lyricsButton.minimumSizeHint().width()+50)
    self._openButton.clicked.connect(lambda: self.openfilepath())
    # self._removeButton = QtWidgets.QPushButton('Remove')
    # self._removeButton.setMaximumWidth(125)
    # self._removeButton.clicked.connect(lambda: self.removeFile())

    self._buttonVBoxLayout = QtWidgets.QVBoxLayout()
    self._buttonVBoxLayout.addWidget(self._lyricsButton)
    self._buttonVBoxLayout.addWidget(self._openButton)
    # self._buttonVBoxLayout.addWidget(self.removeButton)
    self._buttonVBoxLayout.setSpacing(0)

    # Layout containing all elements
    self._allHBoxLayout = QtWidgets.QHBoxLayout()
    if utils.IS_WINDOWS:
      self._leftSpacer = QtWidgets.QSpacerItem(5, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
      self._allHBoxLayout.addItem(self._leftSpacer)
    self._allHBoxLayout.addWidget(self._progressLabel, 0)
    self._allHBoxLayout.addWidget(self._albumArtLabel, 1)
    self._allHBoxLayout.addLayout(self._textVBoxLayout, 2)
    self._allHBoxLayout.addLayout(self._buttonVBoxLayout, 3)
    # Add a spacer on the right side for Windows
    if utils.IS_WINDOWS:
      self._rightSpacer = QtWidgets.QSpacerItem(10, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
      self._allHBoxLayout.addItem(self._rightSpacer)

    self.setLayout(self._allHBoxLayout)
    self.setFocusPolicy(QtCore.Qt.NoFocus)

    # Initialize various parameters to nothing
    self._artist = ''
    self._title = ''
    self._lyrics = ''
    self._url = ''

  def mousePressEvent(self, QMouseEvent):
    if QMouseEvent.button() == QtCore.Qt.LeftButton:
      self.parent.setSelectedWidget(self._filepath)
      self.mouseReleaseEvent = self.openDetailDialog()

  def setBackgroundColor(self, backgroundColor):
    self._pal = QtGui.QPalette()
    self._pal.setColor(QtGui.QPalette.Background, backgroundColor)
    self.setAutoFillBackground(True)
    self.setPalette(self._pal)

  def setProgressIcon(self, state, deviceRatio):
    if state == states.IN_PROGRESS:
      imagePath = utils.resource_path('./assets/in_progress.png')
    elif state == states.ERROR:
      imagePath = utils.resource_path('./assets/error.png')
    elif state == states.COMPLETE:
      imagePath = utils.resource_path('./assets/complete.png')
    else:
      imagePath = utils.resource_path('./assets/not_started.png')
    self._state = state
    self._progressIcon = QtGui.QPixmap(imagePath)
    self._progressIcon.setDevicePixelRatio(deviceRatio)
    self._iconWidth = deviceRatio * self._progressLabel.width()
    self._iconHeight = deviceRatio * self._progressLabel.height()
    self._progressLabel.setPixmap(self._progressIcon.scaled(self._iconWidth,
                                                            self._iconHeight,
                                                            QtCore.Qt.KeepAspectRatio,
                                                            QtCore.Qt.SmoothTransformation))

  def setProgressIconForSingle(self, state):
    self.setProgressIcon(state, self.devicePixelRatio())

  def getState(self):
    if hasattr(self, '_state'):
      return self._state
    else:
      return states.NOT_STARTED

  def setAlbumArt(self, imageData, deviceRatio):
    try:
      if imageData == b'' or imageData is None:
        albumImage = QtGui.QImage(utils.resource_path('./assets/art_empty.png'))
      else:
        albumImage = QtGui.QImage.fromData(imageData)
      if albumImage.isNull():
        albumImage = QtGui.QImage(utils.resource_path('./assets/art_empty.png'))
      albumIcon = QtGui.QPixmap.fromImage(albumImage)
      albumIcon.setDevicePixelRatio(deviceRatio)
      self._iconWidth = deviceRatio * (self._albumArtLabel.width() - 10)
      self._iconHeight = deviceRatio * (self._albumArtLabel.height() - 10)
      self._albumArtLabel.setPixmap(albumIcon.scaled(self._iconWidth,
                                                           self._iconHeight,
                                                           QtCore.Qt.KeepAspectRatio,
                                                           QtCore.Qt.SmoothTransformation))
    except:
      logger.log(logger.LOG_LEVEL_ERROR, 'Error setting album art.')

  def setTitleText(self, text):
    self._title = text
    self._textTitleLabel.setText(text)

  def setArtistText(self, text):
    self._artist = text
    self._textArtistLabel.setText(text)

  def openDetailDialog(self):
    self.resetColours()
    self.setBackgroundColor(appearance.HIGHLIGHT_COLOUR)
    try:
      QWidgetItem.dialog.setWindowTitle('{artist} - {title}'.format(artist=self._artist, title=self._title))
      QWidgetItem.dialog.updateLyrics(self._lyrics)
      QWidgetItem.dialog.updateUrl(self._url)
      QWidgetItem.dialog.setFilepath(self._filepath)
      QWidgetItem.dialog.setArtistAndTitle(self._artist, self._title)
      QWidgetItem.dialog.setParent(self)
      QWidgetItem.dialog.show()
    except Exception as e:
      # self.window().setEnabled(False)
      QWidgetItem.dialog = detail_dialog.QLyricsDialog(parent=self,
                                                       artist=self._artist,
                                                       title=self._title,
                                                       lyrics=self._lyrics,
                                                       url=self._url,
                                                       filepath=self._filepath)
      QWidgetItem.dialog.show()
      self.activateWindow()
      # self.window().setEnabled(True)

  def setfilepath(self, filepath):
    self._filepath = filepath

  def getFilepath(self):
    return self._filepath

  def openfilepath(self):
    # QtGui.QDesktopServices.openUrl(QtCore.QUrl('file://' + self._filepath))
    if utils.IS_MAC:
      subprocess.run(['open', '-R', self._filepath])
    elif utils.IS_WINDOWS:
      subprocess.run('explorer /select,"{}"'.format(self._filepath.replace('/', '\\')))
    else:
      subprocess.run(['xdg-open', os.path.dirname(self._filepath)])

  def getLyrics(self, artist=None, title=None, url=None, source=None):
    self.setProgressIconForSingle(states.IN_PROGRESS)
    if artist is None:
      artist = self._artist
    self._fetch_thread = SingleLyricGrabberThread(parent=self,
                                                  filepath=self._filepath,
                                                  artist=artist,
                                                  title=title,
                                                  url=url,
                                                  source=source)
    self._fetch_thread.start()

    self._fetch_thread.setProgressIcon.connect(self.setProgressIconForSingle)
    self._fetch_thread.setLyrics.connect(self.setLyrics)
    self._fetch_thread.setUrl.connect(self.setUrl)
    self._fetch_thread.finished.connect(self.parent.playSuccessSound)

  def setLyrics(self, lyrics):
    self._lyrics = lyrics
    try:
      if QWidgetItem.dialog is not None:
        if QWidgetItem.dialog.getFilepath() == self._filepath:
          QWidgetItem.dialog.updateLyrics(lyrics)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def saveLyrics(self, lyrics):
    try:
      self._lyrics = lyrics
      self._settings = settings.Settings()
      lyric_grabber.write_file(artist=self._artist,
                               title=self._title,
                               write_info=self._settings.get_info(),
                               write_metadata=self._settings.get_metadata(),
                               write_text=self._settings.get_text(),
                               lyrics=lyrics,
                               song_filepath=self._filepath)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def setUrl(self, url):
    self._url = url
    try:
      if QWidgetItem.dialog is not None:
        if QWidgetItem.dialog.getFilepath() == self._filepath:
          QWidgetItem.dialog.updateUrl(url)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def resetColours(self):
    self.parent.resetListColours()

  # def removeFile (self):
  #   self.setParent(None)

class MainWindow (QtWidgets.QMainWindow):
  selectedWidgetIndex = None
  widgetAddingLock = threading.Lock()

  def __init__(self):
    super(MainWindow, self).__init__()

    # Create a settings object
    self._settings = settings.Settings()

    # Create and add items to menubar
    self._openAboutAction = QtWidgets.QAction('About Quaver')
    self._openAboutAction.triggered.connect(lambda: self.openAboutDialog())
    if utils.IS_MAC:
      self._openSettingsAction = QtWidgets.QAction('Preferences')
    else:
      self._openSettingsAction = QtWidgets.QAction('Settings')
    self._openSettingsAction.setShortcut('Ctrl+Comma')
    self._openSettingsAction.triggered.connect(lambda: self.openSettingsDialog())

    self._openFileAction = QtWidgets.QAction('Open File...', self)
    self._openFileAction.setShortcut('Ctrl+O')
    self._openFileAction.triggered.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles))
    self._openFolderAction = QtWidgets.QAction('Open Folder...', self)
    self._openFolderAction.setShortcut('Ctrl+Shift+O')
    self._openFolderAction.triggered.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.Directory))
    self._closeAction = QtWidgets.QAction('Close')
    self._closeAction.setShortcut('Ctrl+W')
    self._closeAction.triggered.connect(lambda: self.close())

    self._removeAllAction = QtWidgets.QAction('Remove all Files')
    self._removeAllAction.setShortcut('Ctrl+Backspace')
    self._removeAllAction.triggered.connect(lambda: self.removeAllFilesFromList())
    self._removeCompletedAction = QtWidgets.QAction('Remove Files with Lyrics')
    self._removeCompletedAction.setShortcut('Ctrl+Shift+Backspace')
    self._removeCompletedAction.triggered.connect(lambda: self.removeCompletedFiles())

    if utils.IS_MAC:
      self._minimizeAction = QtWidgets.QAction('Minimize', self)
      self._minimizeAction.setShortcut('Ctrl+M')
      self._minimizeAction.triggered.connect(lambda: self.showMinimized())
      self._maximizeAction = QtWidgets.QAction('Zoom', self)
      self._maximizeAction.setShortcut('Ctrl+Shift+M')
      self._maximizeAction.triggered.connect(lambda: self.showMaximized())
      self._showNormalAction = QtWidgets.QAction('Bring to Front', self)
      self._showNormalAction.triggered.connect(lambda: self.showNormal())
      self._fullScreenAction = QtWidgets.QAction('Enter Fullscreen', self)
      self._fullScreenAction.setShortcut('Ctrl+Shift+F')
      self._fullScreenAction.triggered.connect(lambda: self.showFullScreen())

    self._helpAction = QtWidgets.QAction('Help', self)
    self._helpAction.triggered.connect(lambda: self.openAboutDialog())

    if utils.IS_MAC:
      self._menuBar = QtWidgets.QMenuBar()
    else:
      self._menuBar = self.menuBar()

    if utils.IS_MAC:
      self._fileMenu = self._menuBar.addMenu('Quaver')
      self._fileMenu.addAction(self._openAboutAction)
      self._fileMenu.addSeparator()
      self._fileMenu.addAction(self._openSettingsAction)

    self._fileMenu = self._menuBar.addMenu('File')
    self._fileMenu.addAction(self._openFileAction)
    self._fileMenu.addAction(self._openFolderAction)
    self._fileMenu.addSeparator()
    self._fileMenu.addAction(self._closeAction)

    self._editMenu = self._menuBar.addMenu('Edit')
    self._editMenu.addAction(self._removeAllAction)
    self._editMenu.addAction(self._removeCompletedAction)
    self._editMenu.addSeparator()

    if utils.IS_MAC:
      self._windowMenu = self._menuBar.addMenu('Window')
      self._windowMenu.addAction(self._minimizeAction)
      self._windowMenu.addAction(self._maximizeAction)
      self._windowMenu.addAction(self._fullScreenAction)
      self._windowMenu.addSeparator()
      self._windowMenu.addAction(self._showNormalAction)

    if not utils.IS_MAC:
      self._toolsMenu = self._menuBar.addMenu('Tools')
      self._toolsMenu.addAction(self._openSettingsAction)

    self._helpMenu = self._menuBar.addMenu('Help')
    self._helpMenu.addAction(self._helpAction)
    if not utils.IS_MAC:
      self._helpMenu.addAction(self._openAboutAction)

    # Do not create toolbar if not on Mac
    if utils.IS_MAC:
      # Add items to toolbar
      self._leftAlignSpacer = QtWidgets.QSpacerItem(15, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
      self._addFileButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/add_music.png')), 'Add song')
      self._addFileButton.pressed.connect(lambda: self._addFileButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/add_music_inverted.png'))))
      self._addFileButton.released.connect(lambda: self._addFileButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/add_music.png'))))
      self._addFileButton.clicked.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles))
      self._addFolderButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/add_folder.png')), 'Add folder')
      self._addFolderButton.pressed.connect(lambda: self._addFolderButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/add_folder_inverted.png'))))
      self._addFolderButton.released.connect(lambda: self._addFolderButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/add_folder.png'))))
      self._addFolderButton.clicked.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.Directory))
      self._removeFileButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/delete.png')), 'Remove all')
      self._removeFileButton.pressed.connect(lambda: self._removeFileButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/delete_inverted.png'))))
      self._removeFileButton.released.connect(lambda: self._removeFileButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/delete.png'))))
      self._removeFileButton.clicked.connect(lambda: self.removeAllFilesFromList())
      self._horizontalSpacer = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      self._settingsButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/settings.png')), 'Preferences')
      self._settingsButton.pressed.connect(lambda: self._settingsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/settings_inverted.png'))))
      self._settingsButton.released.connect(lambda: self._settingsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/settings.png'))))
      self._settingsButton.clicked.connect(lambda: self.openSettingsDialog())
      self._rightAlignSpacer = QtWidgets.QSpacerItem(15, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

      self._toolBarLayout = QtWidgets.QHBoxLayout()
      self._toolBarLayout.addItem(self._leftAlignSpacer)
      self._toolBarLayout.addWidget(self._addFileButton)
      self._toolBarLayout.addWidget(self._addFolderButton)
      self._toolBarLayout.addWidget(self._removeFileButton)
      self._toolBarLayout.addItem(self._horizontalSpacer)
      self._toolBarLayout.addWidget(self._settingsButton)
      self._toolBarLayout.addItem(self._rightAlignSpacer)
      self._toolBarLayout.setSpacing(5)
      self._toolBarLayout.setContentsMargins(0, 0, 0, 0)

      self._toolBarItems = QtWidgets.QWidget()
      self._toolBarItems.setLayout(self._toolBarLayout)

      # Add toolbar to window
      self._toolBar = self.addToolBar('main')
      self._toolBar.addWidget(self._toolBarItems)
      self._toolBar.setFloatable(False)
      self._toolBar.setMovable(False)
      self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    # Create a hint for the user
    self._instructionIconLabel = QtWidgets.QLabel()
    self._instructionIconLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._instructionIconLabel.setAlignment(QtCore.Qt.AlignCenter)
    self._quaverIcon = QtGui.QPixmap(utils.resource_path('./assets/icon_monochrome.png'))
    self._quaverIcon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * 150
    self._iconHeight = self.devicePixelRatio() * 150
    self._instructionIconLabel.setPixmap(self._quaverIcon.scaled(self._iconWidth, self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    self._verticalSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    if utils.IS_MAC:
      self._instructionLabel = QtWidgets.QLabel('Grab lyrics by adding a song.'
        '<br>Drag a song in, or click "Add song" to get started.')
    else:
      self._instructionLabel = QtWidgets.QLabel('Grab lyrics by adding a song.'
        '<br>Drag a song in, or open the "File" menu to get started.')
    self._instructionLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._instructionLabel.setAlignment(QtCore.Qt.AlignCenter)
    self._instructionLabel.setStyleSheet('color: grey')
    self._instructionLabel.setFont(appearance.SMALL_FONT)

    self._removedInstructions = False

    # This layout contains all the list items
    # Style the layout: spacing (between items), content (padding within items)
    self._mainScrollAreaWidgetLayout = QtWidgets.QVBoxLayout()
    self._mainScrollAreaWidgetLayout.setAlignment(QtCore.Qt.AlignCenter)
    self._mainScrollAreaWidgetLayout.setSpacing(0)
    self._mainScrollAreaWidgetLayout.setContentsMargins(0, 0, 0, 0)

    self._mainScrollAreaWidgetLayout.addWidget(self._instructionIconLabel)
    self._mainScrollAreaWidgetLayout.addItem(self._verticalSpacer)
    self._mainScrollAreaWidgetLayout.addWidget(self._instructionLabel)

    # mainScrollAreaWidget contains layout that contains all listwidgets
    self._mainScrollAreaWidget = QtWidgets.QWidget()
    self._mainScrollAreaWidget.setMinimumWidth(400)
    self._mainScrollAreaWidget.setLayout(self._mainScrollAreaWidgetLayout)

    # Create QScrollArea to contains widget containing list of all list items
    # NOTE: Not using QListWidget because scrolling is choppy on macOS
    self._mainScrollArea = QtWidgets.QScrollArea(self)
    self._mainScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
    self._mainScrollArea.setWidgetResizable(True)
    self._mainScrollArea.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._mainScrollArea.setFocusPolicy(QtCore.Qt.NoFocus)
    self._mainScrollArea.setWidget(self._mainScrollAreaWidget)
    self.setCentralWidget(self._mainScrollArea)

    # Style main window
    self.setMinimumSize(600, 400)
    self.setUnifiedTitleAndToolBarOnMac(True)
    if not utils.IS_MAC:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setAcceptDrops(True)

  def closeEvent(self, event):
    try:
      LyricGrabberThread.interrupt = True
    except:
      logger.log(logger.LOG_LEVEL_ERROR, 'No thread running, exiting!')

  def dragEnterEvent(self, event):
    # print('Something entered')
    event.accept()

  def dragMoveEvent(self, event):
    # print('Drag moved')
    event.accept()

  def dropEvent(self, event):
    # print('Event dropped')
    if event.mimeData().hasUrls:
      event.accept()
      filepaths = []
      for url in event.mimeData().urls():
        url = url.toString().replace('file:///' if utils.IS_WINDOWS else 'file://', '')
        # print(url)
        if os.path.isdir(url):
          for root, dirs, files in os.walk(url):
            [filepaths.append(os.path.join(root, file)) for file in files]
        elif os.path.isfile(url):
          filepaths.append(url)
        else:
          # print('That is neither a directory nor a file (???)')
          pass
      # print('Filepaths are {}'.format(filepaths))
      self.generateFilepathList(filepaths)

  def keyPressEvent(self, event):
    key = event.key()
    # Handle modifiers first, then others
    if event.modifiers() & QtCore.Qt.ShiftModifier and event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_F and utils.IS_MAC:
        self.showFullScreen()
      elif key == QtCore.Qt.Key_M and utils.IS_MAC:
        self.showMaximized()
      elif key == QtCore.Qt.Key_O:
        # Super + shift + O should open folder browser
        self.openFileDialog(QtWidgets.QFileDialog.Directory)
      elif key == QtCore.Qt.Key_Backspace:
        self.removeCompletedFiles()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_M and utils.IS_MAC:
        self.showMinimized()
      elif key == QtCore.Qt.Key_O:
        # Super + O should open file browser
        self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles)
      elif key == QtCore.Qt.Key_W:
        self.close()
      elif key == QtCore.Qt.Key_Backspace:
        self.removeAllFilesFromList()
      elif key == QtCore.Qt.Key_Comma:
        self.openSettingsDialog()
    else:
      if key == QtCore.Qt.Key_S or key == QtCore.Qt.Key_Down:
        if MainWindow.selectedWidgetIndex is not None:
          newIndex = MainWindow.selectedWidgetIndex + 1
          if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
            MainWindow.selectedWidgetIndex += 1
            self.resetListColours()
            self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget())
            self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget().openDetailDialog()
      elif key == QtCore.Qt.Key_W or key == QtCore.Qt.Key_Up:
        if MainWindow.selectedWidgetIndex is not None:
          newIndex = MainWindow.selectedWidgetIndex - 1
          if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
            MainWindow.selectedWidgetIndex -= 1
            self.resetListColours()
            self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget())
            self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget().openDetailDialog()

  def setSelectedWidget(self, filepath):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath() == filepath:
        MainWindow.selectedWidgetIndex = i
        break

  def openFileDialog(self, fileMode):
    # fileMode parameter is QtWidgets.QFileDialog.Directory or QtWidgets.QFileDialog.ExistingFiles
    self._fileDialog = QtWidgets.QFileDialog()
    self._fileDialog.setFileMode(fileMode)
    self._fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

    filepaths = []

    if (fileMode == QtWidgets.QFileDialog.Directory):
      directory = self._fileDialog.getExistingDirectory()
      # print('Directory selected is ' + directory)
      for root, dirs, files in os.walk(directory):
        [filepaths.append(os.path.join(root, file)) for file in files]
    else:
      files = self._fileDialog.getOpenFileNames()
      # print('Files selected are ' + str(files))
      [filepaths.append(file) for file in files[0]]

    self.generateFilepathList(filepaths)

  def generateFilepathList(self, files):
    if not hasattr(self, '_all_filepaths'):
      self._all_filepaths = []
    filepaths = []
    invalid_filepaths = []

    for file in files:
      if file.endswith(utils.SUPPORTED_FILETYPES):
        if file in self._all_filepaths:
          invalid_filepaths.append(file)
        else:
          self._all_filepaths.append(file)
          filepaths.append(file)
      else:
        invalid_filepaths.append(file)

    if len(filepaths) > 0:
      self.startFetchThread(filepaths)

    # Show an error message for each invalid filepath found
    if invalid_filepaths and self._settings.get_show_errors():
      self.showError(invalid_filepaths)

  def showError(self, filepaths):
    self.setEnabled(False)
    try:
      if not hasattr(self, '_error_dialog'):
        self.playErrorSound()
        self._error_dialog = error_dialog.QErrorDialog(self, filepaths)
        self._error_dialog.exec()
        del self._error_dialog
    except:
      pass
    self.setEnabled(True)

  def startFetchThread(self, filepaths):
    # Start another thread for network requests to not block the GUI thread
    self._fetch_thread = LyricGrabberThread(self, filepaths)

    self._fetch_thread.addFileToList.connect(self.addFileToList)
    self._fetch_thread.notifyComplete.connect(self.playSuccessSound)
    self._fetch_thread.notifyNoMetadata.connect(self.showError)
    self._fetch_thread.setLyrics.connect(self.setLyrics)
    self._fetch_thread.setProgressIcon.connect(self.setProgressIcon)

    self._fetch_thread.start()

  def addFileToList(self, artist, title, art, filepath):
    with MainWindow.widgetAddingLock:
      if not self._removedInstructions:
        self._instructionLabel.setParent(None)
        self._instructionIconLabel.setParent(None)
        self._mainScrollAreaWidgetLayout.removeItem(self._verticalSpacer)
        self._mainScrollAreaWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        self._removedInstructions = True

      # Create WidgetItem for each item
      listWidgetItem = QWidgetItem(self)
      listWidgetItem.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
      listWidgetItem.setProgressIcon(states.NOT_STARTED, self.devicePixelRatio())
      listWidgetItem.setAlbumArt(art, self.devicePixelRatio())
      listWidgetItem.setArtistText(artist)
      listWidgetItem.setTitleText(title)
      listWidgetItem.setfilepath(filepath)
      if self._mainScrollAreaWidgetLayout.count() % 2:
        listWidgetItem.setBackgroundColor(appearance.ALTERNATE_COLOUR_ONE)
      else:
        listWidgetItem.setBackgroundColor(QtCore.Qt.white)
      # Add ListWidgetItem into mainScrollAreaWidgetLayout
      self._mainScrollAreaWidgetLayout.addWidget(listWidgetItem)

  def setProgressIcon(self, filepath, state):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilepath() == filepath:
        widgetItem.setProgressIcon(state, self.devicePixelRatio())

  def setLyrics(self, filepath, lyrics, url):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilepath() == filepath:
        widgetItem.setLyrics(lyrics)
        widgetItem.setUrl(url)

  def resetListColours(self):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      if self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionIconLabel \
      or self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionLabel \
      or self._mainScrollAreaWidgetLayout.itemAt(i) is self._verticalSpacer:
        pass
      else:
        if i % 2:
          self._mainScrollAreaWidgetLayout.itemAt(i).widget().setBackgroundColor(appearance.ALTERNATE_COLOUR_ONE)
        else:
          self._mainScrollAreaWidgetLayout.itemAt(i).widget().setBackgroundColor(QtCore.Qt.white)

  def removeAllFilesFromList(self):
    try:
      QWidgetItem.dialog.close()
      self._fetch_thread.exit()
    except:
      pass
    finally:
      for i in reversed(range(self._mainScrollAreaWidgetLayout.count())):
        if self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionIconLabel \
        or self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionLabel \
        or self._mainScrollAreaWidgetLayout.itemAt(i) is self._verticalSpacer:
          pass
        else:
          widget = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
          widget.deleteLater()
          widget.setParent(None)
          widget = None
      if hasattr(self, '_all_filepaths'):
        self._all_filepaths.clear()

  def removeCompletedFiles(self):
    try:
      QWidgetItem.dialog.close()
    except:
      pass
    finally:
      for i in reversed(range(self._mainScrollAreaWidgetLayout.count())):
        if self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionIconLabel \
        or self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionLabel \
        or self._mainScrollAreaWidgetLayout.itemAt(i) is self._verticalSpacer:
          pass
        else:
          if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.COMPLETE:
            self._all_filepaths.remove(self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath())
            widget = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
            widget.deleteLater()
            widget.setParent(None)
            widget = None
      self.resetListColours()

  def openAboutDialog(self):
    self.setEnabled(False)
    self._about_dialog = about_dialog.QAboutDialog(self)
    self._about_dialog.exec()
    self.setEnabled(True)

  def openSettingsDialog(self):
    self.setEnabled(False)
    self._settings_dialog = settings_dialog.QSettingsDialog()
    self._settings_dialog.exec()
    self.setEnabled(True)

  def openUpdateDialog(self, update_available, show_if_no_update=False, show_option_to_hide=True):
    show_hide_message = ('Click "OK" to download the new version of Quaver.'
      '<br><br>Check "Don\'t show this again" if you do not want to see these update messages.'
      ' You can re-enable these messages under Settings.')
    do_not_show_hide_message = ('Click "OK" to download the new version of Quaver.'
      '<br><br>Quaver can automatically check for updates if you check the appropriate option in Settings.')

    if update_available:
      self._update_dialog = update_dialog.QUpdateDialog(self,
        title='Version {} of Quaver is available!'.format(update_available.version),
        message=show_hide_message if show_option_to_hide else do_not_show_hide_message,
        url=update_available.url,
        description=update_available.description,
        show_option_to_hide=show_option_to_hide)
      self._update_dialog.exec()
    elif show_if_no_update:
      self._update_dialog = update_dialog.QUpdateDialog(self,
        title='You are on the newest version of Quaver!',
        message=('Quaver can automatically check for updates if you check the appropriate option in Settings.'),
        url=None,
        description=None,
        show_option_to_hide=show_option_to_hide)
      self._update_dialog.exec()

  def openDialog(self, message):
    self._something_dialog = update_dialog.QUpdateDialog(self,
      title='sys argv passed in is {}'.format(message),
      message='WHOA',
      url=None,
      description=None,
      show_option_to_hide=True)
    self._something_dialog.exec()

  def playSuccessSound(self):
    # Playing sounded with PyQt causes this to happen when closing:
    # QCoreApplication::postEvent: Unexpected null receiver
    # I have no idea why and it doesn't seem to negatively affect UX
    # since it's closing anyway...
    if self._settings.get_play_sounds():
      QtMultimedia.QSound.play(utils.resource_path('./assets/success.wav'))

  def playErrorSound(self):
    if self._settings.get_play_sounds():
      QtMultimedia.QSound.play(utils.resource_path('./assets/error.wav'))