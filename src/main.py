from colours import colours
import file_writer
import lyric_grabber

from concurrent import futures
from concurrent.futures import as_completed
import mutagen
import os
import random
import time

SUPPORTED_FILETYPES = (
  '.mp3', '.mp4', '.m4a', '.m4v', '.aac', \
  '.ape', '.wav', '.wma', '.aiff', '.wv', \
  '.flac', '.ogg', '.oga', '.opus', '.tta'
)

def get_lyrics(song_filepath):
  # song = taglib.File(song_filepath)

  artist = ''
  title = ''
  # print("Filetype is " + str(m.tags))

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

  try:
    # lyrics = lyric_grabber.AZLyrics_get_lyrics(title)
    lyrics = lyric_grabber.Genius_get_lyrics(artist, title)
    # lyrics = lyric_grabber.LyricsFreak_get_lyrics(title)
    # lyrics = lyric_grabber.LyricWiki_get_lyrics(artist, title)
    # lyrics = lyric_grabber.Metrolyrics_get_lyrics(artist, title)
    # time_to_sleep = random.randrange(3, 10)
    # time.sleep(time_to_sleep)
    # lyrics = lyric_grabber.Musixmatch_get_lyrics(title)
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
  start = time.time()

  song_filepaths = []
  for root, dirs, files in os.walk(os.curdir):
    for file in files:
      if file.endswith(SUPPORTED_FILETYPES):
        song_filepaths.append(os.path.join(root, file))

  executor = futures.ThreadPoolExecutor(max_workers=10)
  results = [
    executor.submit(get_lyrics, song_filepath)
    for song_filepath in song_filepaths
  ]
  for result in futures.as_completed(results):
    print(result.result())

  end = time.time()
  print('Grabbed lyrics for {number} songs in {seconds} seconds.'.format(number=len(song_filepaths), seconds=end-start))

  # Clean up
  # for root, dirs, files in os.walk(os.curdir):
  #   for file in files:
  #     if file.endswith('.txt'):
  #       os.remove(os.path.join(root, file))

if __name__ == '__main__':
    main()