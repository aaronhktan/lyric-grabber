from collections import namedtuple
import json
import random
import re
from urllib.parse import urlencode, quote_plus
import urllib.request

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

from modules.keys import genius_key
from modules.logger import logger

AZLYRICS_URL_BASE = 'https://search.azlyrics.com/search.php?'
GENIUS_URL_BASE = 'https://api.genius.com/search?'
LYRICSFREAK_URL_BASE = 'http://www.lyricsfreak.com'
LYRICWIKI_URL_BASE = 'http://lyrics.wikia.com/api.php?'
METROLYRICS_URL_BASE = 'http://www.metrolyrics.com/'
MUSIXMATCH_URL_BASE = 'https://www.musixmatch.com'

LYRICS_TUPLE = namedtuple('lyrics', ['lyrics', 'url'])

SEARCH_ERROR = 'No results from {source} for song {file}'
PARSE_ERROR = 'Could not parse lyrics from {source} for song {file}'

USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (X11; Linux i686; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
  ]

def azlyrics_search_for_url(artist, title):
  proxy = urllib.request.getproxies()
  payload = {'q': title + ' ' + artist}
  search_url = AZLYRICS_URL_BASE + urlencode(payload, quote_via=quote_plus)
  # print(search_url)

  r = requests.get(search_url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    search_results = []
    links = []
    result_tables = document.find_all('td', class_='visitedlyr')
    [search_results.append(result_table) for result_table in result_tables]
    [links.append(search_result.find('a', href=True)) for search_result in search_results]

    url = ''
    for link in links:
      if '/lyrics/' in link['href']:
        url = link['href']
        break

    if url == '':
      logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='AZLyrics', file=title))
      return False

  except:
    logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='AZLyrics', file=title))
    return False

  return url

def azlyrics_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  headers = requests.utils.default_headers()                                                      # AZLyrics filters against bots by inspecting user-agent
  headers.update({
      'User-Agent': random.choice(USER_AGENTS),
  })

  r = requests.get(url, timeout=10, proxies=proxy, headers=headers)

  r.encoding = 'utf-8'

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', class_='', id='')

    [elem.extract() for elem in lyrics.find_all(text=lambda text:isinstance(text, Comment))]      # Remove all text that is a comment in lyrics
    [elem.extract() for elem in lyrics.find_all('div')]                                           # Remove any sub-divs in lyrics
    [elem.extract() for elem in lyrics.find_all('script')]                                        # Remove any scripts in lyrics
    [elem.extract() for elem in lyrics.find_all('i')]                                             # Remove any italics in lyrics
    [elem.extract() for elem in lyrics.find_all('br')]                                            # Remove <br> tags

    return LYRICS_TUPLE(lyrics.get_text().strip(), url)
  except:
    logger.log(logger.LOG_LEVEL_ERROR, PARSE_ERROR.format(source='AZLyrics', file=title))
    return False

  return False

def azlyrics_search_and_scrape_url(artist, title):
  url = azlyrics_search_for_url(artist, title)
  if url == False:
    return url

  lyrics = azlyrics_scrape_url(url, title)
  return lyrics

def genius_search_for_url(artist, title):
  proxy = urllib.request.getproxies()
  if (genius_key == ''):
    url_artist = unidecode.unidecode(artist)   
    url_artist = url_artist.replace(' ', '-').lower()
    url_artist = re.sub('[^a-zA-z0-9-]', '', url_artist)
    url_title = unidecode.unidecode(title)
    url_title = url_title.replace(' ', '-').lower()
    url_title = re.sub('[^a-zA-z0-9-]', '', url_title)
    url = 'https://genius.com/' + url_artist + '-' + url_title + '-lyrics'
    # print(url)
  else:
    query = title + ' ' + artist
    payload = {'q': query}
    search_url = GENIUS_URL_BASE + urlencode(payload, quote_via=quote_plus)
    # print(url)

    headers = requests.utils.default_headers()                                                    # Genius requires an authorization token to get JSON search results
    headers.update({                                                                              # Can't scrape results page because uses Angular :(
        'Authorization': 'Bearer ' + genius_key,
    })

    r = requests.get(search_url, timeout=10, proxies=proxy, headers=headers)

    try:
      search_results = json.loads(r.text)
      if search_results['meta']['status'] == 200:
        url = search_results['response']['hits'][0]['result']['url']
      else:
        logger.log(logger.LOG_LEVEL_INFO, ' Could not reach Genius; got code {code} check your Internet connection and Genius key'.format(code=search_results['meta']['status']))
        return False
    except:
      logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='Genius', file=title))
      return False

  return url

