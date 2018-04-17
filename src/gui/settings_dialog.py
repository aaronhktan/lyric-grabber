from PyQt5 import QtCore, QtGui, QtWidgets

from modules import settings
from modules import utils

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
    for source in utils.SUPPORTED_SOURCES:
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

    # Separator Line
    self._separatorLineFrame = QtWidgets.QFrame()
    self._separatorLineFrame.setFrameShape(QtWidgets.QFrame.HLine)
    self._separatorLineFrame.setFrameShadow(QtWidgets.QFrame.Raised)

    # Other controls
    self._playSoundsCheckBox = QtWidgets.QCheckBox('Enable sound effects')
    self._playSoundsCheckBox.stateChanged.connect(lambda state: self._settings.set_play_sounds(1) if state else self._settings.set_play_sounds(0))
    self._playSoundsCheckBox.setChecked(self._settings.get_play_sounds())
    self._showErrorCheckBox = QtWidgets.QCheckBox('Show error messages')
    self._showErrorCheckBox.stateChanged.connect(lambda state: self._settings.set_show_errors(1) if state else self._settings.set_show_errors(0))
    self._showErrorCheckBox.setChecked(self._settings.get_show_errors())

    # For testing
    # self._approximateCheckBox.setChecked(True)
    # self._tagCheckBox.setChecked(True)

    # Separator leave a bunch of space in case settings expands
    self._verticalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    # Add settings and about to dialog
    self._settingsGridLayout = QtWidgets.QGridLayout()
    self._settingsGridLayout.addWidget(self._sourceLabel, 0, 0)
    self._settingsGridLayout.addWidget(self._sourceComboBox, 0, 1)
    self._settingsGridLayout.addWidget(self._approximateCheckBox, 1, 1)
    self._settingsGridLayout.addWidget(self._bracketCheckBox, 2, 1)
    self._settingsGridLayout.addWidget(self._infoCheckBox, 3, 1)
    self._settingsGridLayout.addWidget(self._metadataCheckBox, 4, 1)
    self._settingsGridLayout.addWidget(self._textCheckBox, 5, 1)
    self._settingsGridLayout.addWidget(self._separatorLineFrame, 6, 0, 1, -1)
    self._settingsGridLayout.addWidget(self._playSoundsCheckBox, 7, 1)
    self._settingsGridLayout.addWidget(self._showErrorCheckBox, 8, 1)
    self._settingsGridLayout.addItem(self._verticalSpacer, 9, 0, -1, -1)

    self.setLayout(self._settingsGridLayout)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    # Style settings dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    self.setWindowTitle('Settings')
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setFixedSize(self.minimumSizeHint())