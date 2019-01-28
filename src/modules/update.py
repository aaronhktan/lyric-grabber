from collections import namedtuple
import json
import re
import urllib.request

try:
  import requests
except ImportError:
  raise ImportError('Can\'t find requests; please install it via "pip install requests"')

try:
  from PyQt5 import QtCore
except ImportError:
  raise ImportError('Can\'t find PyQt5; please install it via "pip install PyQt5"')

from modules import utils

RELEASE_TUPLE = namedtuple('release', ['version', 'url', 'description'])

class UpdateCheckerThread (QtCore.QThread):

  notifyComplete = QtCore.pyqtSignal(object)

  def __init__(self, parent):
    super().__init__()

  def run(self):
    update_available = self.check_for_updates()
    self.notifyComplete.emit(update_available)

  def check_for_updates(self):
    try:
      proxy = urllib.request.getproxies()
      r = requests.get(utils.UPDATE_URL, timeout=10, proxies=proxy)
      releases = r.json()

      for release in releases:
        # print(release['name'])
        m = re.match(utils.UPDATE_REGEX, release['name'])

        platform, version, channel = m.groups()
        # print('{}\n{}\n{}\n'.format(platform, version, channel))

        if utils.IS_MAC:
          if 'macOS' not in platform:
            continue
        elif utils.IS_WINDOWS:
          if 'Windows' not in platform:
            continue
        elif utils.IS_LINUX:
          if 'Linux' not in platform:
            continue
        else:
          break

        if channel != utils.CHANNEL:
          continue

        fetched_version = re.split('\.', version)
        local_version = re.split('\.', utils.VERSION_NUMBER)

        # print(version)
        # print(fetched_version)
        version_parts = zip(local_version, fetched_version)
        for version_part in version_parts:
          if int(version_part[0]) > int(version_part[1]):
            break;
          if int(version_part[0]) < int(version_part[1]):
            for file in release['assets']:
              if utils.IS_MAC:
                if any(s in file['browser_download_url'] for s in ('.zip', '.dmg')):
                  return RELEASE_TUPLE(version,
                    file['browser_download_url'],
                    # release['html_url'],
                    release['body'])
              elif utils.IS_WINDOWS:
                if any(s in file['browser_download_url'] for s in ('.msi', '.exe')):
                  return RELEASE_TUPLE(version,
                    file['browser_download_url'],
                    # release['html_url'],
                    release['body'])
              elif utils.IS_LINUX:
                if any(s in file['browser_download_url'] for s in ('.deb', '.tar.bz2')):
                  return RELEASE_TUPLE(version,
                    file['browser_download_url'],
                    # release['html_url'],
                    release['body'])
      return False
    except:
      return False