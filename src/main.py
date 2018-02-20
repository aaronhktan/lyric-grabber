import file_writer
import lyric_grabber

import os

try:
  import taglib
except ImportError:
  raise ImportError('Can\'t find pytaglib; please install it via "pip install pytaglib"')

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
#       lyrics = lyric_grabber.Musixmatch_get_lyrics(title)
#       # print(lyrics)

#       if lyrics:
#         file_writer.write_lyrics_to_txt(file, lyrics)
#       else:
#         print('[INFO] No lyrics found for file: {file}'.format(file=file))
#     except:
#       print('[ERROR] Something went horribly wrong!')