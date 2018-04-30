from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from modules import utils
from modules import settings

class QModalDialog (QtWidgets.QDialog):
  settings = settings.Settings()

  def __init__(self, parent):
    super().__init__(parent)

    self._iconLabel = QtWidgets.QLabel()
    self._iconLabel.setFixedWidth(75)
    self._iconLabel.setFixedHeight(75)
    self._titleLabel = QtWidgets.QLabel()
    self._titleLabel.setFont(appearance.SMALL_FONT_BOLD)
    self._messageLabel = QtWidgets.QLabel()
    self._messageLabel.setMinimumWidth(300)
    self._messageLabel.setMinimumHeight(self._messageLabel.minimumSizeHint().height())
    self._messageLabel.setWordWrap(True)
    self._messageLabel.setFont(appearance.SMALLER_FONT)

    # Option to suppress further errors
    self._showAgainCheckBox = QtWidgets.QCheckBox('Don\'t show this again')
    self._showAgainCheckBox.stateChanged.connect(lambda state: self.showAgainAction(state))
    self._showAgainCheckBox.setChecked(False)

    # Buttons
    self._showMoreButton = QtWidgets.QPushButton('Show Details')
    self._showMoreButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._showMoreButton.setMaximumWidth(125)
    self._showMoreButton.clicked.connect(lambda: self.showDetails())
    self._okButton = QtWidgets.QPushButton('OK')
    self._okButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._okButton.setMaximumWidth(125)
    self._okButton.clicked.connect(lambda: self.okAction())

    self._dialogGridLayout = QtWidgets.QGridLayout()
    # self._dialogGridLayout.setSpacing(0)
    self._dialogGridLayout.addWidget(self._iconLabel, 1, 0, 2, 1)
    self._dialogGridLayout.setAlignment(self._iconLabel, QtCore.Qt.AlignTop)
    self._dialogGridLayout.addWidget(self._titleLabel, 1, 1, 1, -1)
    self._dialogGridLayout.addWidget(self._messageLabel, 2, 1, 1, -1)
    self._dialogGridLayout.addWidget(self._showAgainCheckBox, 6, 1, 1, 1)
    self._dialogGridLayout.addWidget(self._showMoreButton, 6, 2, 1, 1)
    self._dialogGridLayout.addWidget(self._okButton, 6, 3, 1, 1)

    self.setLayout(self._dialogGridLayout)

    # Style error dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

  def setIcon(self, url):
    icon = QtGui.QPixmap(utils.resource_path(url))
    icon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * self._iconLabel.width() - 10
    self._iconHeight = self.devicePixelRatio() * self._iconLabel.height() - 10
    self._iconLabel.setPixmap(icon.scaled(self._iconWidth,
        self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

  def setTitle(self, title):
    self._titleLabel.setText(title)

  def setMessage(self, message):
    self._messageLabel.setText(message)

  def showDetails(self):
    raise NotImplementedError('Must implement this in your child class!')

  def hideDetails(self):
    raise NotImplementedError('Must implement this in your child class!')

  def showAgainAction(self, state):
    raise NotImplementedError('Must implement this in your child class!')

  def okAction(self):
    raise NotImplementedError('Must implement this in your child class!')