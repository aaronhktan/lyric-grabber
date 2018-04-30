from collections import namedtuple
import json
import re
import urllib.request

try:
  import requests
except ImportError:
  raise ImportError('Can\'t find requests; please install it via "pip install requests"')

from modules import utils

RELEASE_TUPLE = namedtuple('release', ['version', 'url', 'description'])

def check_for_updates():
  proxy = urllib.request.getproxies()
  r = requests.get(utils.UPDATE_URL, timeout=10, proxies=proxy)
  releases = r.json()

  for release in releases:
    m = re.match(utils.UPDATE_REGEX, release['name'])

    platform, version, channel = m.groups()
    # print('{}\n{}\n{}\n'.format(platform, version, channel))

    if utils.IS_MAC:
      if platform != "macOS":
        break;
    elif utils.IS_WINDOWS:
      if platform != "Windows":
        break;
    else:
      break;

    if channel != utils.CHANNEL:
      break;

    fetched_version = re.split('\.', version)
    local_version = re.split('\.', utils.VERSION_NUMBER)

    # print(version)
    # print(fetched_version)
    version_parts = zip(local_version, fetched_version)
    for version_part in version_parts:
      if version_part[0] < version_part[1]:
        return RELEASE_TUPLE(version,
          release['assets'][0]['browser_download_url'],
          release['body'])

  return False