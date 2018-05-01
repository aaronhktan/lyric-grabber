from PyQt5 import QtCore, QtGui, QtWidgets

from modules import utils

HIGHLIGHT_COLOUR = QtGui.QColor(186, 221, 244)
ALTERNATE_COLOUR_ONE = QtGui.QColor(245, 245, 245)

if utils.IS_MAC:
  LARGE_FONT = QtGui.QFont('.SF NS Text', 24)
  MEDIUM_FONT = QtGui.QFont('.SF NS Text', 18)
  SMALL_FONT = QtGui.QFont('.SF NS Text', 13)
  SMALL_FONT_BOLD = QtGui.QFont('.SF NS Text', 13, QtGui.QFont.Bold)
  SMALLER_FONT = QtGui.QFont('.SF NS Text', 12)
  TINY_FONT = QtGui.QFont('.SF NS Text', 10)
elif utils.IS_WINDOWS:
  LARGE_FONT = QtGui.QFont('MS Shell Dlg 2', 16)
  MEDIUM_FONT = QtGui.QFont('MS Shell Dlg 2', 14)
  SMALL_FONT = QtGui.QFont('MS Shell Dlg 2', 9)
  SMALL_FONT_BOLD = QtGui.QFont('MS Shell Dlg 2', 9, QtGui.QFont.Bold)
  SMALLER_FONT = QtGui.QFont('MS Shell Dlg 2', 8)
  TINY_FONT = QtGui.QFont('MS Shell Dlg 2', 7)