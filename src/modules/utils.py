import os, sys
import platform

IS_MAC = platform.uname().system.startswith('Darw')
IS_WINDOWS = platform.uname().system.startswith('Windows')

def resource_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return os.path.join(sys._MEIPASS, relative_path)
     return os.path.join(os.path.abspath('.'), relative_path)