def genius_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  r = requests.get(url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')

    # Genius seems to be returning two types of content
    # One has a 'lyrics' div, the other has Lyrics__Container
    lyrics_div = document.find('div', class_='lyrics')
    if lyrics_div:
      lyrics_paragraphs = []
      [lyrics_paragraphs.append(elem.get_text()) for elem in lyrics_div.find_all('p')]

      lyrics = ''.join(lyrics_paragraphs)
    
      return LYRICS_TUPLE(lyrics.strip(), url)

    lyrics_container = document.find('div', class_=re.compile('Lyrics__Container*'))
    if lyrics_container:
      # Genius puts annotations nested with the actual lyrics spans
      # In order to extract the lyrics correctly, need to replace HTML line breaks
      # with \n line breaks
      for br in lyrics_container.find_all('br'):
        br.replace_with('\n')
      lyrics = lyrics_container.text
      return LYRICS_TUPLE(lyrics, url)

    lyrics_container = document.find('div', class_=re.compile('LyricsPlaceholder__Message*'))
    if lyrics_container:
      # When the song is an instrumental, Genius sometimes puts a LyricsPlaceholder div
      lyrics = '[Instrumental]'
      return LYRICS_TUPLE(lyrics, url)
  except:
    if genius_key == '':
      logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='Genius', file=title))
    else:
      logger.log(logger.LOG_LEVEL_ERROR, PARSE_ERROR.format(source='Genius', file=title))
    return False

  return False

def genius_search_and_scrape_url(artist, title):
  url = genius_search_for_url(artist, title)
  if url == False:
    return url

  lyrics = genius_scrape_url(url, title)
  return lyrics

def lyricsfreak_search_for_url(title):
  proxy = urllib.request.getproxies()
  payload = {'a':       'search', \
             'type':    'song', \
             'q':       title}
  search_url = LYRICSFREAK_URL_BASE + '/search.php?' + urlencode(payload, quote_via=quote_plus)
  # print(search_url)

  r = requests.get(search_url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    search_results = document.find_all('a', class_='song')

    url = LYRICSFREAK_URL_BASE + search_results[0]['href']
    # print(url)
  except:
    logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='LyricsFreak', file=title))
    return False

  return url

def lyricsfreak_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  r = requests.get(url, timeout=10, proxies=proxy)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', id='content')

    # print(lyrics)
    [elem.replace_with('\n') for elem in lyrics.find_all('br')]                                 # Remove <br> tags and reformat them into \n line breaks 
    return LYRICS_TUPLE(lyrics.get_text(), url)
  except:
    logger.log(logger.LOG_LEVEL_ERROR, PARSE_ERROR.format(source='LyricsFreak', file=title))
    return False

  return False

def lyricsfreak_search_and_scrape_url(title):
  url = lyricsfreak_search_for_url(title)
  if url == False:
    return url

  lyrics = lyricsfreak_scrape_url(url, title)
  return lyrics

def lyricwiki_search_for_url(artist, title):
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
    search_results = search_results.replace('\"', '\\\"')                                       # Make sure that quotes are properly escaped
    search_results = search_results.replace('\'', '\"')                                         # LyricWiki returns strings surrounded by single quotes
    search_results = search_results.replace('song = ', '')                                      # LyricWiki prepends song = to JSON, screwing with decoders
    search_results = json.loads(search_results)
    # print(search_results['lyrics'])
  except:
    logger.log(logger.LOG_LEVEL_ERROR, SEARCH_ERROR.format(source='LyricWiki', file=title))

  if search_results['lyrics'] != 'Not found':
    url = search_results['url']
  else:
    logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='LyricWiki', file=title))
    url = False

  return url

