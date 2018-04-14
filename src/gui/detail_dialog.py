from modules import settings
from modules import utils

from PyQt5 import QtCore, QtGui, QtWidgets

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class QLyricsDialog (QtWidgets.QDialog):
  # smallFont = QtGui.QFont('San Francisco', 12)
  x_coordinate = None
  y_coordinate = None

  def __init__(self, parent, artist, title, lyrics, url, filepath):
    super().__init__(parent)

    # Set parent object
    self.parent = parent
    self.parent.resetColours()
    self.parent.setBackgroundColor(QtGui.QColor(170, 211, 255))

    # Style lyrics dialog
    # self.setFixedSize(QtCore.QSize(300, 700))
    self.setModal(False)
    self.setWindowTitle('{artist} - {title}'.format(artist=artist, title=title))
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    self._settings = settings.Settings()

    # Add a menubar
    self._grabAction = QtWidgets.QAction('Re-fetch Lyrics', self)
    self._grabAction.setShortcut('Ctrl+R')
    self._grabAction.triggered.connect(lambda: self.grabLyrics())
    self._openUrlAction = QtWidgets.QAction('Open Lyrics in Browser')
    self._openUrlAction.setShortcut('Ctrl+K')
    self._openUrlAction.triggered.connect(lambda: self.openUrl())
    self._closeAction = QtWidgets.QAction('Close')
    self._closeAction.setShortcut('Esc')
    self._closeAction.triggered.connect(lambda: self.close())

    self._saveAction = QtWidgets.QAction('Save Lyrics', self)
    self._saveAction.setShortcut('Ctrl+S')
    self._saveAction.triggered.connect(lambda: self.saveLyrics())
    self._removeAction = QtWidgets.QAction('Remove Lyrics', self)
    self._removeAction.setShortcut('Ctrl+Backspace')
    self._removeAction.triggered.connect(lambda: self.removeLyrics())

    self._showNormalAction = QtWidgets.QAction('Bring to Front', self)
    self._showNormalAction.triggered.connect(lambda: self.showNormal())
    self._fullScreenAction = QtWidgets.QAction('Enter Fullscreen', self)
    self._fullScreenAction.setShortcut('Ctrl+Shift+F')
    self._fullScreenAction.triggered.connect(lambda: self.showFullScreen())

    self._menuBar = QtWidgets.QMenuBar()

    self._fileMenu = self._menuBar.addMenu('File')
    self._fileMenu.addAction(self._grabAction)
    self._fileMenu.addAction(self._openUrlAction)
    self._fileMenu.addSeparator()
    self._fileMenu.addAction(self._closeAction)
    self._editMenu = self._menuBar.addMenu('Edit')
    self._editMenu.addAction(self._saveAction)
    self._editMenu.addAction(self._removeAction)
    self._windowMenu = self._menuBar.addMenu('Window')
    self._windowMenu.addAction(self._fullScreenAction)
    self._windowMenu.insertSeparator(self._showNormalAction)
    self._windowMenu.addAction(self._showNormalAction)

    # Add filepath
    self._filepath = filepath

    # Add lyrics label and scroll area
    self._lyricsQLabel = QtWidgets.QTextEdit()
    self._lyricsQLabel.setText(lyrics)
    # self._lyricsQLabel.setStyleSheet('background-color:white;');
    self._lyricsQLabel.setAlignment(QtCore.Qt.AlignTop)
    self._lyricsQLabel.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
    self._lyricsQLabel.setContentsMargins(10, 10, 0, 10)

    # self._lyricsScrollArea = QtWidgets.QScrollArea()
    # self._lyricsScrollArea.setWidget(self._lyricsQLabel)
    # self._lyricsScrollArea.setWidgetResizable(True)
    # self._lyricsScrollArea.setMinimumHeight(400)
    # self._lyricsScrollArea.setStyleSheet('background:none;');

    # Add buttons at bottom of screen
    self._lyricsCopyButton = QtWidgets.QPushButton('Copy lyrics')
    self._lyricsCopyButton.setMaximumWidth(125)
    self._lyricsCopyButton.clicked.connect(lambda: self.copyLyrics())
    self._lyricsSaveButton = QtWidgets.QPushButton('Save lyrics')
    self._lyricsSaveButton.setMaximumWidth(125)
    self._lyricsHorizontalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._lyricsSaveButton.clicked.connect(lambda: self.saveLyrics())
    self._lyricsClearButton = QtWidgets.QPushButton('Remove lyrics')
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

    self._urlLineEdit.setText(url)
    self._urlLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._urlLineEdit.setCursorPosition(0)
    self._urlLineEdit.textEdited.connect(self.disableMetadataEditing)

    self._urlExplanationLabel = QtWidgets.QLabel('If you input a valid link, Lyric Grabber can get lyrics from that page when you click the "Grab lyrics" button.')
    self._urlExplanationLabel.setWordWrap(True)

    self._viewUrlButton = QtWidgets.QPushButton('View online')
    self._viewUrlButton.clicked.connect(lambda: self.openUrl())
    self._viewUrlButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._viewUrlButton.setMaximumWidth(150)
    self._copyUrlButton = QtWidgets.QPushButton(QtGui.QIcon(utils.resource_path('./assets/copy.png')), 'Copy URL')
    if utils.IS_MAC:
      self._copyUrlButton.pressed.connect(lambda: self._copyUrlButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/copy_inverted.png'))))
      self._copyUrlButton.released.connect(lambda: self._copyUrlButton.setIcon(QtGui.QIcon(utils.resource_path('./assets/copy.png'))))
    self._copyUrlButton.clicked.connect(lambda: self.copyUrl())
    self._copyUrlButton.setFocusPolicy(QtCore.Qt.NoFocus)

    # Separator Line
    self._separatorLineFrame = QtWidgets.QFrame();
    self._separatorLineFrame.setFrameShape(QtWidgets.QFrame.HLine)
    self._separatorLineFrame.setFrameShadow(QtWidgets.QFrame.Raised)

    # Actual metadata
    self._titleLabel = QtWidgets.QLabel('Title:')
    self._titleLineEdit = QtWidgets.QLineEdit()
    self._titleLineEdit.setText(title);
    self._titleLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._titleLineEdit.textEdited.connect(self.disableUrlEditing)

    self._artistLabel = QtWidgets.QLabel('Artist:')
    self._artistLineEdit = QtWidgets.QLineEdit()
    self._artistLineEdit.setText(artist);
    self._artistLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._artistLineEdit.textEdited.connect(self.disableUrlEditing)

    # Source
    self._sourceLabel = QtWidgets.QLabel('Source:')
    self._sourceLabelComboBox = QtWidgets.QComboBox()
    self._sourceLabelComboBox.setMaximumWidth(150)
    for source in settings.SUPPORTED_SOURCES:
      self._sourceLabelComboBox.addItem(source)
    index = self._sourceLabelComboBox.findText(self._settings.get_source(), QtCore.Qt.MatchFixedString)
    if index >= 0:
      self._sourceLabelComboBox.setCurrentIndex(index)

    # Explanation
    self._metadataExplanationLabel = QtWidgets.QLabel('You can try changing the title or artist that Lyric Grabber will look for in these text boxes. When you click the "Grab lyrics" button, Lyric Grabber will use this new information.')
    self._metadataExplanationLabel.setWordWrap(True)

    # Spacer
    self._verticalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    # Try again button
    self._fetchAgainSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._fetchAgainButton = QtWidgets.QPushButton('Grab lyrics again')
    self._fetchAgainButton.clicked.connect(lambda: self.grabLyrics())
    self._fetchAgainButton.setAutoDefault(True)
    self._fetchAgainButton.setEnabled(False)

    # Add to layout
    self._metadataLayout = QtWidgets.QGridLayout()
    self._metadataLayout.addWidget(self._urlLabel, 0, 0, 1, -1)
    self._metadataLayout.addWidget(self._urlLineEdit, 1, 0, 1, -1)
    self._metadataLayout.addWidget(self._urlExplanationLabel, 2, 0, 1, -1)
    self._metadataLayout.addWidget(self._viewUrlButton, 3, 1, 1, 1)
    self._metadataLayout.addWidget(self._copyUrlButton, 3, 2, 1, -1)
    self._metadataLayout.addWidget(self._separatorLineFrame, 4, 0, 1, -1)
    self._metadataLayout.addWidget(self._titleLabel, 5, 0, 1, -1)
    self._metadataLayout.addWidget(self._titleLineEdit, 6, 0, 1, -1)
    self._metadataLayout.addWidget(self._artistLabel, 7, 0, 1, -1)
    self._metadataLayout.addWidget(self._artistLineEdit, 8, 0, 1, -1)
    self._metadataLayout.addWidget(self._sourceLabel, 9, 0, 1, -1)
    self._metadataLayout.addWidget(self._sourceLabelComboBox, 9, 2, 1, -1)
    self._metadataLayout.addWidget(self._metadataExplanationLabel, 10, 0, 1, -1)
    self._metadataLayout.addItem(self._verticalSpacer, 11, 0, 1, -1)
    self._metadataLayout.addItem(self._fetchAgainSpacer, 12, 0, 1, -1)
    self._metadataLayout.addWidget(self._fetchAgainButton, 12, 2, 1, -1)
    # self._metadataLayout.setSpacing(0)
    # self._metadataLayout.setContentsMargins(10, 10, 10, 10)

    self._metadataWidget = QtWidgets.QWidget()
    self._metadataWidget.setLayout(self._metadataLayout)

    # Add tabs
    self._lyricsTabWidget = QtWidgets.QTabWidget()
    self._lyricsTabWidget.addTab(self._lyricsWidget, 'Lyrics')
    self._lyricsTabWidget.addTab(self._metadataWidget, 'Metadata')

    # Add navigation buttons
    # self._previousSongButton = QtWidgets.QPushButton('Previous Song')
    # self._songNavigationSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    # self._nextSongButton = QtWidgets.QPushButton('Next Song')

    # self._songNavigationWidgetLayout = QtWidgets.QHBoxLayout()
    # self._songNavigationWidgetLayout.addWidget(self._previousSongButton)
    # self._songNavigationWidgetLayout.addItem(self._songNavigationSpacer)
    # self._songNavigationWidgetLayout.addWidget(self._nextSongButton)

    # self._songNavigationWidget = QtWidgets.QWidget()
    # self._songNavigationWidget.setLayout(self._songNavigationWidgetLayout)

    # Add layouts to main widget
    self._allQVBoxLayout = QtWidgets.QVBoxLayout()
    self._allQVBoxLayout.addWidget(self._lyricsTabWidget)
    # self._allQVBoxLayout.addWidget(self._songNavigationWidget)
    self.setLayout(self._allQVBoxLayout)

    if QLyricsDialog.x_coordinate is not None and QLyricsDialog.y_coordinate is not None:
      # print('Read as {}, {}'.format(QLyricsDialog.x_coordinate, QLyricsDialog.y_coordinate))
      if utils.IS_MAC:
        self.move(QLyricsDialog.x_coordinate, QLyricsDialog.y_coordinate - 11 * self.devicePixelRatio())
      elif utils.IS_WINDOWS:
        self.move(QLyricsDialog.x_coordinate - 8 * self.devicePixelRatio(), QLyricsDialog.y_coordinate - 31 * self.devicePixelRatio())
    else:
      self.move(parent.size().width() + self.mapToGlobal(parent.parent.pos()).x() + 25 * self.devicePixelRatio(),
                self.mapToGlobal(parent.parent.pos()).y() - 25 * self.devicePixelRatio())

  def moveEvent(self, event):
    QLyricsDialog.x_coordinate = event.pos().x()
    QLyricsDialog.y_coordinate = event.pos().y()
    # print('Set as {}, {}'.format(QLyricsDialog.x_coordinate, QLyricsDialog.y_coordinate))

  def keyPressEvent(self, event):
    key = event.key()
    if event.modifiers() & QtCore.Qt.ShiftModifier and event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_F:
        self.showFullScreen()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_K:
        self.openUrl()
      elif key == QtCore.Qt.Key_R:
        self.grabLyrics()
      elif key == QtCore.Qt.Key_S:
        self.saveLyrics()
      elif key == QtCore.Qt.Key_Backspace:
        self.removeLyrics()
    elif key == QtCore.Qt.Key_Escape:
      self.close()

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

  def grabLyrics(self):
    if self._urlLineEdit.isEnabled(): # This means we should fetch based on URL
      title = self._titleLineEdit.text()
      url = self._urlLineEdit.text()
      print(title, url)
      self.parent.getLyrics(title=title, url=url)
    else:
      artist = self._artistLineEdit.text()
      title = self._titleLineEdit.text()
      source = self._sourceLabelComboBox.currentText()
      self.parent.getLyrics(artist=artist, title=title, source=source)

  def disableUrlEditing(self):
    self._urlLineEdit.setEnabled(False)
    self._fetchAgainButton.setEnabled(True)

  def disableMetadataEditing(self):
    self._artistLineEdit.setEnabled(False)
    self._titleLineEdit.setEnabled(False)
    self._sourceLabelComboBox.setEnabled(False)
    self._fetchAgainButton.setEnabled(True)

  def getFilepath(self):
    return self._filepath

  def closeEvent(self, event):
    self.parent.resetColours()
    event.accept()