from colours import colours
import file_writer
import lyric_grabber

from concurrent import futures
from concurrent.futures import as_completed
import os
import time

try:
  import taglib
except ImportError:
  raise ImportError('Can\'t find pytaglib; please install it via "pip install pytaglib"')

def get_lyrics(song_filepath):
  song = taglib.File(song_filepath)

  try:
    artist = song.tags['ARTIST'][0]
    title = song.tags['TITLE'][0]
    # print(str(title) + ' ' + str(artist))
  except:
    message = colours.ERROR + '[ERROR]' + colors.RESET + ' Metadata reading error for file: {file}'.format(file=title)
    return message

  try:
    # lyrics = lyric_grabber.AZLyrics_get_lyrics(title)
    lyrics = lyric_grabber.Genius_get_lyrics(artist, title)
    # lyrics = lyric_grabber.LyricsFreak_get_lyrics(title)
    # lyrics = lyric_grabber.LyricWiki_get_lyrics(artist, title)
    # lyrics = lyric_grabber.Metrolyrics_get_lyrics(artist, title)
    # lyrics = lyric_grabber.Musixmatch_get_lyrics(title)
    # time.sleep(random.random() * 7 + 3)
    # print(lyrics)

    if lyrics:
      file_writer.write_lyrics_to_txt(song_filepath, lyrics)
    else:
      message = colours.INFO + '[INFO]' + colours.RESET + ' No lyrics found for file: {file}'.format(file=title)
      return message
  except:
    message = colours.ERROR + '[ERROR]' + colours.RESET + ' Something went horribly wrong!'
    return message

  message = colours.RESET + '[SUCCESS] Got lyrics for file: {file}'.format(file=title)
  return message

def schedule_songs(song_filepaths):
  with futures.ThreadPoolExecutor(max_workers=10) as executor:
    return executor.map(get_lyrics, song_filepaths, timeout=60)

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

#   lyrics = lyric_grabber.AZLyrics_get_lyrics(title)
#   if lyrics:
#     file_writer.write_lyrics_to_txt(title + '_azlyrics.txt', lyrics)
#   else:
#     print('[INFO] No lyrics found for file: {file}'.format(file=title))

#   lyrics = lyric_grabber.Genius_get_lyrics(title)
#   if lyrics:
#     file_writer.write_lyrics_to_txt(title + '_genius.txt', lyrics)
#   else:
#     print('[INFO] No lyrics found for file: {file}'.format(file=title)) 

  # lyrics = lyric_grabber.LyricsFreak_get_lyrics(title)
  # if lyrics:
  #   file_writer.write_lyrics_to_txt(title + '_lyricsfreak.txt', lyrics)
  # else:
  #   print('[INFO] No lyrics found for file: {file}'.format(file=title))

#   lyrics = lyric_grabber.LyricWiki_get_lyrics(artist, title)
#   if lyrics:
#     file_writer.write_lyrics_to_txt(title + '_lyricwiki.txt', lyrics)
#   else:
#     print('[INFO] No lyrics found for file: {file}'.format(file=title))

#   lyrics = lyric_grabber.Metrolyrics_get_lyrics(artist, title)
#   if lyrics:
#     file_writer.write_lyrics_to_txt(title + '_metrolyrics.txt', lyrics)
#   else:
#     print('[INFO] No lyrics found for file: {file}'.format(file=title))

#   lyrics = lyric_grabber.Musixmatch_get_lyrics(title)
#   if lyrics:
#     file_writer.write_lyrics_to_txt(title + '_musixmatch.txt', lyrics)
#   else:
#     print('[INFO] No lyrics found for file: {file}'.format(file=title))

start = time.time()

song_filepaths = []
for root, dirs, files in os.walk(os.curdir):
  for file in files:
    if file.endswith('.mp3') or file.endswith('.m4a') or \
      file.endswith('.mpc') or file.endswith('.flac') or \
      file.endswith('.mp4') or file.endswith('.asf') or \
      file.endswith('.aiff') or file.endswith('.wav') or \
      file.endswith('.tta') or file.endswith('.wv') or \
      file.endswith('.ogg') or file.endswith('.oga') or \
      file.endswith('.spx') or file.endswith('.opus'):
        song_filepaths.append(os.path.join(root, file))

results = schedule_songs(song_filepaths)
for result in results:
  print(result)

end = time.time()
print('Grabbed lyrics for {number} songs in {seconds} seconds.'.format(number=len(song_filepaths), seconds=end - start))