def lyricwiki_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  r = requests.get(url, timeout=10, proxies=proxy)
  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics = document.find('div', class_='lyricbox')                                            # Find all divs with class lyricbox

    [elem.extract() for elem in lyrics.find_all(text=lambda text:isinstance(text, Comment))]    # Remove all text that is a comment in lyrics
    [elem.extract() for elem in lyrics.find_all('div')]                                         # Remove any sub-divs in lyrics
    [elem.extract() for elem in lyrics.find_all('script')]                                      # Remove any scripts in lyrics
    [elem.replace_with('\n') for elem in lyrics.find_all('br')]                                 # Remove <br> tags and reformat them into \n line breaks 

    return LYRICS_TUPLE(lyrics.get_text().strip(), url)
  except:
    logger.log(logger.LOG_LEVEL_ERROR, PARSE_ERROR.format(source='LyricWiki', file=title))
    return False

  return False

def lyricwiki_search_and_scrape_url(artist, title):
  url = lyricwiki_search_for_url(artist, title)
  if url == False:
    return url

  lyrics = lyricwiki_scrape_url(url, title)
  return lyrics

def metrolyrics_search_for_url(artist, title):
  proxy = urllib.request.getproxies()                                                           # Mildly crippled because Metrolyrics uses Angular
  url_artist = unidecode.unidecode(artist)                                                      # And Requests doesn't support loading pages w/ JS
  url_artist = url_artist.replace(' ', '-').lower()                                             # Remove accents
  url_title = unidecode.unidecode(title)                                                        # Replace spaces with en-dashes and formats to lowercase
  url_title = url_title.replace(' ', '-').lower()
  url = METROLYRICS_URL_BASE + '{title}-lyrics-{artist}.html'.format(title=url_title, artist=url_artist)

  return url

def metrolyrics_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  r = requests.get(url, timeout=10, proxies=proxy)
  r.encoding = 'utf-8'

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics_div = document.find('div', id='lyrics-body-text')

    verses = []
    [verses.append(elem.get_text()) for elem in lyrics_div.find_all('p')]
    
    lyrics = '\n\n'.join(verses)
    return LYRICS_TUPLE(lyrics.strip(), url)
  except:
    logger.log(logger.LOG_LEVEL_INFO, PARSE_ERROR.format(source='Metrolyrics', file=title))
    return False

  return False

def metrolyrics_search_and_scrape_url(artist, title):
  url = metrolyrics_search_for_url(artist, title)

  lyrics = metrolyrics_scrape_url(url, title)
  return lyrics

def musixmatch_search_for_url(artist, title):
  proxy = urllib.request.getproxies()
  url_params = urllib.parse.quote_plus(artist + ' ' + title)
  search_url = MUSIXMATCH_URL_BASE + '/search/{params}'.format(params=url_params)
  # print(search_url)

  headers = requests.utils.default_headers()                                                    # Musixmatch filters against bots by inspecting user-agent
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
    logger.log(logger.LOG_LEVEL_INFO, SEARCH_ERROR.format(source='Musixmatch', file=title))
    return False

  return url

def musixmatch_scrape_url(url, title):
  proxy = urllib.request.getproxies()
  headers = requests.utils.default_headers()                                                    # Musixmatch filters against bots by inspecting user-agent
  headers.update({
      'User-Agent': random.choice(USER_AGENTS),
  })

  r = requests.get(url, timeout=10, proxies=proxy, headers=headers)

  try:
    document = BeautifulSoup(r.text, 'html.parser')
    lyrics_paragraphs = []
    [lyrics_paragraphs.append(elem.get_text()) for elem in document.find_all('p', class_='mxm-lyrics__content')]

    lyrics = '\n'.join(lyrics_paragraphs)

    lyrics = lyrics.replace('<i>', '')                                                          # Remove any italics in lyrics
    lyrics = lyrics.replace('<br>', '\n')                                                       # Remove <br> tags and reformat them into \n line breaks
    lyrics = lyrics.replace('\\"', '"')                                                         # Replace escaped quotes with just quotes
    lyrics = lyrics.replace('\\n', '\n')                                                        # Replace \n string with \n line breaks

    return LYRICS_TUPLE(lyrics.strip(), url)
  except:
    logger.log(logger.LOG_LEVEL_ERROR, PARSE_ERROR.format(source='Musixmatch', file=title))
    return False

  return False

def musixmatch_search_and_scrape_url(artist, title):
  url = musixmatch_search_for_url(artist, title)
  if url == False:
    return url

  lyrics = musixmatch_scrape_url(url, title)
  return lyrics
