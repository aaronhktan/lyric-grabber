import subprocess

try:
  from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from gui import appearance
from gui import detail_dialog
from modules.logger import logger
from modules import utils
from threads.single_lyric_grabber_thread import SingleLyricGrabberThread

class states:
  NOT_STARTED = 0
  ERROR = 1
  IN_PROGRESS = 2
  COMPLETE = 3

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
    if utils.IS_WINDOWS:
      self._openButton.setFixedWidth(self._lyricsButton.minimumSizeHint().width()+50)
      self._lyricsButton.setFixedWidth(self._lyricsButton.minimumSizeHint().width()+50)
    else:
      self._openButton.setFixedWidth(self._openButton.sizeHint().width())
      self._lyricsButton.setFixedWidth(self._openButton.sizeHint().width())
    self._openButton.clicked.connect(lambda: self.openFilepath())
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

  def openFilepath(self):
    # QtGui.QDesktopServices.openUrl(QtCore.QUrl('file://' + self._filepath))
    if utils.IS_MAC:
      subprocess.run(['open', '-R', self._filepath])
    elif utils.IS_WINDOWS:
      subprocess.run('explorer /select,"{}"'.format(self._filepath.replace('/', '\\')))
    else:
      subprocess.run(['xdg-open', os.path.dirname(self._filepath)])

  def fetchLyrics(self, artist=None, title=None, url=None, source=None):
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

  def getLyrics(self):
    return self._lyrics

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

  def resetSelectedWidgetIndex(self):
    self.parent.setSelectedWidget(None)

  def removeFromList (self):
    self.setParent(None)
    QWidgetItem.dialog.close()
    self.resetColours()
    self.resetSelectedWidgetIndex()