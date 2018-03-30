from modules.logger import logger
from gui import detail_dialog
from modules import lyric_grabber
from gui import settings_dialog
from modules.settings import Settings

import base64
# from colorthief import ColorThief
from concurrent import futures
import os
from PyQt5 import QtCore, QtGui, QtWidgets

class states:
  NOT_STARTED = 0
  ERROR = 1
  IN_PROGRESS = 2
  COMPLETE = 3

class LyricGrabberThread (QtCore.QThread):
  addFileToList = QtCore.pyqtSignal(['QString', 'QString', bytes, 'QString'])
  setProgressIcon = QtCore.pyqtSignal(['QString', int])
  setLyrics = QtCore.pyqtSignal(['QString', 'QString'])

  def __init__(self, parent, filepaths):
    super().__init__()
    self._filepaths = filepaths

    self._settings = Settings()

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
      self._metadataResults.append(self._metadataExecutor.submit(lyric_grabber.get_metadata, True, filepath))

    # Create and show items in list as metadata finishes fetching
    for result in futures.as_completed(self._metadataResults):
      try:
        if result.result().succeeded:
          if result.result().art is None:
            self.addFileToList.emit(result.result().artist, result.result().title, b'', result.result().filepath)
          else:
            self.addFileToList.emit(result.result().artist, result.result().title, result.result().art, result.result().filepath)
          self._songs.append(result.result())
        else:
          logger.log(logger.LOG_LEVEL_INFO, 'No metadata found: ' + result.result().message)
          # self._badSongs.append(result.result()[2])
          # print(self.badSongs)
      except Exception as e:
        logger.log(logger.LOG_LEVEL_ERROR, ' Exception ocurred while adding file {filepath}: {error}'.format(filepath=result.result().filepath, error=str(e)))

    for song in self._songs:
      self.setProgressIcon.emit(result.result().filepath, states.IN_PROGRESS)
      self._lyricsResults.append(self._lyricsExecutor.submit(lyric_grabber.get_lyrics, self._settings.get_approximate(), not self._settings.get_remove_brackets(), song.artist, song.title, self._settings.get_source().lower(), song.filepath))

    for result in futures.as_completed(self._lyricsResults):
      try:
        if result.result().succeeded and result.result().lyrics:
          self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)
          self.setLyrics.emit(result.result().filepath, result.result().lyrics)
          self._fileWritingResults.append(self._fileWritingExecutor.submit(lyric_grabber.write_file, result.result().artist, result.result().title, self._settings.get_tag(), result.result().lyrics, result.result().filepath))
        elif not result.result().lyrics:
          self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        else:
          self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)
          self.setLyrics.emit(result.result().filepath, result.result().lyrics)
          self._fileWritingResults.append(self._fileWritingExecutor.submit(lyric_grabber.write_file, result.result().artist, result.result().title, self._settings.get_tag(), result.result().lyrics, result.result().filepath))
      except Exception as e:
        self.setProgressIcon.emit(result.result().filepath, states.ERROR)
        logger.log(logger.LOG_LEVEL_ERROR, ' Exception ocurred while getting lyrics for file {filepath}: {error}'.format(filepath=result.result().filepath, error=str(e)))

    for result in futures.as_completed(self._fileWritingResults):
      self.setProgressIcon.emit(result.result().filepath, states.COMPLETE)
      print(result.result().message)

