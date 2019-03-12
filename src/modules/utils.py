import os, sys
import platform

VERSION_NUMBER = '0.19.0311'
CHANNEL = 'alpha'
UPDATE_URL = 'https://api.github.com/repos/aaronhktan/lyric-grabber/releases'
UPDATE_REGEX = r'(.*)\s.?(\d*.{1,})\-(.*)'

IS_MAC = platform.uname().system.startswith('Darw')
IS_WINDOWS = platform.uname().system.startswith('Windows')
IS_LINUX = platform.uname().system.startswith('Linux')

if IS_MAC:
  IS_MACOS_DARK_MODE = (os.system('defaults read -g AppleInterfaceStyle') == 0)
else:
  IS_MACOS_DARK_MODE = False

SUPPORTED_FILETYPES = ('.mp3', '.mp4', '.m4a', '.m4v', \
                       '.tta', '.ape', '.wma', '.aiff', \
                       '.flac', '.ogg', '.oga', '.opus')

SUPPORTED_SOURCES = ('AZLyrics', 'Genius', 'LyricsFreak', \
                     'LyricWiki', 'Metrolyrics', 'Musixmatch')

if hasattr(sys, '_MEIPASS'):
  if IS_MAC:
    CONFIG_PATH = os.path.realpath(sys.argv[0] + '/../../Resources/settings.ini')
  elif IS_LINUX:
    CONFIG_PATH = '/usr/share/quaver/settings.ini'
  elif IS_WINDOWS:
    CONFIG_PATH = os.path.realpath(os.path.dirname(sys.argv[0]) + '/settings.ini')
else:
    CONFIG_PATH = './modules/settings.ini'

def resource_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return os.path.join(sys._MEIPASS, relative_path)
     return os.path.join(os.path.abspath('.'), relative_path)

# !!! README: Update appropriate values if adding new SUPPORTED_FILETYPE !!!
#
# ***** ONE: REGISTRY KEYS FOR INTEGRATION FOR "OPEN WITH" IN WINDOWS *****
# I'm using Advanced Installer to generate a .msi that sets these,
# but this should be applicable to any other installer file generator
# as well.
#
# Term(s): 
#   - HKCU/HKLM: HKEY_CURRENT_USER/HKEY_LOCAL_MACHINE, respectively
#     - The correct key should be used depending on if program is being
#       installed for only user, or for all users; HKCU and HKLM for 
#       each case
#   - HKCR: HKEY_CLASSES_ROOT
#   - Registry values documented with format: TYPE (Name) Data
#
# 1. For application to be registered (and visible to Windows'
#    "How would you like to open this file?" dialog:
#      _HKCU/HKLM
#      └── _Software
#          └── _Classes
#              └──_Applications
#                 └──_name_of_app.exe
#                    ├── Capabilities
#                    ├── _shell
#                    |   └── _open
#                    |       └──_command
#                    └── SupportedTypes
#      NECESSARY:
#        - Capabilities must have the following values:
#          - REG_SZ (ApplicationDescription) some_kind_of_description
#          - REG_SZ (ApplicationName) some_name
#        - command must have the following value:
#          - REG_SZ (Default) "path_to_executable_with quotes" "%1"
#        - name_of_app.exe must have the following values:
#          - REG_SZ (ApplicationCompany) name_of_company
#          - REG_SZ (FriendlyAppName) name_in_right_click_submenu
#      OPTIONAL:
#        - SupportedTypes documents the filetypes for which the app
#          will be visible to. This should be updated for each new
#          filetype:
#          - REG_SZ (.file_type) [empty data]
#        - name_of_app.exe can have the following values:
#          - REG_SZ (Path) path_to_executable
#          - REG_SZ (Version) version_of_app
#
#
# ***** TWO: CORE FOUNDATION KEYS FOR "OPEN WITH" IN MAC OS *****
#
# Term(s): 
#   - plist: The Info.plist located at the root of the app directory bundle,
#            generated by PyInstaller
#
# 1. For application to be registered:
#     Modify the plist file as in the Info.plist file:
#       - Explanation: https://developer.apple.com/library/content/documentation/General/Reference/InfoPlistKeyReference/Articles/CoreFoundationKeys.html#//apple_ref/doc/uid/TP40009249
#         - CFBundleDocumentTypeExtensions is a key that defines the types of filetypes that an application supports. The value is an <array>
#         - Each entry in the array is a <dict> that can have the following keys:
#           - CFBundleTypeExtensions:
#             - An <array> of <string>s that are filetypes that the app
#               supports
#             - An example is <string>mp3</string>
#           - CFBundleTypeName:
#             - The type of files that were described in 
#               CFBundleTypeExtensions
#             - Key is a <string> value
#           - CFBundleTypeRole:
#             - The role of the program. Here, it's a "viewer",
#               but it can also be an "Editor", "Shell", or "None"
#             - Key is a <string> value
#
# 2. To make it show up in Finder:
#   - Assuming it's in Applications and named name.app, following commands must be run:
#     - /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -f /Applications/name.app/
#     - killall Finder
