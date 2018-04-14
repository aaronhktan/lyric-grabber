from modules import settings
from modules import utils

from PyQt5 import QtCore, QtGui, QtWidgets

# Style note: Functions and variable names are not PEP 8 compliant.
# Blame PyQt for that!
# Keeping consistency with PyQt camelCase is prioritised.

class QSettingsDialog (QtWidgets.QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)

    # Style the window
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))

    # Get settings from settings.ini file
    self._settings = settings.Settings()

    # Add settings controls
    self._sourceLabel = QtWidgets.QLabel('Lyrics Source:')
    self._sourceComboBox = QtWidgets.QComboBox()
    self._sourceComboBox.setMaximumWidth(150)
    for source in settings.SUPPORTED_SOURCES:
      self._sourceComboBox.addItem(source)
    index = self._sourceComboBox.findText(self._settings.get_source(), QtCore.Qt.MatchFixedString)
    self._sourceComboBox.currentIndexChanged.connect(lambda: self._settings.set_source(self._sourceComboBox.currentText()))
    if index >= 0:
      self._sourceComboBox.setCurrentIndex(index)
    self._approximateCheckBox = QtWidgets.QCheckBox('Search only by song title')
    self._approximateCheckBox.setChecked(self._settings.get_approximate())
    self._approximateCheckBox.stateChanged.connect(lambda state: self._settings.set_approximate(1) if state else self._settings.set_approximate(0))
    self._bracketCheckBox = QtWidgets.QCheckBox('Remove parts of song title and artist in brackets')
    self._bracketCheckBox.stateChanged.connect(lambda state: self._settings.set_remove_brackets(1) if state else self._settings.set_remove_brackets(0))
    self._bracketCheckBox.setChecked(self._settings.get_remove_brackets())
    self._infoCheckBox = QtWidgets.QCheckBox('Add title and artist to top of saved file')
    self._infoCheckBox.stateChanged.connect(lambda state: self._settings.set_info(1) if state else self._settings.set_info(0))
    self._infoCheckBox.setChecked(self._settings.get_info())
    self._metadataCheckBox = QtWidgets.QCheckBox('Save lyrics to song metadata')
    self._metadataCheckBox.stateChanged.connect(lambda state: self._settings.set_metadata(1) if state else self._settings.set_metadata(0))
    self._metadataCheckBox.setChecked(self._settings.get_metadata())
    self._textCheckBox = QtWidgets.QCheckBox('Save lyrics to a text file')
    self._textCheckBox.stateChanged.connect(lambda state: self._settings.set_text(1) if state else self._settings.set_text(0))
    self._textCheckBox.setChecked(self._settings.get_text())

    # For testing
    # self._approximateCheckBox.setChecked(True)
    # self._tagCheckBox.setChecked(True)

    # Separator between settings and about
    self._verticalSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    # Add about section
    self._iconLabel = QtWidgets.QLabel()
    self._iconLabel.setFixedWidth(100)
    self._iconLabel.setFixedHeight(100)
    self._aboutIcon = QtGui.QPixmap(utils.resource_path('./assets/icon.png'))
    self._aboutIcon.setDevicePixelRatio(self.devicePixelRatio())
    self._iconWidth = self.devicePixelRatio() * (self._iconLabel.width() - 10)
    self._iconHeight = self.devicePixelRatio() * (self._iconLabel.height() - 10)
    self._iconLabel.setPixmap(self._aboutIcon.scaled(self._iconWidth, self._iconHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    self._nameLabel = QtWidgets.QLabel('Quaver')
    self._largeFont = QtGui.QFont('Gill Sans', 24)
    self._nameLabel.setFont(self._largeFont)
    self._detailLabel = QtWidgets.QLabel('Made with love by Aaron Tan.\nFree under the MIT License.')

    self._nameAndDetailVBoxLayout = QtWidgets.QVBoxLayout()
    self._nameAndDetailVBoxLayout.addWidget(self._nameLabel)
    self._nameAndDetailVBoxLayout.addWidget(self._detailLabel)
    self._nameAndDetailWidget = QtWidgets.QWidget()
    self._nameAndDetailWidget.setLayout(self._nameAndDetailVBoxLayout)

    self._aboutWidgetLayout = QtWidgets.QHBoxLayout()
    self._aboutWidgetLayout.addWidget(self._iconLabel)
    self._aboutWidgetLayout.addWidget(self._nameAndDetailWidget)
    self._aboutGroupBox = QtWidgets.QGroupBox()
    self._aboutGroupBox.setTitle('')
    self._aboutGroupBox.setLayout(self._aboutWidgetLayout)

    # self._pal = QtGui.QPalette()
    # self._pal.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
    # self._aboutWidget.setAutoFillBackground(True)
    # self._aboutWidget.setPalette(self._pal)

    # Add settings and about to dialog
    self._settingsGridLayout = QtWidgets.QGridLayout()
    self._settingsGridLayout.addWidget(self._sourceLabel, 0, 0)
    self._settingsGridLayout.addWidget(self._sourceComboBox, 0, 1)
    self._settingsGridLayout.addWidget(self._approximateCheckBox, 1, 1)
    self._settingsGridLayout.addWidget(self._bracketCheckBox, 2, 1)
    self._settingsGridLayout.addWidget(self._infoCheckBox, 3, 1)
    self._settingsGridLayout.addWidget(self._metadataCheckBox, 4, 1)
    self._settingsGridLayout.addWidget(self._textCheckBox, 5, 1)
    self._settingsGridLayout.addItem(self._verticalSpacer, 6, 0)
    self._settingsGridLayout.addWidget(self._aboutGroupBox, 7, 0, 1, -1)

    self.setLayout(self._settingsGridLayout)

    # Style settings dialog
    self.setWindowTitle('Settings')
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setFixedSize(self.minimumSizeHint())