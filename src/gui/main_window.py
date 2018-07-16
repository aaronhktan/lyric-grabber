import os
import threading
from urllib.parse import unquote

try:
  from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from gui import about_dialog
from gui import appearance
from gui import error_dialog
from gui import settings_dialog
from gui import update_dialog
from gui.widget_item import SongWidget
from modules import settings
from modules import utils
from threads.lyric_grabber_thread import LyricGrabberThread
from threads.states import states

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class MainWindow (QtWidgets.QMainWindow):

  """The main window of the application
  
  Attributes:
      selectedWidgetIndex (int): Keeps track of which song's detail pane has been opened
      widgetAddingLock (threading.Lock): Lock for song widget adding to scrolling list view
  """
  
  selectedWidgetIndex = None
  widgetAddingLock = threading.Lock()

  def __init__(self):
    super(MainWindow, self).__init__()

    # Create a settings object
    self._settings = settings.Settings()

    # Create and add items to menubar
    # Actions are ordered by their location in the macOS menubar
    # macOS menubar is significantly larger by OS convention
    # See https://developer.apple.com/design/human-interface-guidelines/macos/menus/menu-bar-menus/
    self._openAboutAction = QtWidgets.QAction('About Quaver')
    self._openAboutAction.triggered.connect(self.openAboutDialog)
    if utils.IS_MAC:
      self._openSettingsAction = QtWidgets.QAction('Preferences')
    else:
      self._openSettingsAction = QtWidgets.QAction('Settings')
    self._openSettingsAction.setShortcut('Ctrl+Comma')
    self._openSettingsAction.triggered.connect(self.openSettingsDialog)

    self._openFileAction = QtWidgets.QAction('Open File...', self)
    self._openFileAction.setShortcut('Ctrl+O')
    self._openFileAction.triggered.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles))
    self._openFolderAction = QtWidgets.QAction('Open Folder...', self)
    self._openFolderAction.setShortcut('Ctrl+Shift+O')
    self._openFolderAction.triggered.connect(lambda: self.openFileDialog(QtWidgets.QFileDialog.Directory))
    self._closeAction = QtWidgets.QAction('Close')
    self._closeAction.setShortcut('Ctrl+W')
    self._closeAction.triggered.connect(self.close)
    if utils.IS_MAC:
      self._openFinderAction = QtWidgets.QAction('Open Selected File in Finder', self)
      self._openFinderAction.triggered.connect(self.openFinder)
      self._openFinderAction.setEnabled(False)

    self._removeAllAction = QtWidgets.QAction('Remove All Files')
    self._removeAllAction.setShortcut('Ctrl+Shift+Backspace')
    self._removeAllAction.triggered.connect(self.removeAllFilesFromList)
    self._removeCompletedAction = QtWidgets.QAction('Remove All Files with Lyrics')
    self._removeCompletedAction.setShortcut('Ctrl+Alt+Shift+Backspace')
    self._removeCompletedAction.triggered.connect(self.removeCompletedFiles)
    self._removeCurrentAction = QtWidgets.QAction('Remove Selected File')
    self._removeCurrentAction.setShortcut('Ctrl+Backspace')
    self._removeCurrentAction.triggered.connect(self.removeCurrentFile)
    self._removeCurrentAction.setEnabled(False)

    if utils.IS_MAC:
      self._copyLyricsAction = QtWidgets.QAction('Copy Lyrics')
      self._copyLyricsAction.setShortcut('Ctrl+C')
      self._copyLyricsAction.triggered.connect(self.copyLyrics)
      self._copyLyricsAction.setEnabled(False)
      self._saveLyricsAction = QtWidgets.QAction('Save Lyrics')
      self._saveLyricsAction.setShortcut('Ctrl+S')
      self._saveLyricsAction.triggered.connect(self.saveLyrics)
      self._saveLyricsAction.setEnabled(False)
      self._removeLyricsAction = QtWidgets.QAction('Remove Lyrics')
      self._removeLyricsAction.setShortcut('Ctrl+Shift+X')
      self._removeLyricsAction.triggered.connect(self.removeLyrics)
      self._removeLyricsAction.setEnabled(False)
      self._undoAction = QtWidgets.QAction('Undo Typing')
      self._undoAction.setShortcut('Ctrl+Z')
      self._undoAction.triggered.connect(self.undoLyrics)
      self._undoAction.setEnabled(False)
      self._redoAction = QtWidgets.QAction('Redo Typing')
      self._redoAction.setShortcut('Ctrl+Shift+Z')
      self._redoAction.triggered.connect(self.redoLyrics)
      self._redoAction.setEnabled(False)

      self._viewSongsSubMenuAction = QtWidgets.QAction('View Lyrics For...', self)
      self._noLyricsAction = QtWidgets.QAction('No songs added', self)
      self._noLyricsAction.setEnabled(False)
      self._viewPreviousAction = QtWidgets.QAction('View Previous', self)
      self._viewPreviousAction.setShortcut('Ctrl+Up')
      self._viewPreviousAction.triggered.connect(self.viewPreviousWidget)
      self._viewPreviousAction.setEnabled(False)
      self._viewNextAction = QtWidgets.QAction('View Next', self)
      self._viewNextAction.setShortcut('Ctrl+Down')
      self._viewNextAction.triggered.connect(self.viewNextWidget)
      self._viewNextAction.setEnabled(False)
      self._toolBarAction = QtWidgets.QAction('Hide Toolbar', self)
      self._toolBarAction.setShortcut('Ctrl+Alt+T')
      self._toolBarAction.triggered.connect(self.toggleToolBar)

      self._minimizeAction = QtWidgets.QAction('Minimize', self)
      self._minimizeAction.setShortcut('Ctrl+M')
      self._minimizeAction.triggered.connect(self.toggleMinimized)
      self._maximizeAction = QtWidgets.QAction('Zoom', self)
      self._maximizeAction.triggered.connect(self.toggleMaximized)
      self._showNormalAction = QtWidgets.QAction('Bring to Front', self)
      self._showNormalAction.triggered.connect(self.showNormal)

    self._helpAction = QtWidgets.QAction('Help', self)
    self._helpAction.triggered.connect(self.openAboutDialog)

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
    if utils.IS_MAC:
      self._fileMenu.addSeparator()
      self._fileMenu.addAction(self._openFinderAction)
    self._fileMenu.addSeparator()
    self._fileMenu.addAction(self._closeAction)

    self._editMenu = self._menuBar.addMenu('Edit')
    self._editMenu.addAction(self._removeCurrentAction)
    self._editMenu.addSeparator()
    self._editMenu.addAction(self._removeAllAction)
    self._editMenu.addAction(self._removeCompletedAction)

    if utils.IS_MAC:
      self._editMenu.addSeparator()
      self._editMenu.addAction(self._copyLyricsAction)
      self._editMenu.addAction(self._saveLyricsAction)
      self._editMenu.addAction(self._removeLyricsAction)
      self._editMenu.addAction(self._undoAction)
      self._editMenu.addAction(self._redoAction)

      self._viewMenu = self._menuBar.addMenu('View')
      self._viewMenu.addAction(self._viewSongsSubMenuAction)
      self._songsSubMenu = QtWidgets.QMenu(self._menuBar)
      self._songsSubMenu.addAction(self._noLyricsAction)
      self._viewSongsSubMenuAction.setMenu(self._songsSubMenu)
      self._viewMenu.addSeparator()
      self._viewMenu.addAction(self._viewPreviousAction)
      self._viewMenu.addAction(self._viewNextAction)
      self._viewMenu.addSeparator()
      self._viewMenu.addAction(self._toolBarAction)

      self._windowMenu = self._menuBar.addMenu('Window')
      self._windowMenu.addAction(self._minimizeAction)
      self._windowMenu.addAction(self._maximizeAction)
      self._windowMenu.addSeparator()
      self._windowMenu.addAction(self._showNormalAction)

    if not utils.IS_MAC:
      self._toolsMenu = self._menuBar.addMenu('Tools')
      self._toolsMenu.addAction(self._openSettingsAction)

    self._helpMenu = self._menuBar.addMenu('Help')
    self._helpMenu.addAction(self._helpAction)
    if not utils.IS_MAC:
      self._helpMenu.addAction(self._openAboutAction)

    # Create toolbar, but only on Mac
    # On other platforms, the menubar essentially takes on the role that the menu bar takes on Mac
    if utils.IS_MAC:
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

      # Add toolbar to window with name 'main'
      self._toolBar = self.addToolBar('main')
      self._toolBar.addWidget(self._toolBarItems)
      self._toolBar.setFloatable(False)
      self._toolBar.setMovable(False)
      self._toolBarVisible = True
      self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    # Create a hint for the user
    # This is the image/text in middle of screen on startup
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

    # This layout contains all the items in the song list
    # Style the layout: spacing (between items), content (padding within items)
    self._mainScrollAreaWidgetLayout = QtWidgets.QVBoxLayout()
    self._mainScrollAreaWidgetLayout.setAlignment(QtCore.Qt.AlignCenter)
    self._mainScrollAreaWidgetLayout.setSpacing(0)
    self._mainScrollAreaWidgetLayout.setContentsMargins(0, 0, 0, 0)

    self._mainScrollAreaWidgetLayout.addWidget(self._instructionIconLabel)
    self._mainScrollAreaWidgetLayout.addItem(self._verticalSpacer)
    self._mainScrollAreaWidgetLayout.addWidget(self._instructionLabel)

    # mainScrollAreaWidget contains the layout that contains all listwidgets
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

  # Functions associated with window management
  def toggleFullScreen(self):
    if self.isFullScreen():
      self.showNormal()
    else:
      self.showFullScreen()

  def toggleToolBar(self):
    if self._toolBarVisible:
      self._toolBarVisible = False
      self._toolBar.hide()
      self._toolBarAction.setText('Show Toolbar')
    else:
      self._toolBarVisible = True
      self._toolBar.show()
      self._toolBarAction.setText('Hide Toolbar')

  def toggleMaximized(self):
    if self.isMaximized():
      self.showNormal()
    else:
      self.showMaximized()

  def toggleMinimized(self):
    if self.isMinimized():
      self.showNormal()
    else:
      self.showMinimized()

  # Functions associated with events
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
        url = unquote(url.toString(QtCore.QUrl.RemoveScheme))
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
    if event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.AltModifier and event.modifiers() & QtCore.Qt.ShiftModifier:
      if key == QtCore.Qt.Key_Backspace:
        self.removeCompletedFiles()
    elif event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.ShiftModifier:
      if key == QtCore.Qt.Key_O:
        self.openFileDialog(QtWidgets.QFileDialog.Directory)
      elif key == QtCore.Qt.Key_Backspace:
        self.removeAllFilesFromList()
    elif event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.MetaModifier:
      if key == QtCore.Qt.Key_F:
        self.toggleFullScreen()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_O:
        self.openFileDialog(QtWidgets.QFileDialog.ExistingFiles)
      elif key == QtCore.Qt.Key_W:
        self.close()
      elif key == QtCore.Qt.Key_Backspace:
        self.removeCurrentFile()
      elif key == QtCore.Qt.Key_Comma:
        self.openSettingsDialog()
    else:
      if key == QtCore.Qt.Key_S or key == QtCore.Qt.Key_Down:
        self.viewNextWidget()
      elif key == QtCore.Qt.Key_W or key == QtCore.Qt.Key_Up:
        self.viewPreviousWidget()

  def setSelectedWidget(self, filepath, index=-1):
    """ 
    The selected widget is used to determine:
      - Whether to enable some menu options
      - Which file's lyrics to display in the menu pane
    
    Args:
        filepath (string): Used to find song widget based on filepath
        index (string, optional): If this is set, this function will use that index

    """
    if filepath == None:
      # Un-set any selected widget
      self.selectedWidgetIndex = None
      self._removeCurrentAction.setEnabled(False)
      if utils.IS_MAC:
        self._openFinderAction.setEnabled(False)
        self._copyLyricsAction.setEnabled(False)
        self._saveLyricsAction.setEnabled(False)
        self._removeLyricsAction.setEnabled(False)
        self._undoAction.setEnabled(False)
        self._redoAction.setEnabled(False)
        self._viewPreviousAction.setEnabled(False)
        self._viewNextAction.setEnabled(False)
      return

    if index < 0:
      # Must find the widget
      for i in range(self._mainScrollAreaWidgetLayout.count()):
        if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath() == filepath:
          self.selectedWidgetIndex = i
          break

    # Apply changes to menu based on selected widget index
    self._removeCurrentAction.setEnabled(True)
    if utils.IS_MAC:
      self._openFinderAction.setEnabled(True)
      self._copyLyricsAction.setEnabled(True)
      self._saveLyricsAction.setEnabled(True)
      self._removeLyricsAction.setEnabled(True)
      self._undoAction.setEnabled(True)
      self._redoAction.setEnabled(True)
      if self.selectedWidgetIndex > 0:
        self._viewPreviousAction.setEnabled(True)
      else:
        self._viewPreviousAction.setEnabled(False)
      if self._mainScrollAreaWidgetLayout.itemAt(self.selectedWidgetIndex + 1) is not None:
        self._viewNextAction.setEnabled(True)
      else:
        self._viewNextAction.setEnabled(False)

  # Functions associated with a selected song widget
  def viewPreviousWidget(self):
    if self.selectedWidgetIndex is not None:
      newIndex = self.selectedWidgetIndex - 1
      if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
        self.selectedWidgetIndex -= 1
        self.resetListColours()
        self.setSelectedWidget('', self.selectedWidgetIndex)
        self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(self.selectedWidgetIndex).widget())
        self._mainScrollAreaWidgetLayout.itemAt(self.selectedWidgetIndex).widget().openDetailDialog()

  def viewNextWidget(self):
    if self.selectedWidgetIndex is not None:
        newIndex = self.selectedWidgetIndex + 1
        if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
          self.selectedWidgetIndex += 1
          self.resetListColours()
          self.setSelectedWidget('', self.selectedWidgetIndex)
          self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(self.selectedWidgetIndex).widget())
          self._mainScrollAreaWidgetLayout.itemAt(self.selectedWidgetIndex).widget().openDetailDialog()

  def openFinder(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().openFilepath()

  def copyLyrics(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().dialog.copyLyrics()

  def saveLyrics(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().dialog.saveLyrics()

  def removeLyrics(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().dialog.removeLyrics()

  def undoLyrics(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().dialog.undoEvent()

  def redoLyrics(self):
    i = self.selectedWidgetIndex
    self._mainScrollAreaWidgetLayout.itemAt(i).widget().dialog.redoEvent()

  # Functions associated with the file picker and adding new songs
  def openFileDialog(self, fileMode):
    """Opens file picker dialog in user-selected mode
    
    Args:
        fileMode (QtWidgets.QFileDialog): Either Directory or ExistingFiles,
          depending on which button/menu option the user selected
    """
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
    """Takes in a list of strings that are filepaths,
      then generates a list of files after verification.
    
    Args:
        files ([strings]): A list of unverified filepaths
    """
    if not hasattr(self, '_all_filepaths'):
      self._all_filepaths = []
    filepaths = []
    invalid_filepaths = []

    for file in files:
      if file.endswith(utils.SUPPORTED_FILETYPES):
        if file in self._all_filepaths:
          # Do not allow same file to be added twice
          invalid_filepaths.append(file)
        else:
          self._all_filepaths.append(file)
          filepaths.append(file)
      else:
        invalid_filepaths.append(file)

    # Show an error message for each invalid filepath found
    if invalid_filepaths and self._settings.get_show_errors():
      self.showError(invalid_filepaths)

    if len(filepaths) > 0:
      self.startFetchThread(filepaths)

  def showError(self, filepaths):
    """Shows an error dialog iff error dialog is not currently visible
    
    Args:
        filepaths ([string]): List of filepaths that could not be added
    """
    if hasattr(self, '_error_dialog'):
      try:
        if self._error_dialog.isVisible():
          return
      except:
        pass

    self._error_dialog = error_dialog.ErrorDialog(self, filepaths)
    self.playErrorSound()
    self._error_dialog.show()

  def startFetchThread(self, filepaths):
    """Start another thread for network requests to not block the GUI thread
    
    Args:
        filepaths ([string]): List of filepaths to read metadata and find lyrics for
    """
    self._fetch_thread = LyricGrabberThread(self, filepaths)

    self._fetch_thread.addFileToList.connect(self.addFileToList)
    self._fetch_thread.notifyComplete.connect(self.playSuccessSound)
    self._fetch_thread.notifyNoMetadata.connect(self.showError)
    self._fetch_thread.setLyrics.connect(self.setLyrics)
    self._fetch_thread.setProgressIcon.connect(self.setProgressIcon)

    self._fetch_thread.start()

  def addFileToList(self, artist, title, art, filepath):
    """Create and add a song widget given data
    
    Args:
        artist (string): Song artist
        title (string): Song title
        art (bytes literal): Embedded album art metadata as bytes literal
        filepath (string): Path to song without scheme
    """
    with MainWindow.widgetAddingLock:
      # Only allow adding one song at a time
      if not self._removedInstructions:
        # Remove hint shown at startup
        self._instructionLabel.setParent(None)
        self._instructionIconLabel.setParent(None)
        self._mainScrollAreaWidgetLayout.removeItem(self._verticalSpacer)
        self._mainScrollAreaWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        self._removedInstructions = True

      # Create WidgetItem for each item
      songWidget = SongWidget(self)
      songWidget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
      songWidget.setProgressIcon(states.NOT_STARTED, self.devicePixelRatio())
      songWidget.setAlbumArt(art, self.devicePixelRatio())
      songWidget.setArtistText(artist)
      songWidget.setTitleText(title)
      songWidget.setfilepath(filepath)
      if self._mainScrollAreaWidgetLayout.count() % 2:
        songWidget.setBackgroundColor(appearance.ALTERNATE_COLOUR_ONE)
      else:
        songWidget.setBackgroundColor(QtCore.Qt.white)
      self._mainScrollAreaWidgetLayout.addWidget(songWidget)

      # Refresh menu items to enable/disable 'Navigate to previous/next' entries
      if self.selectedWidgetIndex is not None:
        i = self.selectedWidgetIndex
        if i > 0 and self._viewPreviousAction.isEnabled() == False:
          self._viewPreviousAction.setEnabled(True)
        if self._mainScrollAreaWidgetLayout.itemAt(i + 1) is not None and self._viewNextAction.isEnabled() == False:
          self._viewNextAction.setEnabled(True)

      if utils.IS_MAC and self._mainScrollAreaWidgetLayout.count() < 10:
        if self._noLyricsAction.isVisible():
          self._noLyricsAction.setVisible(False)
        self._viewSongsSubMenuAction.setEnabled(True)
        songWidget.openItemAction = QtWidgets.QAction(title + ' - ' + artist, self)
        songWidget.openItemAction.setData(filepath)
        songWidget.openItemAction.triggered.connect(songWidget.openDetailDialog)
        songWidget.openItemAction.triggered.connect(lambda: self.setSelectedWidget(filepath))
        self._songsSubMenu.addAction(songWidget.openItemAction)

  def setProgressIcon(self, filepath, state):
    """Sets traffic light indicator for state
    
    Args:
        filepath (string): Filepath of the song whose progress must be changed
        state (int): State that determines the progress indicator colour
    """
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilepath() == filepath:
        widgetItem.setProgressIcon(state, self.devicePixelRatio())

  def setLyrics(self, filepath, lyrics, url):
    """Sets lyrics for a particular song
    
    Args:
        filepath (string): Filepath to the song whose lyrics are being set
        lyrics (string): The lyrics themselves
        url (string): The source of the lyrics
    """
    for i in range(self._mainScrollAreaWidgetLayout.count()):
      widgetItem = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      if widgetItem.getFilepath() == filepath:
        widgetItem.setLyrics(lyrics)
        widgetItem.setUrl(url)

  def resetListColours(self):
    """Removes selected colour, resets to default white/grey alternating pattern"""
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
    """Removes all widget items from the list"""
    try:
      SongWidget.dialog.close()
      self._fetch_thread.exit()
    except:
      pass
    finally:
      # Iterate through all widgets, ignoring welcome text
      # Clear list of filepaths that have been added
      # Remove all actions from the "View" submenu
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
      for i in self._songsSubMenu.actions():
        self._songsSubMenu.removeAction(i)
      self._songsSubMenu.addAction(self._noLyricsAction)
      self._noLyricsAction.setVisible(True)

  def removeCompletedFiles(self):
    """Removes only widget items with lyrics"""
    try:
      SongWidget.dialog.close()
    except:
      pass

    # Iterate through all widgets, ignoring welcome text
    # Remove filepath from list of filepaths that have been added
    # Remove action from the "View" submenu if data (i.e. filepath) corresponds
    for i in reversed(range(self._mainScrollAreaWidgetLayout.count())):
      if self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionIconLabel \
      or self._mainScrollAreaWidgetLayout.itemAt(i).widget() is self._instructionLabel \
      or self._mainScrollAreaWidgetLayout.itemAt(i) is self._verticalSpacer:
        pass
      else:
        if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.COMPLETE:
          self._all_filepaths.remove(self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath())
          widget = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
          if utils.IS_MAC:
            for i in self._songsSubMenu.actions():
              if i.data() == widget.getFilepath():
                self._songsSubMenu.removeAction(i)
          widget.deleteLater()
          widget.setParent(None)
          widget = None
    self.resetListColours()

  def removeCurrentFile(self):
    """Remove file currently selected by user"""
    i = self.selectedWidgetIndex
    if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.COMPLETE \
    or self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.ERROR:
      self._all_filepaths.remove(self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath())
      songWidget = self._mainScrollAreaWidgetLayout.itemAt(i).widget()
      songWidget.removeFromList()
      if utils.IS_MAC and i < 10:
        # Replace entry in the "View lyrics for..." submenu with the 10th song
        try:
          self._songsSubMenu.removeAction(songWidget.openItemAction)
        except Exception as e:
          print(e)
        if self._mainScrollAreaWidgetLayout.itemAt(8) is not None:
          nextWidget = self._mainScrollAreaWidgetLayout.itemAt(8).widget()
          nextWidget.openItemAction = QtWidgets.QAction(nextWidget.getTitleText() + ' - ' + nextWidget.getArtistText(), self)
          nextWidget.openItemAction.setData(nextWidget.getFilepath())
          nextWidget.openItemAction.triggered.connect(nextWidget.openDetailDialog)
          nextWidget.openItemAction.triggered.connect(lambda: self.setSelectedWidget(nextWidget.getFilepath()))
          print(nextWidget.openItemAction)
          self._songsSubMenu.addAction(nextWidget.openItemAction)
        if self._songsSubMenu.isEmpty():
          self._noLyricsAction.setVisible(True)
    self.selectedWidgetIndex = None

  def openAboutDialog(self):
    """Opens dialog showing information about program, with ability to check for updates"""
    self.setEnabled(False)
    self._about_dialog = about_dialog.QAboutDialog(self)
    self._about_dialog.exec()
    self.setEnabled(True)

  def openSettingsDialog(self):
    """Opens dialog showing settings"""
    self.setEnabled(False)
    self._settings_dialog = settings_dialog.QSettingsDialog()
    self._settings_dialog.exec()
    self.setEnabled(True)

  def openUpdateDialog(self, update_available, show_if_no_update=False, show_option_to_hide=True):
    """Opens dialog alerting user of an available update
    
    Args:
        update_available (bool): Is an update available?
        show_if_no_update (bool, optional): When true, shows that user is on the newest version.
          Used when user explicitly requests and update check.
        show_option_to_hide (bool, optional): When true, shows option to supress update notifications.
          Is set to false when user explicitly checks for updates.
    """
    show_hide_message = ('Click "Download" to download the new version of Quaver.'
      '<br><br>Check "Don\'t show this again" if you do not want to see these update messages.'
      ' You can re-enable these messages under Settings.')
    do_not_show_hide_message = ('Click "OK" to download the new version of Quaver.'
      '<br><br>Quaver can automatically check for updates if you check the appropriate option in Settings.')

    if update_available:
      self._update_dialog = update_dialog.UpdateDialog(self,
        title='Version {} of Quaver is available!'.format(update_available.version),
        message=show_hide_message if show_option_to_hide else do_not_show_hide_message,
        url=update_available.url,
        description=update_available.description,
        show_option_to_hide=show_option_to_hide)
      self._update_dialog.exec()
    elif show_if_no_update:
      self._update_dialog = update_dialog.UpdateDialog(self,
        title='You are on the newest version of Quaver!',
        message=('Quaver can automatically check for updates if you check the appropriate option in Settings.'),
        url=None,
        description=None,
        show_option_to_hide=show_option_to_hide)
      self._update_dialog.exec()

  def openDialog(self, message):
    """Used for debugging."""
    self._something_dialog = update_dialog.UpdateDialog(self,
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