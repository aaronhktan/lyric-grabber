from modules.keys import genius_key
from modules.logger import logger
from modules import lyric_grabber

import argparse
from concurrent import futures
import os
import time

SUPPORTED_FILETYPES = ('.mp3', '.mp4', '.m4a', '.m4v', '.aac', \
                       '.ape', '.wav', '.wma', '.aiff', '.wv', \
                       '.flac', '.ogg', '.oga', '.opus', '.tta')

SUPPORTED_SOURCES = ('azlyrics', 'genius', 'lyricsfreak', \
                     'lyricwiki', 'metrolyrics', 'musixmatch')

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
    logger.log(logger.LOG_LEVEL_WARNING, 'AZLyrics rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=3)
  elif args.source == 'genius':
    if genius_key == '':
      logger.log(logger.LOG_LEVEL_INFO, 'No Genius key set; results will be less accurate. Please check keys.py!')
      args.brackets = False
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=10)
  elif args.source == 'musixmatch':
    logger.log(logger.LOG_LEVEL_WARNING, 'Musixmatch rate-limiting in effect; lyric fetching per song will take up to 30 seconds!')
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=3)
  else:
    lyrics_executor = futures.ThreadPoolExecutor(max_workers=10)

  file_writing_executor = futures.ThreadPoolExecutor(max_workers=10)

  metadata_results = []
  lyrics_results = []
  file_writing_results = []

  if filepath.endswith(SUPPORTED_FILETYPES):
    metadata_results.append(metadata_executor.submit(lyric_grabber.get_metadata, False, filepath))
  elif args.recursive:
    for root, dirs, files in os.walk(filepath):
      for file in files:
        if file.endswith(SUPPORTED_FILETYPES):
          metadata_results.append(metadata_executor.submit(lyric_grabber.get_metadata, False, os.path.join(root, file)))
  else:
    for file in os.listdir(filepath):
      if file.endswith(SUPPORTED_FILETYPES):
        metadata_results.append(metadata_executor.submit(lyric_grabber.get_metadata, False, '{filepath}/{file}'.format(filepath=filepath, file=file)))

  for result in futures.as_completed(metadata_results):
    try:
      if result.result().succeeded:
        lyrics_results.append(lyrics_executor.submit(lyric_grabber.get_lyrics, args.approximate, args.brackets, result.result().artist, result.result().title, args.source, result.result().filepath))
      else:
        print(result.result().message)
    except:
      print(result.result())

  for result in futures.as_completed(lyrics_results):
    try:
      if result.result().succeeded:
        file_writing_results.append(file_writing_executor.submit(lyric_grabber.write_file, result.result().artist, result.result().title, args.info, result.result().lyrics, result.result().filepath))
      else:
        print(result.result().message)
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