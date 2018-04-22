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
    self._iconLabel.setFixedWidth(75)
    self._iconLabel.setFixedHeight(75)
    self._aboutIcon = QtGui.QPixmap(utils.resource_path('./assets/warning.png'))
    self._aboutIcon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * self._iconLabel.width() - 10
    self._iconHeight = self.devicePixelRatio() * self._iconLabel.height() - 10
    self._iconLabel.setPixmap(self._aboutIcon.scaled(self._iconWidth,
        self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    self._errorMessageLabel = QtWidgets.QLabel('Some files couldn\'t be added'
        if len(filepaths) > 1 else 'A file couldn\'t be added.')
    self._errorMessageLabel.setFont(appearance.SMALL_FONT_BOLD)
    self._errorDescriptionLabel = QtWidgets.QLabel((
      '<br>Try checking that the file format is valid,'
      ' and that it hasn\'t already been added.'
      '<br><br>Check "Don\'t show this again" if you do not want to see these error messages.'
      ' You can re-enable these messages under Settings.'))
    self._errorDescriptionLabel.setMinimumWidth(300)
    self._errorDescriptionLabel.setMinimumHeight(self._errorDescriptionLabel.minimumSizeHint().height())
    self._errorDescriptionLabel.setWordWrap(True)
    self._errorDescriptionLabel.setFont(appearance.SMALLER_FONT)

    # Spacer as separator
    self._verticalSpacer_1 = QtWidgets.QSpacerItem(50, 20,
                                                   QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Minimum)

    # List of files that couldn't be added
    self._filepathsListView = QtWidgets.QListView()
    self._filepathsListView.setMinimumWidth(300)
    self._filepathsListView.setMinimumHeight(200)
    self._filepathsListView.setAlternatingRowColors(True)
    self._filepathsModel = QtGui.QStandardItemModel(self._filepathsListView)
    [self._filepathsModel.appendRow(QtGui.QStandardItem(filepath)) for filepath in filepaths]
    self._filepathsListView.setModel(self._filepathsModel)
    self._filepathsListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self._filepathsListView.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    # Spacer as separator
    self._verticalSpacer_2 = QtWidgets.QSpacerItem(50, 20,
                                                   QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Minimum)

    # Option to suppress further errors
    self._showErrorCheckBox = QtWidgets.QCheckBox('Don\'t show this again')
    self._showErrorCheckBox.stateChanged.connect(lambda state: self._settings.set_show_errors(0)
        if state else self._settings.set_show_errors(1))
    self._showErrorCheckBox.setChecked(False)

    # Buttons
    self._showMoreButton = QtWidgets.QPushButton('Show Details')
    self._showMoreButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._showMoreButton.setMaximumWidth(125)
    self._showMoreButton.clicked.connect(lambda: self.showDetails())
    self._okButton = QtWidgets.QPushButton('OK')
    self._okButton.setFocusPolicy(QtCore.Qt.NoFocus)
    self._okButton.setMaximumWidth(125)
    self._okButton.clicked.connect(lambda: self.close())

    self._errorGridLayout = QtWidgets.QGridLayout()
    # self._errorGridLayout.setSpacing(0)
    self._errorGridLayout.addWidget(self._iconLabel, 1, 0, 2, 1)
    self._errorGridLayout.addWidget(self._errorMessageLabel, 1, 1, 1, -1)
    self._errorGridLayout.addWidget(self._errorDescriptionLabel, 2, 1, 1, -1)
    self._errorGridLayout.addItem(self._verticalSpacer_1, 3, 1, 1, -1)
    self._errorGridLayout.addWidget(self._showErrorCheckBox, 6, 1, 1, 1)
    self._errorGridLayout.addWidget(self._showMoreButton, 6, 2, 1, 1)
    self._errorGridLayout.addWidget(self._okButton, 6, 3, 1, 1)

    self.setLayout(self._errorGridLayout)

    # Style error dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setFixedSize(self.sizeHint())
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

  def showDetails(self):
    self._errorGridLayout.addWidget(self._filepathsListView, 4, 1, 1, -1)
    self._filepathsListView.show()
    self._errorGridLayout.addItem(self._verticalSpacer_2, 5, 1, 1, -1)
    self._showMoreButton.setText('Hide Details')
    self._showMoreButton.clicked.connect(lambda: self.hideDetails())
    self.setFixedSize(600, 400)

  def hideDetails(self):
    self._errorGridLayout.removeWidget(self._filepathsListView)
    self._filepathsListView.hide()
    self._errorGridLayout.removeItem(self._verticalSpacer_2)
    self._showMoreButton.setText('Show Details')
    self._showMoreButton.clicked.connect(lambda: self.showDetails())
    self.setFixedSize(self.sizeHint())