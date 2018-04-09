from modules.logger import logger
from gui import detail_dialog
from modules import lyric_grabber
from gui import settings_dialog
from modules import settings

import base64
# from colorthief import ColorThief
from concurrent import futures
import os
from PyQt5 import QtCore, QtGui, QtWidgets

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
  setProgressIcon = QtCore.pyqtSignal(['QString', int])
  setLyrics = QtCore.pyqtSignal(['QString', 'QString', 'QString'])

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
    self._songsBad = []

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
          self.setProgressIcon.emit(result.result().filepath, states.ERROR)
          logger.log(logger.LOG_LEVEL_INFO, 'No metadata found: ' + result.result().message)
      except Exception as e:
        self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        logger.log(logger.LOG_LEVEL_ERROR, 
                   ' Exception occurred while adding file {filepath}: {error}'.format(filepath=result.result().filepath,
                                                                                      error=str(e)))

    for song in self._songs:
      self.setProgressIcon.emit(result.result().filepath, states.IN_PROGRESS)
      self._lyricsResults.append(self._lyricsExecutor.submit(lyric_grabber.get_lyrics,
                                                             approximate=self._settings.get_approximate(),
                                                             keep_brackets=not self._settings.get_remove_brackets(),
                                                             artist=song.artist,
                                                             title=song.title,
                                                             source=self._settings.get_source().lower(),
                                                             song_filepath=song.filepath))

    for result in futures.as_completed(self._lyricsResults):
      try:
        if result.result().succeeded:
          if result.result().lyrics:
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
          self.setProgressIcon.emit(result.result().filepath, states.ERROR)
      except Exception as e:
        self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        logger.log(logger.LOG_LEVEL_ERROR,
                   ' Exception occurred while getting lyrics for file {filepath}: {error}'.format(filepath=result.result().filepath,
                                                                                                  error=str(e)))

    for result in futures.as_completed(self._fileWritingResults):
      self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)
      print(result.result().message)

class SingleLyricGrabberThread (QtCore.QThread):
  setProgressIcon = QtCore.pyqtSignal([int])
  setLyrics = QtCore.pyqtSignal(['QString'])

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
    try:
      self.setProgressIcon.emit(states.IN_PROGRESS)
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
        self.setLyrics.emit(result.lyrics)
        result = lyric_grabber.write_file(artist=self._artist,
                                          title=self._title,
                                          write_info=self._settings.get_info(),
                                          write_metadata=self._settings.get_metadata(),
                                          write_text=self._settings.get_text(),
                                          lyrics=result.lyrics,
                                          song_filepath=self._filepath)
        print(result.message)
        self.setProgressIcon.emit(states.COMPLETE)
      else:
        self.setProgressIcon.emit(states.ERROR)
      # print(result.lyrics)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR,
                 ' Exception occurred while getting lyrics for file {filepath}: {error}'.format(self_filepath,
                                                                                                error=str(e)))

class QWidgetItem (QtWidgets.QWidget):
  # self.largeFont = QtGui.QFont('Gill Sans', 18, QtGui.QFont.Bold)
  largeFont = QtGui.QFont('Gill Sans', 18)
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
    self._textArtistLabel = QtWidgets.QLabel()

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

    # Make font
    self._textTitleLabel.setFont(self.largeFont)

    # Add buttons
    self._lyricsButton = QtWidgets.QPushButton(QtGui.QIcon('./assets/lyrics.png'), 'View Lyrics')
    self._lyricsButton.setMaximumWidth(125)
    self._lyricsButton.clicked.connect(lambda: self.openDetailDialog())
    self._openButton = QtWidgets.QPushButton('Open in Finder')
    self._openButton.setMaximumWidth(125)
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
    self._allHBoxLayout.addWidget(self._progressLabel, 0)
    self._allHBoxLayout.addWidget(self._albumArtLabel, 1)
    self._allHBoxLayout.addLayout(self._textVBoxLayout, 2)
    self._allHBoxLayout.addLayout(self._buttonVBoxLayout, 3)

    self.setLayout(self._allHBoxLayout)

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
      imagePath = './assets/in_progress.png'
    elif state == states.ERROR:
      imagePath = './assets/error.png'
    elif state == states.COMPLETE:
      imagePath = './assets/complete.png'
    else:
      imagePath = './assets/not_started.png'
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
        self._albumImage = QtGui.QImage('./assets/art_empty.png')
      else:
        self._albumImage = QtGui.QImage.fromData(imageData)
      if self._albumImage.isNull():
        self._albumImage = QtGui.QImage('./assets/art_empty.png')
      self._albumIcon = QtGui.QPixmap.fromImage(self._albumImage)
      self._albumIcon.setDevicePixelRatio(deviceRatio)
      self._iconWidth = deviceRatio * (self._albumArtLabel.width() - 10)
      self._iconHeight = deviceRatio * (self._albumArtLabel.height() - 10)
      self._albumArtLabel.setPixmap(self._albumIcon.scaled(self._iconWidth,
                                                           self._iconHeight,
                                                           QtCore.Qt.KeepAspectRatio,
                                                           QtCore.Qt.SmoothTransformation))
    except:
      print('Error setting album art.')

  def setTitleText(self, text):
    self._title = text
    self._textTitleLabel.setText(text)

  def setArtistText(self, text):
    self._artist = text
    self._textArtistLabel.setText(text)

  def openDetailDialog(self):
    if QWidgetItem.dialog is not None:
      QWidgetItem.dialog.hide()
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
    QtGui.QDesktopServices.openUrl(QtCore.QUrl('file://' + self._filepath))

  def getLyrics(self, artist=None, title=None, url=None, source=None):
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

  def setLyrics(self, lyrics):
    self._lyrics = lyrics
    try:
      if QWidgetItem.dialog is not None:
        if QWidgetItem.dialog.getFilepath() == self._filepath:
          QWidgetItem.dialog.updateLyrics(lyrics)
    except Exception as e:
      print(e)

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
      print(str(e))

  def setUrl(self, url):
    self._url = url
    try:
      if QWidgetItem.dialog is not None:
        if QWidgetItem.dialog.getFilepath() == self._filepath:
          QWidgetItem.dialog.updateUrl(url)
    except Exception as e:
      print(e)

  def resetColours(self):
    self.parent.resetListColours()

  # def removeFile (self):
  #   self.setParent(None)

