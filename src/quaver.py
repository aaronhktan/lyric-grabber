import sys

try:
  from PyQt5 import QtCore, QtWidgets
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install pyqt5"')

from gui import main_window
from modules import update

class MainApp (QtWidgets.QApplication):
  def __init__(self, argv):
    super(MainApp, self).__init__(argv)

    self._window = main_window.MainWindow()
    self._window.show()
    self._window.setWindowTitle('Quaver')

    if self._window._settings.get_show_updates():
      self._updater_thread = update.UpdateCheckerThread(self)
      self._updater_thread.notifyComplete.connect(self._window.openUpdateDialog)
      self._updater_thread.start()

    try:
      if utils.IS_WINDOWS:
        filepath = sys.argv[1]
        self._window.generateFilepathList([filepath])
      elif utils.IS_LINUX:
        filepaths = []
        [filepaths.append(file) for file in sys.argv[1:]]
        self._window.generateFilepathList(filepaths)
    except:
      pass

  def event(self, event):
    if event.type() == QtCore.QEvent.FileOpen:
      self._window.generateFilepathList([event.url().toString().replace('file://', '')])
    elif event.type() == 20:
      sys.exit()
    else:
      pass
      # print('Type is {}'.format(str(event.type())))
    return True

def main():
  QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
  QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
  app = MainApp(sys.argv)
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()