class QWidgetItem (QtWidgets.QWidget):
  # self.largeFont = QtGui.QFont('Gill Sans', 18, QtGui.QFont.Bold)
  largeFont = QtGui.QFont('Gill Sans', 18)
  dialog = None;

  def __init__(self, parent):
    super().__init__(parent)

    # Add progress label
    self._progressLabel = QtWidgets.QLabel()
    self._progressLabel.setFixedWidth(30)
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
    self._lyricsButton = QtWidgets.QPushButton('View Lyrics')
    self._lyricsButton.setMaximumWidth(125)
    self._lyricsButton.clicked.connect(lambda: self.openDetailDialog())
    self._openButton = QtWidgets.QPushButton('Open in Finder')
    self._openButton.setMaximumWidth(125)
    self._openButton.clicked.connect(lambda: self.openFilePath())
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

  def mousePressEvent(self, QMouseEvent):
      if QMouseEvent.button() == QtCore.Qt.LeftButton:
        self.mouseReleaseEvent = self.openDetailDialog()

  def setBackgroundColor(self, backgroundColor):
    self._pal = QtGui.QPalette()
    self._pal.setColor(QtGui.QPalette.Background, backgroundColor)
    self.setAutoFillBackground(True)
    self.setPalette(self._pal)

  def setProgressIcon(self, imagePath, deviceRatio):
    self._progressIcon = QtGui.QPixmap(imagePath)
    self._progressIcon.setDevicePixelRatio(deviceRatio)
    self._progressLabel.setPixmap(self._progressIcon)

  def setAlbumArt(self, imageData, deviceRatio):
    try:
      if imageData is not None:
        if imageData == b'':
          self._albumImage = QtGui.QImage('./assets/art_empty.png')
        else:
          self._albumImage = QtGui.QImage.fromData(imageData)
        self._albumIcon = QtGui.QPixmap.fromImage(self._albumImage)
        self._albumIcon.setDevicePixelRatio(deviceRatio)
        self._iconWidth = deviceRatio * (self._albumArtLabel.width() - 10)
        self._iconHeight = deviceRatio * (self._albumArtLabel.height() - 10)
        self._albumArtLabel.setPixmap(self._albumIcon.scaled(self._iconWidth, self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    except:
      print('Error setting album art.')

  def setTitleText(self, text):
    self._title = text
    self._textTitleLabel.setText(text)

  def setArtistText(self, text):
    self._artist = text
    self._textArtistLabel.setText(text)

  def openDetailDialog(self):
    # self.window().setEnabled(False)
    QWidgetItem.dialog = detail_dialog.QLyricsDialog(self._artist, self._title, self._lyrics, self._filePath)
    QWidgetItem.dialog.show()
    # self.window().setEnabled(True)

  def setFilePath(self, filePath):
    self._filePath = filePath

  def getFilePath(self):
    return self._filePath

  def openFilePath(self):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl('file://' + self.filePath))

  def setLyrics(self, lyrics):
    self._lyrics = lyrics
    try:
      if self.dialog is not None:
        if self.dialog.getFilePath() == self._filePath:
          self.dialog.updateLyrics(lyrics)
    except Exception as e:
      print(e)

  # def removeFile (self):
  #   self.setParent(None)

class MainWindow (QtWidgets.QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()

    # Style main window
    self.setMinimumSize(600, 400)
    self.setUnifiedTitleAndToolBarOnMac(True)

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

  def openFileDialog(self, fileMode):
    # fileMode parameter is QtWidgets.QFileDialog.Directory or QtWidgets.QFileDialog.ExistingFiles
    self._fileDialog = QtWidgets.QFileDialog()
    self._fileDialog.setFileMode(fileMode)
    self._fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

    self._filepaths = []

    if (fileMode == QtWidgets.QFileDialog.Directory):
      directory = self._fileDialog.getExistingDirectory()
      # print('Directory selected is ' + directory)
      for root, dirs, files in os.walk(directory):
        for file in files:
          if file.endswith(lyric_grabber.SUPPORTED_FILETYPES):
            self._filepaths.append(os.path.join(root, file))
    else:
      files = self._fileDialog.getOpenFileNames()
      # print('Files selected are ' + str(files))
      try:
        for file in files[0]:
          if file.endswith(lyric_grabber.SUPPORTED_FILETYPES):
            self._filepaths.append(file)
      except:
        pass

    self._fetch_thread = LyricGrabberThread(self, self._filepaths)
    self._fetch_thread.start()

    self._fetch_thread.addFileToList.connect(self.addFileToList)
    self._fetch_thread.setProgressIcon.connect(self.setProgressIcon)
    self._fetch_thread.setLyrics.connect(self.setLyrics)

  def addFileToList(self, artist, title, art, filepath):
    # Create WidgetItem for each item
    listWidgetItem = QWidgetItem(self)
    listWidgetItem.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
    listWidgetItem.setProgressIcon('./assets/not_started.png', self.devicePixelRatio())
    listWidgetItem.setAlbumArt(art, self.devicePixelRatio())
    listWidgetItem.setArtistText(artist)
    listWidgetItem.setTitleText(title)
    listWidgetItem.setFilePath(filepath)
    if self._mainScrollAreaWidgetLayout.count() % 2:
      listWidgetItem.setBackgroundColor(QtGui.QColor(245, 245, 245))
    else:
      listWidgetItem.setBackgroundColor(QtCore.Qt.white)
    # Add ListQWidgetItem into mainScrollAreaWidgetLayout
    self._mainScrollAreaWidgetLayout.addWidget(listWidgetItem)

  def setProgressIcon(self, filepath, state):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilePath() == filepath:
        if state == states.IN_PROGRESS:
          widgetItem.setProgressIcon('./assets/in_progress.png', self.devicePixelRatio())
        elif state == states.ERROR:
          widgetItem.setProgressIcon('./assets/error.png', self.devicePixelRatio())
        elif state == states.COMPLETE:
          widgetItem.setProgressIcon('./assets/complete.png', self.devicePixelRatio())

  def setLyrics(self, filepath, lyrics):
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilePath() == filepath:
        widgetItem.setLyrics(lyrics)

  def removeAllFilesFromList(self):
    for i in reversed(range(self._mainScrollAreaWidgetLayout.count())): 
      self._mainScrollAreaWidgetLayout.itemAt(i).widget().setParent(None)

  def openSettingsDialog(self):
    self.setEnabled(False)
    self._dialog = settings_dialog.QSettingsDialog()
    self._dialog.exec()
    self.setEnabled(True)