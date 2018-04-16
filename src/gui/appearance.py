from PyQt5 import QtCore, QtGui, QtWidgets

from modules import utils

HIGHLIGHT_COLOUR = QtGui.QColor(186, 221, 244)
ALTERNATE_COLOUR_ONE = QtGui.QColor(245, 245, 245)

if utils.IS_MAC:
  LARGE_FONT = QtGui.QFont('.SF NS Text', 24)
  MEDIUM_FONT = QtGui.QFont('.SF NS Text', 18)
  SMALL_FONT = QtGui.QFont('.SF NS Text', 13)
  TINY_FONT = QtGui.QFont('.SF NS Text', 10)
elif utils.IS_WINDOWS:
  LARGE_FONT = QtGui.QFont('MS Shell Dlg 2', 24)
  MEDIUM_FONT = QtGui.QFont('MS Shell Dlg 2', 18)
  SMALL_FONT = QtGui.QFont('MS Shell Dlg 2', 13)
  TINY_FONT = QtGui.QFont('MS Shell Dlg 2', 10)