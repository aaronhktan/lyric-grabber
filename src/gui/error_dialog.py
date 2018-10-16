from PyQt5 import QtCore, QtGui, QtWidgets

from gui import appearance
from gui import modal_dialog

class ErrorDialog (modal_dialog.ModalDialog):
  def __init__(self, parent, filepaths):
    """Summary

    Args:
        parent (MainWindow): The main window of the application
        filepaths (string): Array of filepaths that could not be added

    Attributes:
        _filepathsListView (QtWidgets.QListView): Accessory view list view that displays all filepaths that could not be added
    """
    super().__init__(parent)

    self.setIcon('./assets/warning.png')
    self.setTitle('Some files couldn\'t be added'
        if len(filepaths) > 1 else 'A file couldn\'t be added.')
    self.setMessage((
      'Try checking that the file format is valid,'
      ' and that it hasn\'t already been added.'
      '<br><br>Check "Don\'t show this again" if you do not want to see these error messages.'
      ' You can re-enable these messages in settings.'))

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

    # Appearance adjustments for error dialog:
    # Do not show a negative response button; OK button should dismiss alert
    self._noButton.setVisible(False)
    self._dialogGridLayout.addWidget(self._showMoreButton, 7, 2, 1, 1)
    self._dialogGridLayout.addWidget(self._okButton, 7, 3, 1, 1)

    # Center dialog in relation to parent
    self.resize(self.sizeHint())
    self.move(parent.x() + (parent.width() - self.width()) / 2,
      parent.y() + (parent.height() - self.height()) / 2)

  def showAgainAction(self, state):
    if state:
      modal_dialog.ModalDialog.settings.show_errors = 0
    else:
      modal_dialog.ModalDialog.settings.show_errors = 1

  def showDetails(self):
    self._dialogGridLayout.addWidget(self._filepathsListView, 4, 1, 1, -1)
    self._filepathsListView.show()
    self._showMoreButton.setText('Hide Details')
    self._showMoreButton.clicked.connect(self.hideDetails)

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(QtCore.QSize(600, 400))
    animation.start();

  def hideDetails(self):
    self._dialogGridLayout.removeWidget(self._filepathsListView)
    self._filepathsListView.hide()
    self._showMoreButton.setText('Show Details')
    self._showMoreButton.clicked.connect(self.showDetails)

    animation = QtCore.QPropertyAnimation(self, b'size', self)
    animation.setDuration(150)
    animation.setEndValue(self.sizeHint())
    animation.start();

  def okAction(self):
    self.close()