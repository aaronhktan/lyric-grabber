from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from gui import modal_dialog
from modules import utils

class QUpdateDialog (modal_dialog.QModalDialog):
  def __init__(self, parent, version, url, description):
    super().__init__(parent)

    self.setIcon('./assets/update.png')
    self.setTitle('Version {} of Quaver is available!'.format(version))
    self.setMessage((
      'Click "OK" to download the new version of Quaver.'
      '<br><br>Check "Don\'t show this again" if you do not want to see these update messages.'
      ' You can re-enable these messages under Settings.'))

    # Release notes
    self._descriptionQTextEdit = QtWidgets.QTextEdit()
    self._descriptionQTextEdit.setText(description)
    self._descriptionQTextEdit.setAlignment(QtCore.Qt.AlignTop)
    self._descriptionQTextEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
    self._descriptionQTextEdit.setContentsMargins(10, 10, 0, 10)

    # Download update
    self._update_url = url

  def showDetails(self):
    self._dialogGridLayout.addWidget(self._descriptionQTextEdit, 4, 1, 1, -1)
    self._descriptionQTextEdit.show()
    self._showMoreButton.setText('Hide Details')
    self._showMoreButton.clicked.connect(lambda: self.hideDetails())

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(QtCore.QSize(600, 400))
    animation.start();

  def hideDetails(self):
    self._dialogGridLayout.removeWidget(self._descriptionQTextEdit)
    self._descriptionQTextEdit.hide()
    self._showMoreButton.setText('Show Details')
    self._showMoreButton.clicked.connect(lambda: self.showDetails())

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(self.sizeHint())
    animation.start();

  def showAgainAction(self, state):
    if state:
      modal_dialog.QModalDialog.settings.set_show_updates(0)
    else:
      modal_dialog.QModalDialog.settings.set_show_updates(1)

  def okAction(self):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._update_url))
    self.close()