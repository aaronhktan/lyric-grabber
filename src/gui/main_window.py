import os
import threading

try:
  from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from gui import about_dialog
from gui import appearance
from gui import error_dialog
from gui import settings_dialog
from gui import update_dialog
from gui.widget_item import QWidgetItem
from modules import settings
from modules import utils
from threads.lyric_grabber_thread import LyricGrabberThread

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class states:
  NOT_STARTED = 0
  ERROR = 1
  IN_PROGRESS = 2
  COMPLETE = 3

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
    if utils.IS_MAC:
      self._openFinderAction = QtWidgets.QAction('Open Selected File in Finder', self)
      self._openFinderAction.triggered.connect(lambda: self.openFinder())
      self._openFinderAction.setEnabled(False)

    self._removeAllAction = QtWidgets.QAction('Remove All Files')
    self._removeAllAction.setShortcut('Ctrl+Shift+Backspace')
    self._removeAllAction.triggered.connect(lambda: self.removeAllFilesFromList())
    self._removeCompletedAction = QtWidgets.QAction('Remove All Files with Lyrics')
    self._removeCompletedAction.setShortcut('Ctrl+Alt+Shift+Backspace')
    self._removeCompletedAction.triggered.connect(lambda: self.removeCompletedFiles())
    self._removeCurrentAction = QtWidgets.QAction('Remove Selected File')
    self._removeCurrentAction.setShortcut('Ctrl+Backspace')
    self._removeCurrentAction.triggered.connect(lambda: self.removeCurrentFile())
    self._removeCurrentAction.setEnabled(False)

    if utils.IS_MAC:
      self._copyLyricsAction = QtWidgets.QAction('Copy Lyrics')
      self._copyLyricsAction.setShortcut('Ctrl+C')
      self._copyLyricsAction.triggered.connect(lambda: self.copyLyrics())
      self._copyLyricsAction.setEnabled(False)
      self._saveLyricsAction = QtWidgets.QAction('Save Lyrics')
      self._saveLyricsAction.setShortcut('Ctrl+S')
      self._saveLyricsAction.triggered.connect(lambda: self.saveLyrics())
      self._saveLyricsAction.setEnabled(False)
      self._removeLyricsAction = QtWidgets.QAction('Remove Lyrics')
      self._removeLyricsAction.setShortcut('Ctrl+Shift+X')
      self._removeLyricsAction.triggered.connect(lambda: self.removeLyrics())
      self._removeLyricsAction.setEnabled(False)
      self._undoAction = QtWidgets.QAction('Undo Typing')
      self._undoAction.setShortcut('Ctrl+Z')
      self._undoAction.triggered.connect(lambda: self.undoLyrics())
      self._undoAction.setEnabled(False)
      self._redoAction = QtWidgets.QAction('Redo Typing')
      self._redoAction.setShortcut('Ctrl+Shift+Z')
      self._redoAction.triggered.connect(lambda: self.redoLyrics())
      self._redoAction.setEnabled(False)

      self._viewSongsSubMenuAction = QtWidgets.QAction('View Lyrics For...', self)
      self._noLyricsAction = QtWidgets.QAction('No songs added', self)
      self._noLyricsAction.setEnabled(False)
      self._viewPreviousAction = QtWidgets.QAction('View Previous', self)
      self._viewPreviousAction.setShortcut('Ctrl+Up')
      self._viewPreviousAction.triggered.connect(lambda: self.viewPreviousWidget())
      self._viewPreviousAction.setEnabled(False)
      self._viewNextAction = QtWidgets.QAction('View Next', self)
      self._viewNextAction.setShortcut('Ctrl+Down')
      self._viewNextAction.triggered.connect(lambda: self.viewNextWidget())
      self._viewNextAction.setEnabled(False)
      self._toolBarAction = QtWidgets.QAction('Hide Toolbar', self)
      self._toolBarAction.setShortcut('Ctrl+Alt+T')
      self._toolBarAction.triggered.connect(lambda: self.toggleToolBar())

      self._minimizeAction = QtWidgets.QAction('Minimize', self)
      self._minimizeAction.setShortcut('Ctrl+M')
      self._minimizeAction.triggered.connect(lambda: self.toggleMinimized())
      self._maximizeAction = QtWidgets.QAction('Zoom', self)
      self._maximizeAction.triggered.connect(lambda: self.toggleMaximized())
      self._showNormalAction = QtWidgets.QAction('Bring to Front', self)
      self._showNormalAction.triggered.connect(lambda: self.showNormal())

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

    # Only create toolbar on Mac
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
      self._toolBarVisible = True
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
    if event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.AltModifier and event.modifiers() & QtCore.Qt.ShiftModifier:
      if key == QtCore.Qt.Key_Backspace:
        self.removeCompletedFiles()
    elif event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.ShiftModifier:
      if key == QtCore.Qt.Key_O:
        # Super + shift + O should open folder browser
        self.openFileDialog(QtWidgets.QFileDialog.Directory)
      elif key == QtCore.Qt.Key_Backspace:
        self.removeAllFilesFromList()
    elif event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.MetaModifier:
      if key == QtCore.Qt.Key_F:
        self.toggleFullScreen()
    elif event.modifiers() & QtCore.Qt.ControlModifier:
      if key == QtCore.Qt.Key_O:
        # Super + O should open file browser
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

  def focusInEvent(self, event):
    self._viewPreviousAction.setEnabled(True)
    self._viewNextAction.setEnabled(True)

  def focusOutEvent(self, event):
    self._viewPreviousAction.setEnabled(False)
    self._viewNextAction.setEnabled(False)

  def setSelectedWidget(self, filepath, index=-1):
    if filepath == None:
      MainWindow.selectedWidgetIndex = None
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
      for i in range(self._mainScrollAreaWidgetLayout.count()):
        if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath() == filepath:
          MainWindow.selectedWidgetIndex = i
          break

    self._removeCurrentAction.setEnabled(True)
    if utils.IS_MAC:
      self._openFinderAction.setEnabled(True)
      self._copyLyricsAction.setEnabled(True)
      self._saveLyricsAction.setEnabled(True)
      self._removeLyricsAction.setEnabled(True)
      self._undoAction.setEnabled(True)
      self._redoAction.setEnabled(True)
      if MainWindow.selectedWidgetIndex > 0:
        self._viewPreviousAction.setEnabled(True)
      else:
        self._viewPreviousAction.setEnabled(False)
      if self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex + 1) is not None:
        self._viewNextAction.setEnabled(True)
      else:
        self._viewNextAction.setEnabled(False)

  def viewPreviousWidget(self):
    if MainWindow.selectedWidgetIndex is not None:
      newIndex = MainWindow.selectedWidgetIndex - 1
      if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
        MainWindow.selectedWidgetIndex -= 1
        self.resetListColours()
        self.setSelectedWidget('', MainWindow.selectedWidgetIndex)
        self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget())
        self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget().openDetailDialog()

  def viewNextWidget(self):
    if MainWindow.selectedWidgetIndex is not None:
        newIndex = MainWindow.selectedWidgetIndex + 1
        if self._mainScrollAreaWidgetLayout.itemAt(newIndex) is not None:
          MainWindow.selectedWidgetIndex += 1
          self.resetListColours()
          self.setSelectedWidget('', MainWindow.selectedWidgetIndex)
          self._mainScrollArea.ensureWidgetVisible(self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget())
          self._mainScrollAreaWidgetLayout.itemAt(MainWindow.selectedWidgetIndex).widget().openDetailDialog()

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

    # Show an error message for each invalid filepath found
    if invalid_filepaths and self._settings.get_show_errors():
      self.showError(invalid_filepaths)

    if len(filepaths) > 0:
      self.startFetchThread(filepaths)

  def showError(self, filepaths):
    self.setEnabled(False)
    try:
      if not hasattr(self, '_error_dialog'):
        self._error_dialog = error_dialog.QErrorDialog(self, filepaths)
        self.playErrorSound()
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

      # Refresh menu items
      if MainWindow.selectedWidgetIndex is not None:
        i = MainWindow.selectedWidgetIndex
        if i > 0 and self._viewPreviousAction.isEnabled() == False:
          self._viewPreviousAction.setEnabled(True)
        if self._mainScrollAreaWidgetLayout.itemAt(i + 1) is not None and self._viewNextAction.isEnabled() == False:
          self._viewNextAction.setEnabled(True)

      if utils.IS_MAC and self._mainScrollAreaWidgetLayout.count() < 10:
        if self._noLyricsAction.isVisible():
          self._noLyricsAction.setVisible(False)
        self._viewSongsSubMenuAction.setEnabled(True)
        openItemAction = QtWidgets.QAction(title + ' - ' + artist, self)
        openItemAction.triggered.connect(lambda: listWidgetItem.openDetailDialog())
        self._songsSubMenu.addAction(openItemAction)

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

  def removeCurrentFile(self):
    i = MainWindow.selectedWidgetIndex
    if self._mainScrollAreaWidgetLayout.itemAt(i).widget().getState() == states.COMPLETE:
      self._all_filepaths.remove(self._mainScrollAreaWidgetLayout.itemAt(i).widget().getFilepath())
      self._mainScrollAreaWidgetLayout.itemAt(i).widget().removeFromList()
    MainWindow.selectedWidgetIndex = None

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