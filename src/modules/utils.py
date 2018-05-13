import os, sys
import platform

VERSION_NUMBER = '0.5.513'
CHANNEL = 'alpha'
UPDATE_URL = 'https://api.github.com/repos/cheeseisdisgusting/lyric-grabber/releases'
UPDATE_REGEX = r'(.*)\s.?(\d*.{1,})\-(.*)'

IS_MAC = platform.uname().system.startswith('Darw')
IS_WINDOWS = platform.uname().system.startswith('Windows')
IS_LINUX = platform.uname().system.startswith('Linux')

SUPPORTED_FILETYPES = ('.mp3', '.mp4', '.m4a', '.m4v', \
                       '.tta', '.ape', '.wma', '.aiff', \
                       '.flac', '.ogg', '.oga', '.opus')

SUPPORTED_SOURCES = ('AZLyrics', 'Genius', 'LyricsFreak', \
                     'LyricWiki', 'Metrolyrics', 'Musixmatch')

def resource_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return os.path.join(sys._MEIPASS, relative_path)
     return os.path.join(os.path.abspath('.'), relative_path)