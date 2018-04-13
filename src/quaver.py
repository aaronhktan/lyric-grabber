from gui import main_window

import sys
from PyQt5 import QtCore, QtWidgets

def main():
  QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
  app = QtWidgets.QApplication(sys.argv)

  window = main_window.MainWindow()
  window.show()
  window.setWindowTitle('Quaver')

  sys.exit(app.exec_())

if __name__ == '__main__':
  main()