import os

def write_lyrics_to_txt(filename, lyrics):
  try:
    lyrics_file = open(filename[:filename.rfind('.')] + '.txt', 'w+')                                   # Slice off file extension and replace with txt
    lyrics_file.write(lyrics)
    lyrics_file.close()
    return True
  except:
    return False