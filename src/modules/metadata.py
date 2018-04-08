from modules.logger import logger
from modules import settings

from collections import namedtuple
import mutagen

METADATA_TUPLE = namedtuple('metadata', ['succeeded', 'artist', 'title', 'art', 'filepath'])
ERROR_TUPLE = namedtuple('error', ['succeeded', 'message', 'filepath'])

def get_metadata(get_art, song_filepath):
  artist = ''
  title = ''
  art = None

  try:
    if song_filepath.endswith('.aac'):
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'AAC files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath))
      return ERROR_TUPLE(False, message, song_filepath)
    if song_filepath.endswith('.wav'):
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'WAV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath))
      return ERROR_TUPLE(False, message, song_filepath)
    elif song_filepath.endswith('.wv'):
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'WV files not supported;' \
      ' consider converting {file} to another format'.format(file=song_filepath))
      return ERROR_TUPLE(False, message, song_filepath)
    elif song_filepath.endswith(settings.SUPPORTED_FILETYPES):
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
        if song_filepath.endswith('.flac'):
          art = m.pictures[0].data
        else:
          for tag in ('covr', 'APIC:', 'pictures'):
            try:
              if tag == 'covr':
                art = m[tag][0]
              elif tag == 'APIC:':
                try:
                  art = m['APIC:'].data
                except:
                  pass

                try:
                  art = m['APIC:Album cover'].data
                except:
                  pass
              elif tag == 'pictures':
                art = m.pictures[0].data
              break
            except:
              pass

    else:
      message = logger.create_message(logger.LOG_LEVEL_ERROR, 'File format not supported for: {file}'.format(file=song_filepath))
      return ERROR_TUPLE(False, message, song_filepath)
    # print(str(title) + ' ' + str(artist))
  except:
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Metadata reading error for file: {file}'.format(file=song_filepath))
    return ERROR_TUPLE(False, message, song_filepath)

  if artist == '' and title == '':
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Metadata empty for {file}'.format(file=song_filepath))
    return ERROR_TUPLE(False, message, song_filepath)

  return METADATA_TUPLE(True, artist, title, art, song_filepath)

def write_lyrics_to_file(lyrics, song_filepath):
  try:
    if song_filepath.endswith(('.mp3', '.tta', '.aiff')):
      if song_filepath.endswith(('.mp3', '.tta')):
        m = mutagen.id3.ID3(song_filepath)
      elif song_filepath.endswith('.aiff'):
        song = mutagen.aiff.AIFF(song_filepath)

      try:
        # Remove any previously saved lyrics
        if len(m.getall(u'USLT')) != 0:
          m.delall(u'USLT')
        else:
          m.add(u'USLT')
      except:
        print('Failed to add USLT')

      try:
        # Save new lyrics
        m[u'USLT'] = (mutagen.id3.USLT(encoding=3, lang=u'XXX', desc=u'desc', text=lyrics))
        m.save(song_filepath)
      except:
        print('Failed to write USLT')
    elif song_filepath.endswith(('.mp4', '.m4a', '.m4v', '.ape', '.wma', '.flac', '.ogg', '.oga', '.opus')):
      m = mutagen.File(song_filepath)

      if song_filepath.endswith(('.mp4', '.m4a', 'm4v')):
        tag = u'\xa9lyr'
      elif song_filepath.endswith(('.ape', '.flac')):
        tag = 'LYRICS'
      elif song_filepath.endswith('.wma'):
        tag = 'WM/Lyrics'
      elif song_filepath.endswith(('.ogg', '.oga', '.opus')):
        tag = 'lyrics'
      else:
        raise

      m[tag] = lyrics
      m.save(song_filepath)
    else:
      pass
    message = logger.create_message(logger.LOG_LEVEL_SUCCESS, 'Wrote lyrics for file: {file}'.format(file=song_filepath))
    return ERROR_TUPLE(True, message, song_filepath)
  except Exception as e:
    print(str(e))
    message = logger.create_message(logger.LOG_LEVEL_ERROR, 'Couldn\'t write lyrics for file: {file}; error {error}'.format(file=song_filepath,
                                                                                                                            error=str(e)))
    return ERROR_TUPLE(False, message, song_filepath)