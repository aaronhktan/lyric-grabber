import configparser

from modules import utils

# This class should be the single source of truth for settings

current_version = 1

class Settings:
  source = 'genius'
  approximate = False
  info = False
  remove_brackets = True
  metadata = True
  text = False
  play_sounds = True
  show_errors = True
  show_updates = True

  def __init__ (self, parent=None):
    config = configparser.ConfigParser()
    config.read(utils.resource_path('./modules/settings.ini'))
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
    if 'play_sounds' in config_settings:
      self.set_play_sounds(config_settings.getboolean('play_sounds'))
    if 'show_errors' in config_settings:
      self.set_show_errors(config_settings.getboolean('show_errors'))
    if 'show_updates' in config_settings:
      self.set_show_updates(config_settings.getboolean('show_updates'))

  def set_source(self, source_flag):
    Settings.source = str(source_flag)
    self.save_settings()

  def get_source(self):
    return Settings.source

  def set_approximate(self, approximate_flag):
    Settings.approximate = bool(approximate_flag)
    self.save_settings()

  def get_approximate(self):
    return Settings.approximate

  def set_info(self, info_flag):
    Settings.info = bool(info_flag)
    self.save_settings()

  def get_info(self):
    return Settings.info

  def set_remove_brackets(self, remove_brackets_flag):
    Settings.remove_brackets = bool(remove_brackets_flag)
    self.save_settings()

  def get_remove_brackets(self):
    return Settings.remove_brackets

  def set_metadata(self, metadata_flag):
    Settings.metadata = bool(metadata_flag)
    self.save_settings()

  def get_metadata(self):
    return Settings.metadata

  def set_text(self, text_flag):
    Settings.text = bool(text_flag)
    self.save_settings()

  def get_text(self):
    return Settings.text

  def set_play_sounds(self, play_sounds_flag):
    Settings.play_sounds = bool(play_sounds_flag)
    self.save_settings()

  def get_play_sounds(self):
    return Settings.play_sounds

  def set_show_errors(self, show_errors_flag):
    Settings.show_errors = bool(show_errors_flag)
    self.save_settings()

  def get_show_errors(self):
    return Settings.show_errors

  def set_show_updates(self, show_updates_flag):
    Settings.show_updates = bool(show_updates_flag)
    self.save_settings()

  def get_show_updates(self):
    return Settings.show_updates

  def save_settings(self):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'source': Settings.source,
                          'approximate': Settings.approximate,
                          'info': Settings.info,
                          'remove_brackets': Settings.remove_brackets,
                          'metadata': Settings.metadata,
                          'text': Settings.text,
                          'play_sounds': Settings.play_sounds,
                          'show_errors': Settings.show_errors,
                          'show_updates': Settings.show_updates}
    config['ABOUT'] = {'version': 1}
    with open(utils.resource_path('./modules/settings.ini'), 'w') as configfile:
      config.write(configfile)