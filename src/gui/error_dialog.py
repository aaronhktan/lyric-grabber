from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from modules import utils
from modules import settings

class QErrorDialog (QtWidgets.QDialog):
  def __init__(self, parent, filepaths):
    super().__init__(parent)

    # Create a settings object
    self._settings = settings.Settings()

    self._iconLabel = QtWidgets.QLabel()
    self._iconLabel.setFixedWidth(50)
    self._iconLabel.setFixedHeight(50)
    self._aboutIcon = QtGui.QPixmap(utils.resource_path('./assets/double_bar.png'))
    self._aboutIcon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * self._iconLabel.width()
    self._iconHeight = self.devicePixelRatio() * self._iconLabel.height()
    self._iconLabel.setPixmap(self._aboutIcon.scaled(self._iconWidth, self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    self._errorMessageLabel = QtWidgets.QLabel('Some files couldn\'t be added' if len(filepaths) > 1 else 'A file couldn\'t be added')
    self._errorMessageLabel.setFont(appearance.MEDIUM_FONT)
    self._errorDescriptionLabel = QtWidgets.QLabel(('<center>Try checking that the file format is valid,'
      '<br>and that it hasn\'t already been added.</center>'))
    self._errorDescriptionLabel.setFont(appearance.SMALL_FONT)

    # Spacer as separator
    self._verticalSpacer_1 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    # List of files that couldn't be added
    self._filepathsListView = QtWidgets.QListView()
    self._filepathsListView.setMinimumWidth(400)
    self._filepathsListView.setMaximumHeight(150)
    self._filepathsListView.setAlternatingRowColors(True)
    self._filepathsModel = QtGui.QStandardItemModel(self._filepathsListView)
    [self._filepathsModel.appendRow(QtGui.QStandardItem(filepath)) for filepath in filepaths]
    self._filepathsListView.setModel(self._filepathsModel)
    self._filepathsListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    # Spacer as separator
    self._verticalSpacer_2 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    # Option to suppress further errors
    self._showErrorCheckBox = QtWidgets.QCheckBox('Don\'t show this again')
    self._showErrorCheckBox.stateChanged.connect(lambda state: self._settings.set_show_errors(0) if state else self._settings.set_show_errors(1))
    self._showErrorCheckBox.setChecked(False)

    # Buttons
    self._okButton = QtWidgets.QPushButton('OK')
    self._okButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._okButton.clicked.connect(lambda: self.close())

    self._errorGridLayout = QtWidgets.QGridLayout()
    self._errorGridLayout.addWidget(self._iconLabel, 1, 0, 2, 1, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addWidget(self._errorMessageLabel, 1, 1, 1, 3, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addWidget(self._errorDescriptionLabel, 2, 1, 1, 3, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addItem(self._verticalSpacer_1, 3, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addWidget(self._filepathsListView, 4, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addItem(self._verticalSpacer_2, 5, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addWidget(self._showErrorCheckBox, 6, 0, 1, -1, QtCore.Qt.AlignCenter)
    self._errorGridLayout.addWidget(self._okButton, 7, 0, 1, -1, QtCore.Qt.AlignCenter)

    self.setLayout(self._errorGridLayout)

    # Style error dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setWindowTitle('Just so you know...')
    self.setFixedSize(self.minimumSizeHint())
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)