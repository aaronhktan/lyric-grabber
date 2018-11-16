from PyQt5 import QtCore, QtGui, QtWidgets

from modules import settings
from modules import utils

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class LyricsDialog (QtWidgets.QWidget):
  x_coordinate = None
  y_coordinate = None

  def __init__(self, parent, artist, title, lyrics, url, filepath):
    """This is the dialog that shows more details about a particular song
    
    Args:
        parent (QWidget): The song widget that cause this dialog to pop up
        artist (string): Song artist
        title (string): Song title
        lyrics (string): Song lyrics
        url (string): Source for the song lyrics
        filepath (string): Filepath for the song
    """
    super().__init__(parent, QtCore.Qt.Window)
    # Must pass QtCore.Qt.Window as parameter to ensure that widget is displayed in new window
    # rather than added as child of the song widget that caused it to open

    self.parent = parent

    # Style lyrics dialog
    self.setWindowTitle('{artist} - {title}'.format(artist=artist, title=title))
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    flags = self.windowFlags() | QtCore.Qt.CustomizeWindowHint
    flags &= ~(QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowFullscreenButtonHint)
    self.setWindowFlags(flags)

    self._settings = settings.Settings()

    self._filepath = filepath

    # Add lyrics label and scroll area
    self._lyricsQLabel = QtWidgets.QTextEdit()
    self._lyricsQLabel.setText(lyrics)
    if utils.IS_MACOS_DARK_MODE:
      self._lyricsQLabel.verticalScrollBar().setStyleSheet('\
        QScrollBar::handle:vertical { \
          background: #696969; \
          min-height: 0px; \
        }')
      self._lyricsQLabel.setStyleSheet('background-color:dimgrey;')
    self._lyricsQLabel.setAlignment(QtCore.Qt.AlignTop)
    self._lyricsQLabel.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
    self._lyricsQLabel.setContentsMargins(10, 10, 0, 10)

    # Add buttons at bottom of screen
    self._lyricsCopyButton = QtWidgets.QPushButton('Copy')
    self._lyricsCopyButton.setMaximumWidth(125)
    self._lyricsCopyButton.clicked.connect(lambda: self.copyLyrics())
    self._lyricsSaveButton = QtWidgets.QPushButton('Save')
    self._lyricsSaveButton.setMaximumWidth(125)
    self._lyricsHorizontalSpacer = QtWidgets.QSpacerItem(0, 0,
                                                         QtWidgets.QSizePolicy.Expanding,
                                                         QtWidgets.QSizePolicy.Minimum)
    self._lyricsSaveButton.clicked.connect(lambda: self.saveLyrics())
    self._lyricsClearButton = QtWidgets.QPushButton('Remove')
    self._lyricsClearButton.setMaximumWidth(125)
    self._lyricsClearButton.clicked.connect(lambda: self.removeLyrics())

    # Layout containing both scroll area and buttons
    self._lyricsGridLayout = QtWidgets.QGridLayout()
    self._lyricsGridLayout.addWidget(self._lyricsQLabel, 0, 0, 1, -1)
    self._lyricsGridLayout.addWidget(self._lyricsCopyButton, 1, 0, 1, 1)
    self._lyricsGridLayout.addWidget(self._lyricsSaveButton, 1, 1, 1, 1)
    self._lyricsGridLayout.addItem(self._lyricsHorizontalSpacer, 1, 2, 1, -1)
    self._lyricsGridLayout.addWidget(self._lyricsClearButton, 1, 3, 1, 1)
    self._lyricsGridLayout.setContentsMargins(10, 10, 10, 10)
    self._lyricsGridLayout.setSpacing(10)

    self._lyricsWidget = QtWidgets.QWidget()
    self._lyricsWidget.setLayout(self._lyricsGridLayout)

    # Add metadata editing tab
    # Lyrics URL sections
    self._urlLabel = QtWidgets.QLabel('Lyrics URL:')
    self._urlLineEdit = QtWidgets.QLineEdit()
    if utils.IS_MACOS_DARK_MODE:
      self._urlLineEdit.setStyleSheet('background-color:dimgrey;');

    self._urlLineEdit.setText(url)
    self._urlLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._urlLineEdit.setCursorPosition(0)

    self._urlExplanationLabel = QtWidgets.QLabel('If you input a valid link,'
        ' Quaver can get lyrics from that page when you click the "Grab lyrics" button.')
    self._urlExplanationLabel.setWordWrap(True)

    self._viewUrlButton = QtWidgets.QPushButton('View online')
    self._viewUrlButton.clicked.connect(lambda: self.openUrl())
    self._viewUrlButton.setMaximumWidth(150)
    if not utils.IS_MACOS_DARK_MODE:
      self._copyUrlButton = QtWidgets.QPushButton(
          QtGui.QIcon(utils.resource_path('./assets/copy.png')), 'Copy URL')
      if utils.IS_MAC:
        self._copyUrlButton.pressed.connect(lambda: self._copyUrlButton.setIcon(
          QtGui.QIcon(utils.resource_path('./assets/copy_inverted.png'))))
        self._copyUrlButton.released.connect(lambda: self._copyUrlButton.setIcon(
          QtGui.QIcon(utils.resource_path('./assets/copy.png'))))
    elif utils.IS_MACOS_DARK_MODE:
      self._copyUrlButton = QtWidgets.QPushButton(
          QtGui.QIcon(utils.resource_path('./assets/copy_inverted.png')), 'Copy URL')
    self._copyUrlButton.clicked.connect(lambda: self.copyUrl())
    self._fetchAgainLinkButton = QtWidgets.QPushButton('Grab Lyrics')
    self._fetchAgainLinkButton.setMaximumWidth(150)
    self._fetchAgainLinkButton.clicked.connect(lambda: self.grabLyrics())
    self._fetchAgainLinkButton.setAutoDefault(True)

    # Separator Line
    self._separatorLineFrame = QtWidgets.QFrame()
    self._separatorLineFrame.setFrameShape(QtWidgets.QFrame.HLine)
    self._separatorLineFrame.setFrameShadow(QtWidgets.QFrame.Raised)

    # Actual metadata
    self._titleLabel = QtWidgets.QLabel('Title:')
    self._titleLineEdit = QtWidgets.QLineEdit()
    if utils.IS_MACOS_DARK_MODE:
      self._titleLineEdit.setStyleSheet('background-color:dimgrey;');
    self._titleLineEdit.setText(title)
    self._titleLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)

    self._artistLabel = QtWidgets.QLabel('Artist:')
    self._artistLineEdit = QtWidgets.QLineEdit()
    if utils.IS_MACOS_DARK_MODE:
      self._artistLineEdit.setStyleSheet('background-color:dimgrey;');
    self._artistLineEdit.setText(artist)
    self._artistLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)

    # Source
    self._sourceLabel = QtWidgets.QLabel('Source:')
    self._sourceLabelComboBox = QtWidgets.QComboBox()
    self._sourceLabelComboBox.setMaximumWidth(150)
    for source in utils.SUPPORTED_SOURCES:
      self._sourceLabelComboBox.addItem(source)
    index = self._sourceLabelComboBox.findText(self._settings.source, QtCore.Qt.MatchFixedString)
    if index >= 0:
      self._sourceLabelComboBox.setCurrentIndex(index)

    # Explanation
    self._metadataExplanationLabel = QtWidgets.QLabel('You can change the title or artist'
        ' that Quaver will look for in these text boxes.'
        ' When you click the "Grab lyrics" button, Quaver will use this new information.')
    self._metadataExplanationLabel.setWordWrap(True)

    # Spacer
    self._verticalSpacer = QtWidgets.QSpacerItem(0, 0,
                                                 QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Expanding)

    # Try again button
    self._fetchAgainSpacer = QtWidgets.QSpacerItem(0, 0,
                                                   QtWidgets.QSizePolicy.Expanding,
                                                   QtWidgets.QSizePolicy.Minimum)
    self._fetchAgainMetadataButton = QtWidgets.QPushButton('Grab lyrics')
    self._fetchAgainMetadataButton.clicked.connect(lambda: self.grabLyrics(use_url=False))
    self._fetchAgainMetadataButton.setAutoDefault(True)

    # Add to layout
    self._metadataLayout = QtWidgets.QGridLayout()
    self._metadataLayout.addWidget(self._urlLabel, 0, 0, 1, -1)
    self._metadataLayout.addWidget(self._urlLineEdit, 1, 0, 1, -1)
    self._metadataLayout.addWidget(self._viewUrlButton, 2, 1, 1, 1)
    self._metadataLayout.addWidget(self._copyUrlButton, 2, 2, 1, 1)
    self._metadataLayout.addWidget(self._urlExplanationLabel, 3, 0, 1, -1)
    self._metadataLayout.addWidget(self._fetchAgainLinkButton, 4, 2, 1, 1)
    self._metadataLayout.addWidget(self._separatorLineFrame, 5, 0, 1, -1)
    self._metadataLayout.addWidget(self._titleLabel, 6, 0, 1, -1)
    self._metadataLayout.addWidget(self._titleLineEdit, 7, 0, 1, -1)
    self._metadataLayout.addWidget(self._artistLabel, 8, 0, 1, -1)
    self._metadataLayout.addWidget(self._artistLineEdit, 9, 0, 1, -1)
    self._metadataLayout.addWidget(self._sourceLabel, 10, 0, 1, -1)
    self._metadataLayout.addWidget(self._sourceLabelComboBox, 10, 2, 1, -1)
    self._metadataLayout.addWidget(self._metadataExplanationLabel, 11, 0, 1, -1)
    self._metadataLayout.addItem(self._verticalSpacer, 12, 0, 1, -1)
    self._metadataLayout.addItem(self._fetchAgainSpacer, 13, 0, 1, -1)
    self._metadataLayout.addWidget(self._fetchAgainMetadataButton, 13, 2, 1, -1)
    self._metadataLayout.setSpacing(10)
    # self._metadataLayout.setContentsMargins(10, 10, 10, 10)

    self._metadataWidget = QtWidgets.QWidget()
    self._metadataWidget.setLayout(self._metadataLayout)

    # Add tabs
    self._lyricsTabWidget = QtWidgets.QTabWidget()
    self._lyricsTabWidget.addTab(self._lyricsWidget, 'Lyrics')
    self._lyricsTabWidget.addTab(self._metadataWidget, 'Metadata')

    # Add navigation buttons
    self._previousSongButton = QtWidgets.QPushButton('Previous')
    self._previousSongButton.clicked.connect(self.parent.parent.viewPreviousWidget)
    self._songNavigationSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._nextSongButton = QtWidgets.QPushButton('Next')
    self._nextSongButton.clicked.connect(self.parent.parent.viewNextWidget)

    # Add layouts to main widget
    self._allQGridLayout = QtWidgets.QGridLayout()
    self._allQGridLayout.addWidget(self._lyricsTabWidget, 0, 0, 1, 3)
    self._allQGridLayout.addWidget(self._previousSongButton, 1, 0, 1, 1)
    self._allQGridLayout.addItem(self._songNavigationSpacer, 1, 1, 1, 1)
    self._allQGridLayout.addWidget(self._nextSongButton, 1, 2, 1, 1)
    self.setLayout(self._allQGridLayout)

    # Set allowable sizes for this dialog
    self.resize(self.sizeHint())
    self.setMinimumSize(self.sizeHint())

    # Move dialog to last position on macOS, otherwise move it to match vertical position of parent window
    if LyricsDialog.x_coordinate is not None \
    and LyricsDialog.y_coordinate is not None \
    and utils.IS_MAC:
      # print('Read as {}, {}'.format(LyricsDialog.x_coordinate, LyricsDialog.y_coordinate))
      # if utils.IS_MAC:
      self.move(LyricsDialog.x_coordinate, LyricsDialog.y_coordinate)
      # elif utils.IS_WINDOWS:
      #   self.move(LyricsDialog.x_coordinate - 8 * self.devicePixelRatio(), LyricsDialog.y_coordinate - 31 * self.devicePixelRatio())
    else:
      x = parent.size().width() + self.mapToGlobal(parent.parent.pos()).x() + 25 * self.devicePixelRatio()
      y = self.mapToGlobal(parent.parent.pos()).y() - (25 * self.devicePixelRatio() if utils.IS_MAC else 0)
      self.move(x if (x + self.width() < QtWidgets.QDesktopWidget().availableGeometry().width()) \
                  else QtWidgets.QDesktopWidget().availableGeometry().width() - self.width(),
                y if y > 0 else 0)

  def closeEvent(self, event):
    self.parent.resetColours()
    self.parent.resetSelectedWidgetIndex()
    event.accept()

  def keyPressEvent(self, event):
    key = event.key()
    if event.modifiers() & QtCore.Qt.ShiftModifier and event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_F:
        self.showFullScreen()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_K:
        self.openUrl()
      elif key == QtCore.Qt.Key_S:
        self.saveLyrics()
      elif key == QtCore.Qt.Key_Backspace:
        self.removeLyrics()
    elif key == QtCore.Qt.Key_Escape:
      self.close()

  def undoEvent(self):
    undoEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Z, QtCore.Qt.ControlModifier)
    QtCore.QCoreApplication.sendEvent(self._lyricsQLabel, undoEvent)

  def redoEvent(self):
    redoEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Z, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
    QtCore.QCoreApplication.sendEvent(self._lyricsQLabel, redoEvent)

  def moveEvent(self, event):
    LyricsDialog.x_coordinate = event.pos().x()
    LyricsDialog.y_coordinate = event.pos().y()
    # print('Set as {}, {}'.format(LyricsDialog.x_coordinate, LyricsDialog.y_coordinate))

  def updateMetadata(self, artist, title):
    self.setWindowTitle('{artist} - {title}'.format(artist=artist, title=title))
    self._titleLineEdit.setText(title)
    self._artistLineEdit.setText(artist)

  def updateLyrics(self, lyrics):
    self._lyricsQLabel.setText(lyrics)
    self._lyricsQLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

  def copyLyrics(self):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.clear(mode=clipboard.Clipboard)
    clipboard.setText(self._lyricsQLabel.toPlainText(), mode=QtGui.QClipboard.Clipboard)

  def saveLyrics(self):
    lyrics = self._lyricsQLabel.toPlainText()
    self.parent.saveLyrics(lyrics)

  def removeLyrics(self):
    self._lyricsQLabel.setText('')
    self.parent.saveLyrics(' ')

  def updateUrl(self, url):
    self._urlLineEdit.setText(url)

  def openUrl(self):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._urlLineEdit.text()))

  def copyUrl(self):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.clear(mode=clipboard.Clipboard)
    clipboard.setText(self._urlLineEdit.text(), mode=QtGui.QClipboard.Clipboard)

  def setArtistAndTitle(self, artist, title):
    self._artistLineEdit.setText(artist)
    self._titleLineEdit.setText(title)

  def grabLyrics(self, use_url=True):
    if use_url: # This means we should fetch based on URL
      title = self._titleLineEdit.text()
      url = self._urlLineEdit.text()
      # print(title, url)
      self.parent.fetchLyrics(title=title, url=url)
    else:
      artist = self._artistLineEdit.text()
      title = self._titleLineEdit.text()
      source = self._sourceLabelComboBox.currentText()
      # print(source)
      self.parent.fetchLyrics(artist=artist,
        title=title, source=source)

  def getFilepath(self):
    return self._filepath

  def setFilepath(self, filepath):
    self._filepath = filepath

  def setParent(self, parent):
    self.parent = parent