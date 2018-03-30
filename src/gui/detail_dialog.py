from PyQt5 import QtCore, QtGui, QtWidgets
from modules.settings import Settings

SUPPORTED_SOURCES = (
  'AZLyrics', 'Genius', 'LyricsFreak', \
  'LyricWiki', 'Metrolyrics', 'Musixmatch'
)

class QLyricsDialog (QtWidgets.QDialog):
  def __init__(self, artist, title, lyrics, filepath, parent=None):
    super().__init__(parent)

    # Style lyrics dialog
    # self.setFixedSize(QtCore.QSize(300, 700))
    self.setModal(False)
    self.setWindowTitle('{artist} - {title}'.format(artist=artist, title=title))

    self._settings = Settings()

    # Add filepath
    self._filepath = filepath

    # Add lyrics label and scroll area
    self._lyricsQLabel = QtWidgets.QLabel()
    self._lyricsQLabel.setText(lyrics)
    self._lyricsQLabel.setStyleSheet('background-color:white;');
    self._lyricsQLabel.setAlignment(QtCore.Qt.AlignTop)
    self._lyricsQLabel.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
    self._lyricsQLabel.setContentsMargins(10, 10, 0, 10)

    self._lyricsScrollArea = QtWidgets.QScrollArea()
    self._lyricsScrollArea.setWidget(self._lyricsQLabel)
    self._lyricsScrollArea.setWidgetResizable(True)
    self._lyricsScrollArea.setMinimumHeight(400)
    self._lyricsScrollArea.setStyleSheet('background:none;');

    # Add buttons at bottom of screen
    self._lyricsCopyButton = QtWidgets.QPushButton('Copy lyrics')
    self._lyricsCopyButton.clicked.connect(lambda: self.copyLyrics())
    self._lyricsSaveButton = QtWidgets.QPushButton('Save lyrics')
    self._lyricsHorizontalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._lyricsClearButton = QtWidgets.QPushButton('Remove lyrics')

    self._lyricsButtonContainerHBoxLayout = QtWidgets.QHBoxLayout()
    self._lyricsButtonContainerHBoxLayout.addWidget(self._lyricsCopyButton)
    self._lyricsButtonContainerHBoxLayout.addWidget(self._lyricsSaveButton)
    self._lyricsButtonContainerHBoxLayout.addItem(self._lyricsHorizontalSpacer)
    self._lyricsButtonContainerHBoxLayout.addWidget(self._lyricsClearButton)

    self._lyricsButtonContainer = QtWidgets.QWidget()
    self._lyricsButtonContainer.setLayout(self._lyricsButtonContainerHBoxLayout)

    # Layout containing both scroll area and buttons
    self._lyricsVBoxLayout = QtWidgets.QVBoxLayout()
    self._lyricsVBoxLayout.addWidget(self._lyricsScrollArea)
    self._lyricsVBoxLayout.addWidget(self._lyricsButtonContainer)
    self._lyricsVBoxLayout.setContentsMargins(10, 10, 10, 10)
    self._lyricsVBoxLayout.setSpacing(5)

    self._lyricsWidget = QtWidgets.QWidget()
    self._lyricsWidget.setLayout(self._lyricsVBoxLayout)

    # Add metadata editing tab
    # Lyrics URL sections
    self._urlLabel = QtWidgets.QLabel('Lyrics URL:')
    self._urlLineEdit = QtWidgets.QLineEdit()

    self._urlLineEdit.setText('https://google.caa;oisdjfaoisjdfiopajwoipefjopiawjopiefjaoiwjepofaisdlhfaisdifhaisdhiofhapsodfais')
    self._urlLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
    self._urlLineEdit.setCursorPosition(0)

    self._viewUrlButton = QtWidgets.QPushButton('View online')
    self._viewUrlButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._viewUrlButton.setMaximumWidth(100)
    self._copyUrlButton = QtWidgets.QPushButton('Copy URL')
    self._copyUrlButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._copyUrlButton.setMaximumWidth(100)

    self._urlWidgetLayout = QtWidgets.QGridLayout()
    self._urlWidgetLayout.addWidget(self._urlLabel, 0, 0, 1, -1)
    self._urlWidgetLayout.addWidget(self._urlLineEdit, 1, 0, 1, -1)
    self._urlWidgetLayout.addWidget(self._viewUrlButton, 2, 1)
    self._urlWidgetLayout.addWidget(self._copyUrlButton, 2, 2)

    self._urlWidget = QtWidgets.QWidget()
    self._urlWidget.setLayout(self._urlWidgetLayout)
    # For testing purposes
    # self._urlWidget.setStyleSheet('''
    #     background: rgb(255, 0, 0);
    # ''')

    # Actual metadata
    self._titleLabel = QtWidgets.QLabel('Title:')
    self._titleLineEdit = QtWidgets.QLineEdit()
    self._titleLineEdit.setText(title);
    self._titleLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)

    self._titleWidgetLayout = QtWidgets.QVBoxLayout()
    self._titleWidgetLayout.addWidget(self._titleLabel)
    self._titleWidgetLayout.addWidget(self._titleLineEdit)

    self._titleWidget = QtWidgets.QWidget()
    self._titleWidget.setLayout(self._titleWidgetLayout)

    self._artistLabel = QtWidgets.QLabel('Artist:')
    self._artistLineEdit = QtWidgets.QLineEdit()
    self._artistLineEdit.setText(artist);
    self._artistLineEdit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)

    self._artistWidgetLayout = QtWidgets.QVBoxLayout()
    self._artistWidgetLayout.addWidget(self._artistLabel)
    self._artistWidgetLayout.addWidget(self._artistLineEdit)

    self._artistWidget = QtWidgets.QWidget()
    self._artistWidget.setLayout(self._artistWidgetLayout)

    # Source
    self._sourceLabel = QtWidgets.QLabel('Source:')
    self._sourceLabelComboBox = QtWidgets.QComboBox()
    self._sourceLabelComboBox.setMaximumWidth(150)
    for source in SUPPORTED_SOURCES:
      self._sourceLabelComboBox.addItem(source)
    index = self._sourceLabelComboBox.findText(self._settings.get_source(), QtCore.Qt.MatchFixedString)
    if index >= 0:
      self._sourceLabelComboBox.setCurrentIndex(index)
    self._sourceWidgetLayout = QtWidgets.QHBoxLayout()
    self._sourceWidgetLayout.addWidget(self._sourceLabel)
    self._sourceWidgetLayout.addWidget(self._sourceLabelComboBox)

    self._sourceWidget = QtWidgets.QWidget()
    self._sourceWidget.setLayout(self._sourceWidgetLayout)

    # Spacer
    self._verticalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    # Try again button
    self._fetchAgainSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    self._fetchAgainButton = QtWidgets.QPushButton('Grab lyrics again')
    self._fetchAgainButton.setAutoDefault(True)

    self._fetchAgainWidgetLayout = QtWidgets.QHBoxLayout()
    self._fetchAgainWidgetLayout.addItem(self._fetchAgainSpacer)
    self._fetchAgainWidgetLayout.addWidget(self._fetchAgainButton)

    self._fetchAgainWidget = QtWidgets.QWidget()
    self._fetchAgainWidget.setLayout(self._fetchAgainWidgetLayout)

    # Add to layout
    self._metadataLayout = QtWidgets.QVBoxLayout()
    self._metadataLayout.addWidget(self._urlWidget)
    self._metadataLayout.addWidget(self._titleWidget)
    self._metadataLayout.addWidget(self._artistWidget)
    self._metadataLayout.addWidget(self._sourceWidget)
    self._metadataLayout.addItem(self._verticalSpacer)
    self._metadataLayout.addWidget(self._fetchAgainWidget)
    self._metadataLayout.setSpacing(0)
    self._metadataLayout.setContentsMargins(10, 10, 10, 10)

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

  def updateLyrics(self, lyrics):
    self._lyricsQLabel.setText(lyrics)

  def copyLyrics(self):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.clear(mode=clipboard.Clipboard )
    clipboard.setText(self._lyricsQLabel.text(), mode=QtGui.QClipboard.Clipboard)

  def getFilePath(self):
    return self._filepath