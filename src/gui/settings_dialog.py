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

    # Wrapper for settings class
    def set_source():
      self._settings.source = self._sourceComboBox.currentText()

    def set_approximate(state):
      self._settings.approximate = state

    def set_remove_brackets(state):
      self._settings.remove_brackets = state

    def set_info(state):
      self._settings.info = state

    def set_metadata(state):
      self._settings.metadata = state

    def set_text(state):
      self._settings.text = state

    def set_sounds(state):
      self._settings.play_sounds = state

    def set_errors(state):
      self._settings.show_errors = state

    def set_updates(state):
      self._settings.show_updates = state

    # Add settings controls
    self._sourceLabel = QtWidgets.QLabel('Lyrics source:')
    self._sourceLabel.setAlignment(QtCore.Qt.AlignRight)
    self._sourceComboBox = QtWidgets.QComboBox()
    self._sourceComboBox.setMaximumWidth(150)
    for source in utils.SUPPORTED_SOURCES:
      self._sourceComboBox.addItem(source)
    index = self._sourceComboBox.findText(self._settings.source, QtCore.Qt.MatchFixedString)
    self._sourceComboBox.currentIndexChanged.connect(set_source)
    if index >= 0:
      self._sourceComboBox.setCurrentIndex(index)
    self._optionsLabel = QtWidgets.QLabel('Lyrics options:')
    self._optionsLabel.setAlignment(QtCore.Qt.AlignRight)
    self._approximateCheckBox = QtWidgets.QCheckBox('Search only by song title and ignore artist')
    self._approximateCheckBox.setChecked(self._settings.approximate)
    self._approximateCheckBox.stateChanged.connect(lambda state: set_approximate(state))
    self._bracketCheckBox = QtWidgets.QCheckBox('Remove parts of song title and artist in brackets\nwhen searching for lyrics')
    self._bracketCheckBox.setStyleSheet('QCheckBox::indicator { subcontrol-position: left top; }')
    self._bracketCheckBox.stateChanged.connect(lambda state: set_remove_brackets(state))
    self._bracketCheckBox.setChecked(self._settings.remove_brackets)
    self._infoCheckBox = QtWidgets.QCheckBox('Add title and artist to top of saved lyrics')
    self._infoCheckBox.stateChanged.connect(lambda state: set_info(state))
    self._infoCheckBox.setChecked(self._settings.info)
    self._metadataCheckBox = QtWidgets.QCheckBox('Save lyrics to song metadata\n(e.g. for display in music apps on phone)')
    self._metadataCheckBox.setStyleSheet('QCheckBox::indicator { subcontrol-position: left top; }')
    self._metadataCheckBox.stateChanged.connect(lambda state: set_metadata(state))
    self._metadataCheckBox.setChecked(self._settings.metadata)
    self._textCheckBox = QtWidgets.QCheckBox('Save lyrics to a text file')
    self._textCheckBox.stateChanged.connect(lambda state: set_text(state))
    self._textCheckBox.setChecked(self._settings.text)

    # Separator Line
    self._separatorLineFrame = QtWidgets.QFrame()
    self._separatorLineFrame.setFrameShape(QtWidgets.QFrame.HLine)
    self._separatorLineFrame.setFrameShadow(QtWidgets.QFrame.Raised)

    # Other controls
    self._playSoundsLabel = QtWidgets.QLabel('Sounds and dialogs:')
    self._playSoundsCheckBox = QtWidgets.QCheckBox('Enable sound effects')
    self._playSoundsCheckBox.stateChanged.connect(lambda state: set_sounds(state))
    self._playSoundsCheckBox.setChecked(self._settings.play_sounds)
    self._showErrorCheckBox = QtWidgets.QCheckBox('Show error messages')
    self._showErrorCheckBox.stateChanged.connect(lambda state: set_errors(state))
    self._showErrorCheckBox.setChecked(self._settings.show_errors)
    self._showUpdatesCheckBox = QtWidgets.QCheckBox('Show update messages')
    self._showUpdatesCheckBox.stateChanged.connect(lambda state: set_updates(state))
    self._showUpdatesCheckBox.setChecked(self._settings.show_updates)

    # For testing
    # self._approximateCheckBox.setChecked(True)
    # self._tagCheckBox.setChecked(True)

    # Separator leave a bunch of space in case settings expands
    self._verticalSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    # Add settings and about to dialog
    self._settingsGridLayout = QtWidgets.QGridLayout()
    self._settingsGridLayout.addWidget(self._sourceLabel, 0, 0)
    self._settingsGridLayout.addWidget(self._sourceComboBox, 0, 1)
    self._settingsGridLayout.addWidget(self._optionsLabel, 1, 0)
    self._settingsGridLayout.addWidget(self._approximateCheckBox, 1, 1)
    self._settingsGridLayout.addWidget(self._bracketCheckBox, 2, 1)
    self._settingsGridLayout.addWidget(self._infoCheckBox, 3, 1)
    self._settingsGridLayout.addWidget(self._metadataCheckBox, 4, 1)
    self._settingsGridLayout.addWidget(self._textCheckBox, 5, 1)
    self._settingsGridLayout.addWidget(self._separatorLineFrame, 6, 0, 1, -1)
    self._settingsGridLayout.addWidget(self._playSoundsLabel, 7, 0)
    self._settingsGridLayout.addWidget(self._playSoundsCheckBox, 7, 1)
    self._settingsGridLayout.addWidget(self._showErrorCheckBox, 8, 1)
    self._settingsGridLayout.addWidget(self._showUpdatesCheckBox, 9, 1)
    self._settingsGridLayout.addItem(self._verticalSpacer, 10, 0, -1, -1)

    self.setLayout(self._settingsGridLayout)

    # Style settings dialog
    if utils.IS_WINDOWS:
      self.setWindowIcon(QtGui.QIcon(utils.resource_path('./assets/icon.png')))
    if utils.IS_MAC:
      self.setWindowTitle('Preferences')
    else:
      self.setWindowTitle('Settings')
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    self.setFixedSize(self.minimumSizeHint())

    # Center dialog in relation to parent
    self.resize(self.minimumSizeHint())
    self.move(parent.x() + (parent.width() - self.width()) / 2,
      parent.y() + (parent.height() - self.height()) / 2)