class MainWindow (QtWidgets.QMainWindow):
  selectedWidgetIndex = None

  def __init__(self):
    super(MainWindow, self).__init__()

    # Style main window
    self.setMinimumSize(600, 400)
    self.setUnifiedTitleAndToolBarOnMac(True)

    # Create and add items to menubar
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
    self._removeAllAction.triggered.connect(lambda: self.removeCompletedFiles())
    self._removeCompletedAction = QtWidgets.QAction('Remove Files with Lyrics')
    self._removeCompletedAction.setShortcut('Ctrl+Shift+Backspace')
    self._removeCompletedAction.triggered.connect(lambda: self.removeCompletedFiles())

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
    self._helpAction.triggered.connect(lambda: self.openSettingsDialog())

    self._menuBar = self.menuBar()

    self._fileMenu = self._menuBar.addMenu('File')
    self._fileMenu.addAction(self._openFileAction)
    self._fileMenu.addAction(self._openFolderAction)
    self._fileMenu.addSeparator()
    self._fileMenu.addAction(self._closeAction)

    self._editMenu = self._menuBar.addMenu('Edit')
    self._editMenu.addAction(self._removeAllAction)
    self._editMenu.addAction(self._removeCompletedAction)
    self._editMenu.addSeparator()

    self._windowMenu = self._menuBar.addMenu('Window')
    self._windowMenu.addAction(self._minimizeAction)
    self._windowMenu.addAction(self._maximizeAction)
    self._windowMenu.addAction(self._fullScreenAction)
    self._windowMenu.addSeparator()
    self._windowMenu.addAction(self._showNormalAction)

    self._helpMenu = self._menuBar.addMenu('Help')
    self._helpMenu.addAction(self._helpAction)

    # Add items to toolbar
    self._leftAlignSpacer = QtWidgets.QSpacerItem(15, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    self._addFileButton = QtWidgets.QPushButton(QtGui.QIcon('./assets/add_music.png'), 'Add song')
    self._addFileButton.clicked.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles))
    self._addFolderButton = QtWidgets.QPushButton(QtGui.QIcon('./assets/add_folder.png'), 'Add folder')
    self._addFolderButton.clicked.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.Directory))
    self._removeFileButton = QtWidgets.QPushButton(QtGui.QIcon('./assets/delete.png'), 'Remove all')
    self._removeFileButton.clicked.connect(lambda: self.removeAllFilesFromList())
    self._horizontalSpacer = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._settingsButton = QtWidgets.QPushButton(QtGui.QIcon('./assets/settings.png'), 'Settings')
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

    # This layout contains all the list items
    # Style the layout: spacing (between items), content (padding within items)
    self._mainScrollAreaWidgetLayout = QtWidgets.QVBoxLayout()
    self._mainScrollAreaWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
    self._mainScrollAreaWidgetLayout.setSpacing(0)
    self._mainScrollAreaWidgetLayout.setContentsMargins(0, 0, 0, 0)

    # mainScrollAreaWidget contains layout that contains all listwidgets
    self._mainScrollAreaWidget = QtWidgets.QWidget()
    self._mainScrollAreaWidget.setMinimumWidth(400)
    self._mainScrollAreaWidget.setLayout(self._mainScrollAreaWidgetLayout)

    # Create QScrollArea to contains widget containing list of all list items
    # NOTE: Not using QListWidget because scrolling is choppy on macOS
    self._mainScrollArea = QtWidgets.QScrollArea(self)
    self._mainScrollArea.setWidgetResizable(True)
    self._mainScrollArea.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._mainScrollArea.setWidget(self._mainScrollAreaWidget)
    self.setCentralWidget(self._mainScrollArea)

  def keyPressEvent(self, event):
    key = event.key()
    # Handle modifiers first, then others
    if event.modifiers() & QtCore.Qt.ShiftModifier and event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_F:
        self.showFullScreen()
      elif key == QtCore.Qt.Key_M:
        self.showMaximized()
      elif key == QtCore.Qt.Key_O:
        # Super + shift + O should open folder browser
        self.openFileDialog(QtWidgets.QFileDialog.Directory)
      elif key == QtCore.Qt.Key_Backspace:
        self.removeCompletedFiles()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_M:
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
      if key == QtCore.Qt.Key_W or key == QtCore.Qt.Key_Up:
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

    if not hasattr(self, '_filepaths'):
      self._filepaths = []
    else:
      print([filepath for filepath in self._filepaths])
    self._new_filepaths = []
    self._invalid_filepaths = []

    if (fileMode == QtWidgets.QFileDialog.Directory):
      directory = self._fileDialog.getExistingDirectory()
      # print('Directory selected is ' + directory)
      for root, dirs, files in os.walk(directory):
        for file in files:
          if file.endswith(settings.SUPPORTED_FILETYPES):
            if file in self._filepaths:
              self._invalid_filepaths.append(os.path.join(root, file))
            else:
              self._filepaths.append(os.path.join(root, file))
              self._new_filepaths.append(os.path.join(root, file))
          else:
            self._invalid_filepaths.append(os.path.join(root, file))
    else:
      files = self._fileDialog.getOpenFileNames()
      # print('Files selected are ' + str(files))
      try:
        for file in files[0]:
          if file.endswith(settings.SUPPORTED_FILETYPES):
            if file in self._filepaths:
              self._invalid_filepaths.append(file)
            else:
              self._filepaths.append(file)
              self._new_filepaths.append(file)
          else:
            self._invalid_filepaths.append(file)
      except:
        pass

    # Show an error message for each invalid filepath found
    if self._invalid_filepaths:
      message = '<b>Some files couldn\'t be added!</b><br>Make sure that it is a valid filetype, and that it hasn\'t already been added.<br><br>▸ ' + '<br>▸ '.join(self._invalid_filepaths)
      messageDialog = QtWidgets.QErrorMessage(self)
      messageDialog.showMessage(message)

    # Start another thread for network requests to not block the GUI thread
    self._fetch_thread = LyricGrabberThread(self, self._new_filepaths)
    self._fetch_thread.start()

    self._fetch_thread.addFileToList.connect(self.addFileToList)
    self._fetch_thread.setProgressIcon.connect(self.setProgressIcon)
    self._fetch_thread.setLyrics.connect(self.setLyrics)

  def addFileToList(self, artist, title, art, filepath):
    # Create WidgetItem for each item
    listWidgetItem = QWidgetItem(self)
    listWidgetItem.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
    listWidgetItem.setProgressIcon(states.NOT_STARTED, self.devicePixelRatio())
    listWidgetItem.setAlbumArt(art, self.devicePixelRatio())
    listWidgetItem.setArtistText(artist)
    listWidgetItem.setTitleText(title)
    listWidgetItem.setfilepath(filepath)
    if self._mainScrollAreaWidgetLayout.count() % 2:
      listWidgetItem.setBackgroundColor(QtGui.QColor(245, 245, 245))
    else:
      listWidgetItem.setBackgroundColor(QtCore.Qt.white)
    # Add ListQWidgetItem into mainScrollAreaWidgetLayout
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
      if i % 2:
        self._mainScrollAreaWidgetLayout.itemAt(i).widget().setBackgroundColor(QtGui.QColor(245, 245, 245))
      else:
        self._mainScrollAreaWidgetLayout.itemAt(i).widget().setBackgroundColor(QtCore.Qt.white)

  def removeAllFilesFromList(self):
    if QWidgetItem.dialog:
      QWidgetItem.dialog.close()
    for i in reversed(range(self._mainScrollAreaWidgetLayout.count())):
      self._mainScrollAreaWidgetLayout.itemAt(i).widget().setParent(None)
    if hasattr(self, '_filepaths'):
      self._filepaths.clear()

  def removeCompletedFiles(self):
    if QWidgetItem.dialog:
      QWidgetItem.dialog.close()
    for i in reversed(range(self._mainScrollAreaWidgetLayout.count())):
      if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.COMPLETE:
        self._filepaths.remove(self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath())
        self._mainScrollAreaWidgetLayout.itemAt(i).widget().setParent(None)
    self.resetListColours()

  def openSettingsDialog(self):
    self.setEnabled(False)
    self._dialog = settings_dialog.QSettingsDialog()
    self._dialog.exec()
    self.setEnabled(True)