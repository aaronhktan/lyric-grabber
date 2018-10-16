from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from gui import modal_dialog
from modules import utils

class UpdateDialog (modal_dialog.ModalDialog):
  def __init__(self, parent, title, message, url, description, show_option_to_hide=True):
    """This is the dialog that notifies the user of a software update.
    
    Args:
        parent (MainWindow): The main window of the application
        title (string): The string that should be shown in the title bar
        message (string): The body text of the dialog (in HIG terms, 'Informative Text')
        url (string): The URL that leads to an update. Set to None if no update available.
        description (string): Description of update, displayed in the QTextEdit.
          Set to None if no update.
        show_option_to_hide (bool, optional): Control display of suppression checkbox.
          Set to False when user causes update check.

    Attributes:
        _descriptionQTextEdit (QtWidgets.QTextEdit): Accessory view text box displaying release notes
    """
    super().__init__(parent)

    self.setIcon('./assets/update.png')
    self.setTitle(title)
    self.setMessage(message)

    # Show release notes in text area if applicable
    # Otherwise, hide the button that allows showing release notes
    if description is not None:
      self._descriptionQTextEdit = QtWidgets.QTextEdit()
      self._descriptionQTextEdit.setText(description)
      self._descriptionQTextEdit.setAlignment(QtCore.Qt.AlignTop)
      self._descriptionQTextEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
      self._descriptionQTextEdit.setContentsMargins(10, 10, 0, 10)
    else:
      self._showMoreButton.setVisible(False)

    # Check whether to allow user to suppress dialogs
    if not show_option_to_hide:
      self._showAgainCheckBox.setVisible(False)

    # Set the download URL if available
    # If available, then also change text on affirmative and negative response buttons
    self._update_url = url
    if url is not None:
      self.setWindowTitle('Software Update')
      self._okButton.setText('Download')
      self._noButton.setText('Not now')
    else:
      self._okButton.setText('OK')
      self._noButton.setVisible(False)

    # Center dialog in relation to parent
    self.resize(self.sizeHint())
    self.move(parent.x() + (parent.width() - self.width()) / 2,
      parent.y() + (parent.height() - self.height()) / 2)

  def showAgainAction(self, state):
    if state:
      modal_dialog.ModalDialog.settings.show_updates = 0
    else:
      modal_dialog.ModalDialog.settings.show_updates = 1

  def noAction(self):
    self.close()

  def showDetails(self):
    self._dialogGridLayout.addWidget(self._descriptionQTextEdit, 4, 1, 1, -1)
    self._descriptionQTextEdit.show()
    self._showMoreButton.setText('Hide Details')
    self._showMoreButton.clicked.connect(self.hideDetails)

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(QtCore.QSize(600, 400))
    animation.start();

  def hideDetails(self):
    self._dialogGridLayout.removeWidget(self._descriptionQTextEdit)
    self._descriptionQTextEdit.hide()
    self._showMoreButton.setText('Show Details')
    self._showMoreButton.clicked.connect(self.showDetails)

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(self.sizeHint())
    animation.start();

  def okAction(self):
    if self._update_url is not None:
      QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._update_url))
    self.close()