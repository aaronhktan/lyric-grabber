import configparser

from modules import utils

# This class should be the single source of truth for settings

current_version = 1

class Settings(object):
  _source = 'genius'
  _approximate = False
  _info = False
  _remove_brackets = True
  _metadata = True
  _text = False
  _play_sounds = True
  _show_errors = True
  _show_updates = True

  def __init__ (self, parent=None):
    config = configparser.ConfigParser()
    config.read(utils.resource_path('./modules/settings.ini'))
    config_settings = config['SETTINGS']
    if 'source' in config_settings:
      self._source = config_settings['source']
    if 'approximate' in config_settings:
      self._approximate = config_settings.getboolean('approximate')
    if 'info' in config_settings:
      self._info = config_settings.getboolean('info')
    if 'remove_brackets' in config_settings:
      self._remove_brackets = config_settings.getboolean('remove_brackets')
    if 'metadata' in config_settings:
      self._metadata = config_settings.getboolean('metadata')
    if 'text' in config_settings:
      self._text = config_settings.getboolean('text')
    if 'play_sounds' in config_settings:
      self._play_sounds = config_settings.getboolean('play_sounds')
    if 'show_errors' in config_settings:
      self._show_errors = config_settings.getboolean('show_errors')
    if 'show_updates' in config_settings:
      self._show_updates = config_settings.getboolean('show_updates')

  @property 
  def source(self):
    return Settings._source

  @source.setter
  def source(self, source_flag):
    Settings._source = str(source_flag)
    self.save_settings()

  @property
  def approximate(self):
    return Settings._approximate

  @approximate.setter
  def approximate(self, approximate_flag):
    Settings._approximate = bool(approximate_flag)
    self.save_settings()

  @property
  def info(self):
    return Settings._info

  @info.setter
  def info(self, info_flag):
    Settings._info = bool(info_flag)
    self.save_settings()

  @property
  def remove_brackets(self):
    return Settings._remove_brackets

  @remove_brackets.setter
  def remove_brackets(self, remove_brackets_flag):
    Settings._remove_brackets = bool(remove_brackets_flag)
    self.save_settings()

  @property
  def metadata(self):
    return Settings._metadata

  @metadata.setter
  def metadata(self, metadata_flag):
    Settings._metadata = bool(metadata_flag)
    self.save_settings()

  @property
  def text(self):
    return Settings._text

  @text.setter
  def text(self, text_flag):
    Settings._text = bool(text_flag)
    self.save_settings()

  @property
  def play_sounds(self):
    return Settings._play_sounds

  @play_sounds.setter
  def play_sounds(self, play_sounds_flag):
    Settings._play_sounds = bool(play_sounds_flag)
    self.save_settings()

  @property
  def show_errors(self):
    return Settings._show_errors

  @show_errors.setter
  def show_errors(self, show_errors_flag):
    Settings._show_errors = bool(show_errors_flag)
    self.save_settings()

  @property
  def show_updates(self):
    return Settings._show_updates

  @show_updates.setter
  def show_updates(self, show_updates_flag):
    Settings._show_updates = bool(show_updates_flag)
    self.save_settings()

  def save_settings(self):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'source': Settings._source,
                          'approximate': Settings._approximate,
                          'info': Settings._info,
                          'remove_brackets': Settings._remove_brackets,
                          'metadata': Settings._metadata,
                          'text': Settings._text,
                          'play_sounds': Settings._play_sounds,
                          'show_errors': Settings._show_errors,
                          'show_updates': Settings._show_updates}
    config['ABOUT'] = {'version': 1}
    with open(utils.resource_path('./modules/settings.ini'), 'w') as configfile:
      config.write(configfile)