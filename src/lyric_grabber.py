from keys import genius_key

import json
from urllib.parse import urlencode, quote_plus
import urllib.request
import random

try:
  from BeautifulSoup import BeautifulSoup, Comment
except:
  try:
    from bs4 import BeautifulSoup, Comment
  except ImportError:
    raise ImportError('Can\'t find BeautifulSoup; please install it via "pip install BeautifulSoup4"')

try:
  import requests
except ImportError:
  raise ImportError('Can\'t find requests; please install it via "pip install requests"')

try:
  import unidecode
except ImportError:
  raise ImportError('Can\'t find unidecode; please install it via "pip install unidecode"')

AZLYRICS_URL_BASE = 'https://search.azlyrics.com/search.php?'
GENIUS_URL_BASE = 'https://api.genius.com/search?'
LYRICSFREAK_URL_BASE = 'http://www.lyricsfreak.com'
LYRICWIKI_URL_BASE = 'http://lyrics.wikia.com/api.php?'
METROLYRICS_URL_BASE = 'http://www.metrolyrics.com/'
MUSIXMATCH_URL_BASE = 'https://www.musixmatch.com'

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

def Genius_get_lyrics(title):
  if (genius_key == ''):
    print('[ERROR] No Genius key set? Please check keys.py!')
    return False

  proxy = urllib.request.getproxies()
  payload = {'q': title}
  search_url = GENIUS_URL_BASE + urlencode(payload, quote_via=quote_plus)
  # print(url)

  headers = requests.utils.default_headers()                                                  # Genius requires an authorization token to get JSON search results
  headers.update({                                                                            # Can't scrape results page because uses Angular :(
      'Authorization': 'Bearer ' + genius_key,
  })

  r = requests.get(search_url, timeout=10, proxies=proxy, headers=headers)

  search_results = json.loads(r.text)

  try:
    if search_results['meta']['status'] == 200:
      url = search_results['response']['hits'][0]['result']['url']
    else:
      print('[INFO] Could not reach Genius; check your Internet connection and Genius key')
  except:
    print('[ERROR] Could not parse search results from Genius; check your Genius key')
    return False

  r = requests.get(url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics_div = document.find('div', class_='lyrics')
    
    lyrics_paragraphs = []
    [lyrics_paragraphs.append(elem.get_text()) for elem in lyrics_div.find_all('p')]

    lyrics = ''.join(lyrics_paragraphs)
    
    return lyrics.strip()
  except:
    return False

  return False

def LyricsFreak_get_lyrics(title):
  proxy = urllib.request.getproxies()
  payload = {'a':       'search', \
             'type':    'song', \
             'q':       title}
  search_url = LYRICSFREAK_URL_BASE + '/search.php?' + urlencode(payload, quote_via=quote_plus)
  # print(url)

  r = requests.get(search_url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    search_results = document.find_all('a', class_='song')

    url = LYRICSFREAK_URL_BASE + search_results[0]['href']
    # print(url)
  except:
    print('[ERROR] Could not parse search results from LyricsFreak')
    return False

  r = requests.get(url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', id='content_h')

    [elem.replace_with('\n') for elem in lyrics.find_all('br')]                               # Remove <br> tags and reformat them into \n line breaks 
    return lyrics.get_text()
  except:
    print('[ERROR] Could not parse lyrics from LyricsFreak')
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
    search_results = r.text
    search_results = search_results.replace('\"', '\\\"')                                                     # Make sure that quotes are properly escaped
    search_results = search_results.replace('\'', '\"')                                                       # LyricWiki returns strings surrounded by single quotes
    search_results = search_results.replace('song = ', '')                                                    # LyricWiki prepends song = to JSON, screwing with decoders
    search_results = json.loads(search_results)
    # print(search_results['lyrics'])
  except:
    print('[ERROR] Could not parse search results from LyricWiki')

  if search_results['lyrics'] != 'Not found':
    r = requests.get(search_results['url'], timeout=10, proxies=proxy)
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

def Metrolyrics_get_lyrics(artist, title):                                                      # Mildly crippled because Metrolyrics uses Angular
  proxy = urllib.request.getproxies()                                                           # And Requests doesn't support loading pages w/ JS
  artist = unidecode.unidecode(artist)                                                          # Remove accents
  artist = artist.replace(' ', '-').lower()                                                     # Replace spaces with en-dashes and formats to lowercase
  title = unidecode.unidecode(title)
  title = title.replace(' ', '-').lower()
  url = METROLYRICS_URL_BASE + '{title}-lyrics-{artist}.html'.format(title=title, artist=artist)
  # print(url)

  r = requests.get(url, timeout=10, proxies=proxy)
  r.encoding = 'utf-8'

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics_div = document.find('div', id='lyrics-body-text')

    verses = []
    [verses.append(elem.get_text()) for elem in lyrics_div.find_all('p')]
    
    lyrics = '\n\n'.join(verses)
    return lyrics.strip()
  except:
    print('[INFO] No results for song from LyricWiki')
    return False

  return False

def Musixmatch_get_lyrics(title):
  proxy = urllib.request.getproxies()
  title = urllib.parse.quote_plus(title)
  search_url = MUSIXMATCH_URL_BASE + '/search/{title}'.format(title=title)
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
    url = MUSIXMATCH_URL_BASE + search_result[0]['href']
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