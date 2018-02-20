import file_writer

import json
from urllib.parse import urlencode, quote_plus
import urllib.request
import random

try:
  import requests
except ImportError:
  raise ImportError('Can\'t find requests; please install it via "pip install requests"')

try:
  from BeautifulSoup import BeautifulSoup, Comment
except:
  try:
    from bs4 import BeautifulSoup, Comment
  except ImportError:
    raise ImportError('Can\'t find BeautifulSoup; please install it via "pip install BeautifulSoup4"')

try:
  import taglib
except ImportError:
  raise ImportError('Can\'t find pytaglib; please install it via "pip install pytaglib"')

LYRICWIKI_URL_BASE = 'http://lyrics.wikia.com/api.php?'
AZLYRICS_URL_BASE = 'https://search.azlyrics.com/search.php?'

USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
  'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
  'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
  'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
  'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2'
  ]

def AZLyrics_get_lyrics(title):
  proxy = urllib.request.getproxies()
  payload = {'q': title}
  search_url = AZLYRICS_URL_BASE + urlencode(payload, quote_via=quote_plus)
  # print(search_url)

  r = requests.get(search_url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    search_results = document.find_all('td', class_='visitedlyr')
    search_results = search_results[0].find_all('a', href=True)
    # print(search_results[0]['href'])

    url = search_results[0]['href']
  except:
    print('[INFO] No results for song from AZLyrics')
    return False

  headers = requests.utils.default_headers()                                                  # AZLyrics filters against bots by inspecting user-agent
  headers.update({
      'User-Agent': random.choice(USER_AGENTS),
  })

  r = requests.get(url, timeout=10, proxies=proxy, headers=headers)

  r.encoding = 'utf-8'

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', class_='', id='')

    [elem.extract() for elem in lyrics.find_all(text=lambda text:isinstance(text, Comment))]  # Remove all text that is a comment in lyrics
    [elem.extract() for elem in lyrics.find_all('div')]                                       # Remove any sub-divs in lyrics
    [elem.extract() for elem in lyrics.find_all('script')]                                    # Remove any scripts in lyrics
    [elem.extract() for elem in lyrics.find_all('i')]                                         # Remove any italics in lyrics
    [elem.extract() for elem in lyrics.find_all('br')]                                        # Remove <br> tags

    return lyrics.get_text().strip()
  except:
    print('[ERROR] Could not parse lyrics from AZLyrics')
    return False

  return False

def LyricWiki_get_lyrics(artist, title):
  proxy = urllib.request.getproxies()
  payload = {'action':  'lyrics', \
             'artist':  artist, \
             'song':    title, \
             'fmt':     'json', \
             'func':    'getSong'}
  url = LYRICWIKI_URL_BASE + urlencode(payload, quote_via=quote_plus)
  # print(url)

  r = requests.get(url, timeout=10, proxies=proxy)

  try:
    returned = r.text
    returned = returned.replace("\"", "\\\"")                                                     # Make sure that quotes are properly escaped
    returned = returned.replace("\'", "\"")                                                       # LyricWiki returns strings surrounded by single quotes
    returned = returned.replace("song = ", "")                                                    # LyricWiki prepends song = to JSON, screwing with decoders
    returned = json.loads(returned)
    # print(returned["lyrics"])
  except:
    print('[ERROR] Could not parse search results from LyricWiki')

  if returned["lyrics"] != "Not found":
    r = requests.get(returned['url'], timeout=10, proxies=proxy)
    try:
      document = BeautifulSoup(r.text, 'html.parser')
      lyrics = document.find('div', class_='lyricbox')                                          # Find all divs with class lyricbox

      [elem.extract() for elem in lyrics.find_all(text=lambda text:isinstance(text, Comment))]  # Remove all text that is a comment in lyrics
      [elem.extract() for elem in lyrics.find_all('div')]                                       # Remove any sub-divs in lyrics
      [elem.extract() for elem in lyrics.find_all('script')]                                    # Remove any scripts in lyrics
      [elem.replace_with('\n') for elem in lyrics.find_all('br')]                               # Remove <br> tags and reformat them into \n line breaks 

      return lyrics.get_text().strip()
    except:
      print('[ERROR] Could not parse lyrics from LyricWiki')
      return False
  else:
    print('[INFO] No results for song from LyricWiki')
    return False

def Musixmatch_get_lyrics(title):
  proxy = urllib.request.getproxies()
  title = urllib.parse.quote_plus(title)
  search_url = 'https://www.musixmatch.com/search/{title}'.format(title=title)
  # print(search_url)

  headers = requests.utils.default_headers()                                                  # Musixmatch filters against bots by inspecting user-agent
  headers.update({
      'User-Agent': random.choice(USER_AGENTS),
  })

  r = requests.get(search_url, timeout=10, proxies=proxy, headers=headers)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    search_result = document.find('div', class_='box-style-plain')
    search_result = search_result.find_all('a', href=True)
    url = 'https://www.musixmatch.com' + search_result[0]['href']
    # print(url)
  except:
    print('[INFO] No results for song from Musixmatch')
    return False

  headers = requests.utils.default_headers()                                                  # Musixmatch filters against bots by inspecting user-agent
  headers.update({
      'User-Agent': random.choice(USER_AGENTS),
  })

  r = requests.get(url, timeout=10, proxies=proxy, headers=headers)

  try:                                                                                        # Lyrics are located in the scripts section of the site
    start_index = r.text.find('"body":"')                                                     # And are preceded with the string "body":
    end_index = r.text.find('","language"')                                                   # And are succeeded with the string "language"

    lyrics = r.text[start_index+len('"body":"'):end_index]

    lyrics = lyrics.replace('<i>', '')                                                        # Remove any italics in lyrics
    lyrics = lyrics.replace('<br>', '\n')                                                     # Remove <br> tags and reformat them into \n line breaks
    lyrics = lyrics.replace('\\"', '"')                                                       # Replace escaped quotes with just quotes
    lyrics = lyrics.replace('\\n', '\n')                                                      # Replace \n string with \n line breaks

    return lyrics.strip()
  except:
    print('[ERROR] Could not parse lyrics from Musixmatch')
    return False

  return False

# tracks = [
#   {'Artist': 'Boy',                 'Title': 'Little Numbers'},
#   {'Artist': 'Natalia Lafourcade',  'Title': 'Tú sí sabes quererme'},
#   {'Artist': 'Pierre Lapointe',     'Title': 'Au bar des suicidés'},
#   {'Artist': '曲婉婷',               'Title': '我的歌声里'},
#   {'Artist': '方皓玟',               'Title': '你是我本身的傅奇'}
# ]

# for item in tracks:
#   artist = item['Artist']
#   title = item['Title']
#   lyrics = LyricWiki_get_lyrics(artist, title)
  # if lyrics:
  #   write_lyrics_to_txt(title + '_lyricwiki.txt', lyrics)
  # else:
  #   print('[INFO] No lyrics found for file: {file}'.format(file=title))
  # lyrics = AZLyrics_get_lyrics(title)
  # if lyrics:
  #   write_lyrics_to_txt(title + '_azlyrics.txt', lyrics)
  # else:
  #   print('[INFO] No lyrics found for file: {file}'.format(file=title))
  # lyrics = Musixmatch_get_lyrics(title)
  # if lyrics:
  #   write_lyrics_to_txt(title + '_musixmatch.txt', lyrics)
  # else:
  #   print('[INFO] No lyrics found for file: {file}'.format(file=title))

# for file in os.listdir(os.curdir):
#   if os.path.isfile(file) and (file.endswith('.mp3') or \
#     file.endswith('.mpc') or file.endswith('.flac') or \
#     file.endswith('.mp4') or file.endswith('.asf') or \
#     file.endswith('.aiff') or file.endswith('.wav') or \
#     file.endswith('.tta') or file.endswith('.wv') or \
#     file.endswith('.ogg') or file.endswith('.oga') or \
#     file.endswith('.spx') or file.endswith('.opus')) or \
#     file.endswith('.m4a'):

#     filename = os.getcwd() + '/' + file
#     song = taglib.File(filename)

#     try:
#       artist = song.tags['ARTIST'][0]
#       title = song.tags['TITLE'][0]
#       # print(str(title) + ' ' + str(artist))
#     except:
#       print('[ERROR] Metadata reading error for file: {file}'.format(file=file))
#       continue

#     try:
#       # lyrics = LyricWiki_get_lyrics(artist, title)
#       # lyrics = AZLyrics_get_lyrics(title)
#       lyrics = Musixmatch_get_lyrics(title)
#       # print(lyrics)

#       if lyrics:
#         write_lyrics_to_txt(file, lyrics)
#       else:
#         print('[INFO] No lyrics found for file: {file}'.format(file=file))
#     except:
#       print('[ERROR] Something went horribly wrong!')