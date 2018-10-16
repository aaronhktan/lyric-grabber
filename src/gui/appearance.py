from PyQt5 import QtCore, QtGui, QtWidgets

from modules import utils

if utils.IS_MACOS_DARK_MODE:
  HIGHLIGHT_COLOUR = QtGui.QColor(14, 92, 205)
  ALTERNATE_COLOUR_ONE = QtGui.QColor(41, 45, 47)
  ALTERNATE_COLOUR_TWO = QtGui.QColor(30, 35, 37)
else:
  HIGHLIGHT_COLOUR = QtGui.QColor(186, 221, 244)
  ALTERNATE_COLOUR_ONE = QtGui.QColor(245, 245, 245)
  ALTERNATE_COLOUR_TWO = QtGui.QColor(255, 255, 255)

if utils.IS_MAC:
  LARGE_FONT = QtGui.QFont('.SF NS Text', 24)
  MEDIUM_FONT = QtGui.QFont('.SF NS Text', 18)
  SMALL_FONT = QtGui.QFont('.SF NS Text', 13)
  SMALL_FONT_BOLD = QtGui.QFont('.SF NS Text', 13, QtGui.QFont.Bold)
  SMALLER_FONT = QtGui.QFont('.SF NS Text', 12)
  TINY_FONT = QtGui.QFont('.SF NS Text', 10)
elif utils.IS_WINDOWS:
  LARGE_FONT = QtGui.QFont('Sans Serif', 16)
  MEDIUM_FONT = QtGui.QFont('Sans Serif', 12)
  SMALL_FONT = QtGui.QFont('Sans Serif', 9)
  SMALL_FONT_BOLD = QtGui.QFont('Sans Serif', 9, QtGui.QFont.Bold)
  SMALLER_FONT = QtGui.QFont('Sans Serif', 8)
  TINY_FONT = QtGui.QFont('Sans Serif', 7)
else:
  LARGE_FONT = QtGui.QFont('Sans Serif', 16)
  MEDIUM_FONT = QtGui.QFont('Sans Serif', 14)
  SMALL_FONT = QtGui.QFont('Sans Serif', 10)
  SMALL_FONT_BOLD = QtGui.QFont('Sans Serif', 10, QtGui.QFont.Bold)
  SMALLER_FONT = QtGui.QFont('Sans Serif', 9)
  TINY_FONT = QtGui.QFont('Sans Serif', 8)