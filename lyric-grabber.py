import json
import os
from urllib.parse import urlencode, quote_plus
import urllib.request

try:
  import requests
except ImportError:
  raise ImportError("Can\'t find requests; please install it via \"pip install requests\"")

try:
  from BeautifulSoup import BeautifulSoup, Comment
except:
  try:
    from bs4 import BeautifulSoup, Comment
  except ImportError:
    raise ImportError("Can\'t find BeautifulSoup; please install it via \"pip install BeautifulSoup4\"")

try:
  import taglib
except ImportError:
  raise ImportError("Can\'t find pytaglib; please install it via \"pip install pytaglib\"'")

def LyricWiki_GetLyrics(artist, title):
  proxy = urllib.request.getproxies()
  payload = {'action':  'lyrics', \
             'artist':  artist, \
             'song':    title, \
             'fmt':     'json', \
             'func':    'getSong'}
  url = 'http://lyrics.wikia.com/api.php?' + urlencode(payload, quote_via=quote_plus)
  # print(url)

  r = requests.get(url, timeout=10, proxies=proxy)

  returned = r.text
  # print(returned)
  returned = returned.replace("\"", "\\\"") # Make sure that quotes are properly escaped
  returned = returned.replace("\'", "\"") # LyricWiki returns strings surrounded by single quotes
  returned = returned.replace("song = ", "") # LyricWiki prepends song = to JSON, screwing with decoders
  returned = json.loads(returned)
  # print(returned["lyrics"])

  if returned["lyrics"] != "Not found":
    r = requests.get(returned['url'], timeout=10, proxies=proxy)
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', class_='lyricbox') # Find all divs with class lyricbox

    # Format the lyrics
    [elem.extract() for elem in lyrics.find_all(text=lambda text:isinstance(text, Comment))] # Remove all text that is a comment in lyrics
    [elem.extract() for elem in lyrics.find_all('div')] # Remove any sub-divs in lyrics
    [elem.extract() for elem in lyrics.find_all('script')] # Remove any scripts in lyrics
    [elem.replace_with('\n') for elem in lyrics.find_all('br')] # Remove <br> tags and reformat them into \n line breaks 

    # print(lyrics.get_text())

    return lyrics.get_text()

# def MusixMatch_GetLyrics(artist, title):
#   proxy = urllib.request.getproxies()
#   url = 'https://www.musixmatch.com/lyrics/{artist}/{title}'.format()
#   print(url)

# tracks = [
#   {'Artist': 'Boy',                 'Title': 'Little Numbers'},
#   {'Artist': 'Natalia Lafourcade',  'Title': 'Tú sí sabes quererme'},
#   {'Artist': 'Pierre Lapointe',     'Title': 'Au bar des suicidés'},
#   {'Artist': '方皓玟',               'Title': '你是我本身的傅奇'}
# ]

# for item in tracks:
#   artist = item['Artist'].encode('utf-8')
#   title = item['Title'].encode('utf-8')
#   LyricWiki_GetLyrics(artist, title)
#   MusixMatch_GetLyrics(artist, title)

for file in os.listdir(os.curdir):
    if os.path.isfile(file) and (file.endswith('.mp3') or \
      file.endswith('.mpc') or file.endswith('.flac') or \
      file.endswith('.mp4') or file.endswith('.asf') or \
      file.endswith('.aiff') or file.endswith('.wav') or \
      file.endswith('.tta') or file.endswith('.wv') or \
      file.endswith('.ogg') or file.endswith('.oga') or \
      file.endswith('.spx') or file.endswith('.opus')) or \
      file.endswith('.m4a'):
        song = taglib.File(os.getcwd() + '/' + file)
        artist = song.tags['ARTIST'][0]
        title = song.tags['TITLE'][0]

        lyrics = LyricWiki_GetLyrics(artist, title)
        # print(str(title) + ' ' + str(artist))
        # print(lyrics)
        
        lyrics_file = open(file[:file.rfind('.')] + '.txt', 'w+') # Slice off file extension and replace with txt
        lyrics_file.write(lyrics)
        lyrics_file.close()