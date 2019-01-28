import subprocess
import os

try:
  from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from gui import appearance
from gui import detail_dialog
from modules.logger import logger
from modules import utils
from threads.single_lyric_grabber_thread import SingleLyricGrabberThread
from threads.states import states

class SongWidget (QtWidgets.QWidget):

  """SongWidget represents a widget for a song in the list view.
  
  Attributes:
      dialog (LyricsDialog): The single dialog window that is opened when a song is selected
      parent (MainWindow): The window that contains this song widget
  """
  
  dialog = None;

  def __init__(self, parent):
    super().__init__(parent)

    self.parent = parent

    # Add label for progress icon
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
    if utils.IS_MAC and not utils.IS_MACOS_DARK_MODE:
      self._lyricsButton.pressed.connect(lambda: self._lyricsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/lyrics_inverted.png'))))
      self._lyricsButton.released.connect(lambda: self._lyricsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/lyrics.png'))))
    elif utils.IS_MACOS_DARK_MODE:
      self._lyricsButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/lyrics_inverted.png')))
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
    # self._removeButton.clicked.connect(lambda: self.removeFromList())

    self._buttonVBoxLayout = QtWidgets.QVBoxLayout()
    self._buttonVBoxLayout.addWidget(self._lyricsButton)
    self._buttonVBoxLayout.addWidget(self._openButton)
    # self._buttonVBoxLayout.addWidget(self._removeButton)
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
      self.mouseReleaseEvent = self.openDetailDialog()

  def setBackgroundColor(self, backgroundColor):
    """Sets background color of a song widget
    
    Args:
        backgroundColor (Qt.GlobalColor): A Qt named colour
    """
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
    """Sets album art in song widget
    
    Args:
        imageData (bytes): A bytes literal containing embedded album art
        deviceRatio (int): Pixel ratio of the screen that this program runs on
    """
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

  def getTitleText(self):
    return self._title

  def setArtistText(self, text):
    self._artist = text
    self._textArtistLabel.setText(text)

  def getArtistText(self):
    return self._artist

  def openDetailDialog(self):
    self.parent.setSelectedWidget(self._filepath)
    self.resetColours()
    self.setBackgroundColor(appearance.HIGHLIGHT_COLOUR)
    try:
      SongWidget.dialog.setWindowTitle('{artist} - {title}'.format(artist=self._artist, title=self._title))
      SongWidget.dialog.updateLyrics(self._lyrics)
      SongWidget.dialog.updateUrl(self._url)
      SongWidget.dialog.setFilepath(self._filepath)
      SongWidget.dialog.setArtistAndTitle(self._artist, self._title)
      SongWidget.dialog.setParent(self)
      SongWidget.dialog.raise_()
      SongWidget.dialog.show()
    except Exception as e:
      SongWidget.dialog = detail_dialog.LyricsDialog(parent=self,
                                                     artist=self._artist,
                                                     title=self._title,
                                                     lyrics=self._lyrics,
                                                     url=self._url,
                                                     filepath=self._filepath)
      SongWidget.dialog.raise_()
      SongWidget.dialog.show()
      self.activateWindow()

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
    """Grab lyrics again from the Internet
    
    Args:
        artist (string, optional): Song artist
        title (string, optional): Song title
        url (string, optional): Source URL
        source (string, optional): Source name (e.g. 'Genius')
    """
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
      if SongWidget.dialog is not None:
        if SongWidget.dialog.getFilepath() == self._filepath:
          SongWidget.dialog.updateLyrics(lyrics)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def saveLyrics(self, lyrics):
    try:
      self._lyrics = lyrics
      self._settings = settings.Settings()
      lyric_grabber.write_file(artist=self._artist,
                               title=self._title,
                               write_info=self._settings.info,
                               write_metadata=self._settings.metadata,
                               write_text=self._settings.text,
                               lyrics=lyrics,
                               song_filepath=self._filepath)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def setUrl(self, url):
    self._url = url
    try:
      if SongWidget.dialog is not None:
        if SongWidget.dialog.getFilepath() == self._filepath:
          SongWidget.dialog.updateUrl(url)
    except Exception as e:
      logger.log(logger.LOG_LEVEL_ERROR, str(e))

  def resetColours(self):
    self.parent.resetListColours()

  def resetSelectedWidgetIndex(self):
    self.parent.setSelectedWidget(None)

  def removeFromList(self):
    self.setParent(None)
    SongWidget.dialog.close()
    self.resetColours()
    self.resetSelectedWidgetIndex()