from colours import colours
import file_writer
from keys import genius_key
import lyric_fetcher

import argparse
from collections import namedtuple
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

def get_metadata(approximate, keep_brackets, get_art, song_filepath):
  artist = ''
  title = ''
  art = None

  try:
    if song_filepath.endswith('.aac'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' AAC files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return (None, message, song_filepath)
    if song_filepath.endswith('.wav'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' WAV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return (None, message, song_filepath)
    elif song_filepath.endswith('.wv'):
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' WV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath)
      return (None, message, song_filepath)
    elif song_filepath.endswith(SUPPORTED_FILETYPES):
      m = mutagen.File(song_filepath)
      for tag in ('TPE1', u'\xa9ART', 'Author', 'Artist', 'ARTIST', 'artist'):
        try:
          artist = str(m[tag][0])
          break
        except:
          pass
      
      for tag in ('TIT2', u'\xa9nam', 'Title', 'TITLE', 'title'):
        try:
          title = str(m[tag][0])
          break
        except:
          pass

      if get_art:
        for tag in ('covr', 'APIC:', 'pictures'):
          try:
            if tag == 'covr':
              art = m[tag][0]
            elif tag == 'APIC:':
              art = m['APIC:'].data
            elif tag == 'pictures':
              art = m.pictures[0].data
            break
          except:
            pass

    else:
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' File format not supported for: {file}'.format(file=song_filepath)
      return (None, message, song_filepath)
    # print(str(title) + ' ' + str(artist))
  except:
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Metadata reading error for file: {file}'.format(file=song_filepath)
    return (None, message, song_filepath)

  if artist == '' and title == '':
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Metadata empty for {file}'.format(file=song_filepath)
    return (None, message, song_filepath)

  if approximate and source != 'lyricwiki' and source != 'metrolyrics':
    artist = ''
  if not keep_brackets:
    artist = re.sub(r'\((.+)\)', '', artist).strip()
    title = re.sub(r'\((.+)\)', '', title).strip()

  metadata_tuple = namedtuple("metadata", ["artist", "title", "art", "filepath"])
  return metadata_tuple(artist, title, art, song_filepath)

def get_lyrics(artist, title, source, song_filepath):
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
    else:
      message = colours.ERROR + '[ERROR]' + colours.RESET + ' Source not valid! (choose from \'azlyrics\', \'genius\', \'lyricsfreak\', \'lyricwiki\', \'metrolyrics\', \'musixmatch\')'
      return (None, message)

    lyrics_tuple = namedtuple("lyrics", ["artist", "title", "lyrics", "filepath"])
    return lyrics_tuple(artist, title, lyrics, song_filepath)
  except:
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Something went horribly wrong getting lyrics for {file}!'.format(file=title)
    return (None, message)

def write_file(artist, title, write_info, lyrics, song_filepath):
  file_tuple = namedtuple('state', ['filepath', 'message'])
  if lyrics and write_info:
    file_writer.write_lyrics_to_txt(song_filepath, artist + ' - ' + title + '\n\n' + lyrics)
  elif lyrics and not write_info:
    file_writer.write_lyrics_to_txt(song_filepath, lyrics)
  else:
    message = colours.INFO + '[INFO]' + colours.RESET + ' No lyrics found for file: {file}'.format(file=title)
    return file_tuple(song_filepath, message)

  message = colours.SUCCESS + '[SUCCESS]' + colours.RESET + ' Got lyrics for file: {file}'.format(file=title)
  return file_tuple(song_filepath, message)

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
  parser.add_argument('-i', '--info',
                      action='store_true',
                      help='add song title and artist to top of file (default: lyrics only)')
  parser.add_argument('-r', '--recursive', 
                      action='store_true',
                      help='scan all subdirectories for files (default: scans specified filepath only)')
  parser.add_argument('-s', '--source', metavar='source',
                      nargs='?', choices=SUPPORTED_SOURCES, default='genius',
                      help='which lyrics source to use (default: \'genius\')')
  parser.add_argument('-t', '--tag', 
                      action='store_true',
                      help='save lyrics directly to file (default: saves them as a text file with the same name)')
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

  start = time.time()

  metadata_executor = futures.ThreadPoolExecutor(max_workers=20)

  if args.source == 'azlyrics':
    print(colours.INFO + '[WARNING]' + colours.RESET + ' AZLyrics rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=3)
  elif args.source == 'genius':
    if genius_key == '':
      print(colours.INFO + '[INFO]' + colours.RESET + ' No Genius key set; results will be less accurate. Please check keys.py!')
      args.brackets = False
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=10)
  elif args.source == 'musixmatch':
    print(colours.INFO + '[WARNING]' + colours.RESET + ' Musixmatch rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=3)
  else:
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=10)

  file_writing_executor = futures.ThreadPoolExecutor(max_workers=10)

  metadata_results = []
  lyrics_results = []
  file_writing_results = []

  if filepath.endswith(SUPPORTED_FILETYPES):
    metadata_results.append(metadata_executor.submit(get_metadata, args.approximate, args.brackets, False, filepath))
  elif args.recursive:
    for root, dirs, files in os.walk(filepath):
      for file in files:
        if file.endswith(SUPPORTED_FILETYPES):
          metadata_results.append(metadata_executor.submit(get_metadata, args.approximate, args.brackets, False, os.path.join(root, file)))
  else:
    for file in os.listdir(filepath):
      if file.endswith(SUPPORTED_FILETYPES):
        metadata_results.append(metadata_executor.submit(get_metadata, args.approximate, args.brackets, False, '{filepath}/{file}'.format(filepath=filepath, file=file)))

  for result in futures.as_completed(metadata_results):
    try:
      if result.result()[0] is None:
        print(result.result()[1])
      else:
        lyrics_results.append(lyrics_executor.submit(get_lyrics, result.result().artist, result.result().title, args.source, result.result().filepath))
    except:
      print(result.result())

  for result in futures.as_completed(lyrics_results):
    try:
      if result.result()[0] is None:
        print(result.result()[1])
      else:
        file_writing_results.append(file_writing_executor.submit(write_file, result.result().artist, result.result().title, args.info, result.result().lyrics, result.result().filepath))
    except:
      print(result.result())

  for result in futures.as_completed(file_writing_results):
    print(result.result().message)

  end = time.time()
  print('Grabbed lyrics for {number} songs in {seconds} seconds.'.format(number=len(metadata_results), seconds=end-start))

  # Clean up by deleting all text files
  # for root, dirs, files in os.walk(filepath):
  #   for file in files:
  #     if file.endswith('.txt'):
  #       os.remove(os.path.join(root, file))

if __name__ == '__main__':
    main()