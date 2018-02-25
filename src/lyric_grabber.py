from colours import colours
import file_writer
from keys import genius_key
import lyric_fetcher

import argparse
from concurrent import futures
import mutagen
import os
import random
import re
import time

SUPPORTED_FILETYPES = (
  '.mp3', '.mp4', '.m4a', '.m4v', '.aac', \
  '.ape', '.wav', '.wma', '.aiff', '.wv', \
  '.flac', '.ogg', '.oga', '.opus', '.tta'
)

SUPPORTED_SOURCES = (
  'azlyrics', 'genius', 'lyricsfreak', \
  'lyricwiki', 'metrolyrics', 'musixmatch'
)

def get_lyrics(approximate, brackets, source, song_filepath):

  artist = ''
  title = ''

  try:
    if song_filepath.endswith('.flac'):
      m = mutagen.flac.FLAC(song_filepath)
      artist = m['artist'][0]
      title = m['title'][0]
    elif song_filepath.endswith('.ogg') or song_filepath.endswith('.oga'):
      m = mutagen.oggvorbis.OggVorbis(song_filepath)
      artist = m['Artist'][0]
      title = m['Title'][0]
    elif song_filepath.endswith('.opus'):
      m = mutagen.oggopus.OggOpus(song_filepath)
      artist = m['artist'][0]
      title = m['title'][0]
    elif song_filepath.endswith('.mp4'):
      m = mutagen.mp4.MP4(song_filepath)
      artist = m['\xa9ART'][0]
      title = m['\xa9nam'][0]
    elif song_filepath.endswith('.aac'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' AAC files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return message
    elif song_filepath.endswith('.wav'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' WAV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return message
    elif song_filepath.endswith('.wv'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' WV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return message
    elif song_filepath.endswith(SUPPORTED_FILETYPES):
      m = mutagen.File(song_filepath)
      for tag in ('TPE1', u'©ART', 'Author', 'Artist', 'ARTIST', 'artist'):
        try:
          artist = str(m[tag][0])
          break
        except KeyError:
          pass
      
      for tag in ('TIT2', u'©nam', 'Title', 'TITLE', 'title'):
        try:
          title = str(m[tag][0])
          break
        except KeyError:
          pass
    else:
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' File format not supported for: {file}'.format(file=song_filepath)
      return message      
    # print(str(title) + ' ' + str(artist))
  except:
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Metadata reading error for file: {file}'.format(file=song_filepath)
    return message

  if artist == '' and title == '':
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Metadata empty for {file}'.format(file=song_filepath)
    return message

  if approximate and source != 'lyricwiki' and source != 'metrolyrics':
    artist = ''
  if not brackets:
    artist = re.sub(r'\((.+)\)', '', artist).strip()
    title = re.sub(r'\((.+)\)', '', title).strip()

    # print(artist + ' ' + title)

  try:
    if source == 'azlyrics':
      time_to_sleep = random.randrange(10, 30)
      time.sleep(time_to_sleep)
      lyrics = lyric_fetcher.AZLyrics_get_lyrics(artist, title)
    elif source == 'genius':
      lyrics = lyric_fetcher.Genius_get_lyrics(artist, title)
    elif source == 'lyricsfreak':
      lyrics = lyric_fetcher.LyricsFreak_get_lyrics(title)
    elif source == 'lyricwiki':
      lyrics = lyric_fetcher.LyricWiki_get_lyrics(artist, title)
    elif source == 'metrolyrics':
      lyrics = lyric_fetcher.Metrolyrics_get_lyrics(artist, title)
    elif source == 'musixmatch':
      time_to_sleep = random.randrange(10, 30)
      time.sleep(time_to_sleep)
      lyrics = lyric_fetcher.Musixmatch_get_lyrics(artist, title)
    # time.sleep(time_to_sleep)
    # print(lyrics)

    if lyrics:
      file_writer.write_lyrics_to_txt(song_filepath, lyrics)
    else:
      message = colours.INFO + '[INFO]' + colours.RESET + ' No lyrics found for file: {file}'.format(file=title)
      return message
  except:
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Something went horribly wrong getting lyrics for {file}!'.format(file=title)
    return message

  message = colours.SUCCESS + '[SUCCESS]' + colours.RESET + ' Got lyrics for file: {file}'.format(file=title)
  return message

def main():
  parser = argparse.ArgumentParser(description='''
/\ \                     __            /\  _`\                /\ \     /\ \                     
\ \ \      __  __  _ __ /\_\    ___    \ \ \L\_\  _ __    __  \ \ \____\ \ \____     __   _ __  
 \ \ \  __/\ \/\ \/\`'__\/\ \  /'___\   \ \ \L_L /\`'__\/'__`\ \ \ '__`\\ \ '__`\  /'__`\/\`'__\\
  \ \ \L\ \ \ \_\ \ \ \/ \ \ \/\ \__/    \ \ \/, \ \ \//\ \L\.\_\ \ \L\ \\ \ \L\ \/\  __/\ \ \/ 
   \ \____/\/`____ \ \_\  \ \_\ \____\    \ \____/\ \_\\ \__/.\_\\ \_,__/ \ \_,__/\ \____\\ \_\ 
    \/___/  `/___/> \/_/   \/_/\/____/     \/___/  \/_/ \/__/\/_/ \/___/   \/___/  \/____/ \/_/ 
               /\___/                                            Version 0.5 by cheeseisdigusting
               \/__/                                      Grabs song lyrics so you don't need to!''',
               formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--version', action='version', version='''
/\ \                     __            /\  _`\                /\ \     /\ \                     
\ \ \      __  __  _ __ /\_\    ___    \ \ \L\_\  _ __    __  \ \ \____\ \ \____     __   _ __  
 \ \ \  __/\ \/\ \/\`'__\/\ \  /'___\   \ \ \L_L /\`'__\/'__`\ \ \ '__`\\ \ '__`\  /'__`\/\`'__\\
  \ \ \L\ \ \ \_\ \ \ \/ \ \ \/\ \__/    \ \ \/, \ \ \//\ \L\.\_\ \ \L\ \\ \ \L\ \/\  __/\ \ \/ 
   \ \____/\/`____ \ \_\  \ \_\ \____\    \ \____/\ \_\\ \__/.\_\\ \_,__/ \ \_,__/\ \____\\ \_\ 
    \/___/  `/___/> \/_/   \/_/\/____/     \/___/  \/_/ \/__/\/_/ \/___/   \/___/  \/____/ \/_/ 
               /\___/                                            Version 0.5 by cheeseisdigusting
               \/__/                                      Grabs song lyrics so you don't need to!''')
  parser.add_argument('-a', '--approximate',
                      action='store_true',
                      help='approximate searching; search only by song title (default: search by both title and artist in full)')
  parser.add_argument('-b', '--brackets',
                      action='store_false',
                      help='remove parts of song titles and artists in brackets (default: keeps titles and artists as they are)')
  parser.add_argument('-f', '--filepath', '--file', metavar='filepath',
                      nargs='?', default='default',
                      help='file/filepath to scan (default: scans current directory)')
  parser.add_argument('-s', '--source', metavar='source',
                      nargs='?', choices=SUPPORTED_SOURCES, default='genius',
                      help='which lyrics source to use (default: \'genius\')')
  parser.add_argument('-r', '--recursive', 
                      action='store_true',
                      help='scan all subdirectories for files (default: scans specified filepath only)')

  args = parser.parse_args()

  # print(args.approximate)
  # print(args.brackets)
  # print(args.filepath)
  # print(args.source)
  # print(args.recursive)

  if args.filepath == 'default':
    filepath = os.curdir
  else:
    filepath = args.filepath

  if args.source == 'azlyrics':
    print(colours.INFO + '[WARNING]' + colours.RESET + ' AZLyrics rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    executor = futures.ThreadPoolExecutor(max_workers=3)
  elif args.source == 'genius':
    if genius_key == '':
      print(colours.INFO + '[INFO]' + colours.RESET + ' No Genius key set; results will be less accurate. Please check keys.py!')
      args.brackets = False
    executor = futures.ThreadPoolExecutor(max_workers=10)
  elif args.source == 'musixmatch':
    print(colours.INFO + '[WARNING]' + colours.RESET + ' Musixmatch rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    executor = futures.ThreadPoolExecutor(max_workers=3)
  else:
    executor = futures.ThreadPoolExecutor(max_workers=10)

  start = time.time()

  results = []

  if filepath.endswith(SUPPORTED_FILETYPES):
    results.append(executor.submit(get_lyrics, args.approximate, args.brackets, args.source, filepath))
  elif args.recursive:
    for root, dirs, files in os.walk(filepath):
      for file in files:
        if file.endswith(SUPPORTED_FILETYPES):
          results.append(executor.submit(get_lyrics, args.approximate, args.brackets, args.source, os.path.join(root, file)))
  else:
    for file in os.listdir(filepath):
      if file.endswith(SUPPORTED_FILETYPES):
        results.append(executor.submit(get_lyrics, args.approximate, args.brackets, args.source, '{filepath}/{file}'.format(filepath=filepath, file=file)))

  for result in futures.as_completed(results):
    print(result.result())

  end = time.time()
  print('Grabbed lyrics for {number} songs in {seconds} seconds.'.format(number=len(results), seconds=end-start))

  # Clean up by deleting all text files
  # for root, dirs, files in os.walk(filepath):
  #   for file in files:
  #     if file.endswith('.txt'):
  #       os.remove(os.path.join(root, file))

if __name__ == '__main__':
    main()