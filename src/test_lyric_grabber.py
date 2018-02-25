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