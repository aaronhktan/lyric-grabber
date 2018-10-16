from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from modules import utils
from modules import settings

class ModalDialog (QtWidgets.QDialog):

  """A modal dialog with some virtual functions that blocks user input.
  By default, has icon, message, informative text, suppression checkbox,
  affirmative/negative repsonse button, and show more button.

  Can be inherited from to customize and add more elements or remove elements.
  If used as base class, inheritor must implement virtual functions,
  corresponding to slots for the signals emitted by buttons/checkboxes.

  Attributes:
      settings (Settings): A settings object
      _iconLabel (QtWidgets.QLabel): Label used to display icon on left
      _titleLabel (QtWidgets.QLabel): Label used to display HIG message
      _messageLabel (QtWidgets.QLabel): Label used to display HIG informative text
      _showAgainCheckBox (QtWidgets.QCheckBox): Checkbox used has HIG suppression checkbox
      _noButton (QtWidget.QPushButton): Button used as negative response button
      _okButton (QtWidget.QPushButton): Button used as positive response button
      _showMoreButton (QtWidget.QPushButton): Button used to expand an HIG accessory view
  """
  
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
    self._showAgainCheckBox = QtWidgets.QCheckBox('Do not show this message again')
    self._showAgainCheckBox.stateChanged.connect(lambda state: self.showAgainAction(state))
    self._showAgainCheckBox.setChecked(False)

    # Buttons
    self._noButton = QtWidgets.QPushButton('Cancel')
    self._noButton.setMaximumWidth(125)
    self._noButton.clicked.connect(self.noAction)
    self._showMoreButton = QtWidgets.QPushButton('Show Details')
    self._showMoreButton.setMaximumWidth(125)
    self._showMoreButton.clicked.connect(self.showDetails)
    self._okButton = QtWidgets.QPushButton('OK')
    self._okButton.setDefault(True)
    self._okButton.setMaximumWidth(125)
    self._okButton.clicked.connect(self.okAction)

    self._dialogGridLayout = QtWidgets.QGridLayout()
    # self._dialogGridLayout.setSpacing(0)
    self._dialogGridLayout.addWidget(self._iconLabel, 1, 0, 2, 1)
    self._dialogGridLayout.setAlignment(self._iconLabel, QtCore.Qt.AlignTop)
    self._dialogGridLayout.addWidget(self._titleLabel, 1, 1, 1, -1)
    self._dialogGridLayout.addWidget(self._messageLabel, 2, 1, 1, -1)
    self._dialogGridLayout.addWidget(self._showAgainCheckBox, 6, 1, 1, 1)
    self._dialogGridLayout.addWidget(self._showMoreButton, 7, 1, 1, 1)
    self._dialogGridLayout.addWidget(self._noButton, 7, 2, 1, 1)
    self._dialogGridLayout.addWidget(self._okButton, 7, 3, 1, 1)

    self.setLayout(self._dialogGridLayout)

    # Style error dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    if not utils.IS_MAC:
      self.setWindowTitle('Quaver')
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    flags = self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint
    flags &= ~(QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowFullscreenButtonHint)
    self.setWindowFlags(flags)

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

  def showAgainAction(self, state):
    raise NotImplementedError('Must implement this in your child class!')

  def noAction(self):
    raise NotImplementedError('Must implement this in your child class!')

  def showDetails(self):
    raise NotImplementedError('Must implement this in your child class!')

  def hideDetails(self):
    raise NotImplementedError('Must implement this in your child class!')

  def okAction(self):
    raise NotImplementedError('Must implement this in your child class!')