import configparser

current_version = 1

SUPPORTED_FILETYPES = ('.mp3', '.mp4', '.m4a', '.m4v', \
                       '.tta', '.ape', '.wma', '.aiff', \
                       '.flac', '.ogg', '.oga', '.opus', \
                       '.aac', '.wav', '.wv')

SUPPORTED_SOURCES = ('AZLyrics', 'Genius', 'LyricsFreak', \
                     'LyricWiki', 'Metrolyrics', 'Musixmatch')

class Settings:
  source = 'genius'
  approximate = False
  info = False
  remove_brackets = True
  metadata = True
  text = False

  def __init__ (self, parent=None):
    config = configparser.ConfigParser()
    config.read('./modules/settings.ini')
    config_settings = config['SETTINGS']
    if 'source' in config_settings:
      self.set_source(config_settings['source'])
    if 'approximate' in config_settings:
      self.set_approximate(config_settings.getboolean('approximate'))
    if 'info' in config_settings:
      self.set_info(config_settings.getboolean('info'))
    if 'remove_brackets' in config_settings:
      self.set_remove_brackets(config_settings.getboolean('remove_brackets'))
    if 'metadata' in config_settings:
      self.set_metadata(config_settings.getboolean('metadata'))
    if 'text' in config_settings:
      self.set_text(config_settings.getboolean('text'))

  def set_source(self, source_flag):
    self.source = source_flag
    self.save_settings()

  def get_source(self):
    return self.source

  def set_approximate(self, approximate_flag):
    self.approximate = approximate_flag
    self.save_settings()

  def get_approximate(self):
    return self.approximate

  def set_info(self, info_flag):
    self.info = info_flag
    self.save_settings()

  def get_info(self):
    return self.info

  def set_remove_brackets(self, remove_brackets_flag):
    self.remove_brackets = remove_brackets_flag
    self.save_settings()

  def get_remove_brackets(self):
    return self.remove_brackets

  def set_metadata(self, metadata_flag):
    self.metadata = metadata_flag
    self.save_settings()

  def get_metadata(self):
    return self.metadata

  def set_text(self, text_flag):
    self.text = text_flag
    self.save_settings()

  def get_text(self):
    return self.text

  def save_settings(self):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'source': self.source,
                          'approximate': self.approximate,
                          'info': self.info,
                          'remove_brackets': self.remove_brackets,
                          'metadata': self.metadata,
                          'text': self.text}
    config['ABOUT'] = {'version': 1}
    with open('./modules/settings.ini', 'w') as configfile:
      config.write(configfile)