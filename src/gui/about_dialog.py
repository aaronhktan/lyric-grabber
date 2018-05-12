from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from modules import utils
from modules import update

class QAboutDialog (QtWidgets.QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)

    self._parent = parent;

    # Metadata about Quaver
    self._iconLabel = QtWidgets.QLabel()
    self._iconLabel.setFixedWidth(100)
    self._iconLabel.setFixedHeight(100)
    self._aboutIcon = QtGui.QPixmap(utils.resource_path('./assets/icon.png'))
    self._aboutIcon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * self._iconLabel.width()
    self._iconHeight = self.devicePixelRatio() * self._iconLabel.height()
    self._iconLabel.setPixmap(self._aboutIcon.scaled(self._iconWidth, self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    self._nameLabel = QtWidgets.QLabel('Quaver')
    self._nameLabel.setFont(appearance.LARGE_FONT)
    self._sloganLabel = QtWidgets.QLabel('Quickly find your lyrics')
    self._sloganLabel.setFont(appearance.SMALL_FONT)

    # Spacer as separator
    self._verticalSpacer = QtWidgets.QSpacerItem(50, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    # Buttons
    # self._projectLinkButton = QtWidgets.QPushButton('See on Github...')
    self._checkUpdatesButton = QtWidgets.QPushButton('Check for updates')
    self._checkUpdatesButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._checkUpdatesButton.clicked.connect(lambda: self.check_for_updates())

    # Credits
    self._creditsLabel = QtWidgets.QLabel(('<center>Made with love by Aaron Tan'
      '<br>Free under the <a href=https://github.com/cheeseisdisgusting/lyric-grabber/blob/master/LICENSE style="color: black; text-decoration: none">MIT License</a>'
      '<br>Check it out on <a href=https://github.com/cheeseisdisgusting/lyric-grabber>Github</a>!</center>'))
    self._creditsLabel.setOpenExternalLinks(True)
    self._iconsCreditsLabel = QtWidgets.QLabel(('<center>UI icons from <a href=https://feathericons.com style="color: black; text-decoration: none">Feather Icons</a>'
      '<br>Quaver icon based on <a href=https://commons.wikimedia.org/wiki/File:Eighth_rest.svg style="color: black; text-decoration: none">Marmelad</a>'
      '<br>Warning icon from <a href=https://openclipart.org/detail/29833/warning-icon style="color: black; text-decoration: none">matthewgarysmith</a>'
      '<br>Download icon from <a href=https://openclipart.org/detail/218662/download-icon style="color: black; text-decoration: none">qubodup</a>'
      '<br>Sounds contributed by <a href=https://sonniss.com style="color: black; text-decoration: none">Sonniss</a>'
      '<br><br>Built with <a href=https://www.python.org style="color: black; text-decoration: none">Python</a>'
      ' and <a href=https://riverbankcomputing.com/software/pyqt/intro style="color: black; text-decoration: none">PyQt</a></center>'))
    self._iconsCreditsLabel.setOpenExternalLinks(True)
    self._iconsCreditsLabel.setFont(appearance.TINY_FONT)
    self._versionLabel = QtWidgets.QLabel('Build {}-{}'.format(utils.VERSION_NUMBER, utils.CHANNEL))
    self._versionLabel.setFont(appearance.TINY_FONT)

    # self._pal = QtGui.QPalette()
    # self._pal.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
    # self._iconLabel.setAutoFillBackground(True)
    # self._iconLabel.setPalette(self._pal)

    self._aboutGridLayout = QtWidgets.QGridLayout()
    if utils.IS_WINDOWS:
        self._aboutGridLayout.setVerticalSpacing(15)
    self._aboutGridLayout.addWidget(self._iconLabel, 0, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._nameLabel, 1, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._sloganLabel, 2, 0, 1, -1, QtCore.Qt.AlignCenter)
    # self._aboutGridLayout.addWidget(self._projectLinkButton, 3, 0, 1, 1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._checkUpdatesButton, 3, 0, 1, 1, QtCore.Qt.AlignCenter)
    # self._aboutGridLayout.addItem(self._verticalSpacer, 4, 0, 2, 1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._creditsLabel, 4, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._iconsCreditsLabel, 5, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._aboutGridLayout.addWidget(self._versionLabel, 9, 0, 1, -1, QtCore.Qt.AlignCenter)

    self.setLayout(self._aboutGridLayout)

    # Style about dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setWindowTitle('About Quaver')
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    if not utils.IS_WINDOWS:
        self.setFixedSize(self.minimumSizeHint())
    else:
        self.setFixedSize(200, self.minimumSizeHint().height())
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

  def check_for_updates(self):
    self._updater_thread = update.UpdateCheckerThread(self)
    self._updater_thread.notifyComplete.connect(self.openUpdateDialog)
    self._updater_thread.start()

  def openUpdateDialog(self, update_available):
    self._parent.openUpdateDialog(update_available,
      show_if_no_update=True,
      show_option_to_hide=False)