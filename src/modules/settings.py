import configparser
import os
import sys

from modules import utils

# This class should be the single source of truth for settings

current_version = 1

class Settings(object):
  _source = None
  _approximate = None
  _info = None
  _remove_brackets = None
  _metadata = None
  _text = None
  _play_sounds = None
  _show_errors = None
  _show_updates = None

  def __init__ (self, parent=None):
    config = configparser.ConfigParser()
    config.read(utils.CONFIG_PATH)

    if 'SETTINGS' not in config:
      return

    config_settings = config['SETTINGS']

    if 'source' in config_settings:
      Settings._source = config_settings['source']
    else:
      Settings._source = 'genius'
    if 'approximate' in config_settings:
      Settings._approximate = config_settings.getboolean('approximate')
    else:
      Settings._approximate = False
    if 'info' in config_settings:
      Settings._info = config_settings.getboolean('info')
    else:
      Settings._info = False
    if 'remove_brackets' in config_settings:
      Settings._remove_brackets = config_settings.getboolean('remove_brackets')
    else:
      Settings._remove_brackets = True
    if 'metadata' in config_settings:
      Settings._metadata = config_settings.getboolean('metadata')
    else:
      Settings._metadata = True
    if 'text' in config_settings:
      Settings._text = config_settings.getboolean('text')
    else:
      Settings._text = False
    if 'play_sounds' in config_settings:
      Settings._play_sounds = config_settings.getboolean('play_sounds')
    else:
      Settings._play_sounds = True
    if 'show_errors' in config_settings:
      Settings._show_errors = config_settings.getboolean('show_errors')
    else:
      Settings._show_errors = True
    if 'show_updates' in config_settings:
      Settings._show_updates = config_settings.getboolean('show_updates')
    else:
      Settings._show_updates = True

  @property 
  def source(self):
    return Settings._source

  @source.setter
  def source(self, source_flag):
    if source_flag is not None:
      Settings._source = str(source_flag)
      self.save_settings()

  @property
  def approximate(self):
    return Settings._approximate

  @approximate.setter
  def approximate(self, approximate_flag):
    if approximate_flag is not None:
      Settings._approximate = bool(approximate_flag)
      self.save_settings()

  @property
  def info(self):
    return Settings._info

  @info.setter
  def info(self, info_flag):
    if info_flag is not None:
      Settings._info = bool(info_flag)
      self.save_settings()

  @property
  def remove_brackets(self):
    return Settings._remove_brackets

  @remove_brackets.setter
  def remove_brackets(self, remove_brackets_flag):
    if remove_brackets_flag is not None:
      Settings._remove_brackets = bool(remove_brackets_flag)
      self.save_settings()

  @property
  def metadata(self):
    return Settings._metadata

  @metadata.setter
  def metadata(self, metadata_flag):
    if metadata_flag is not None:
      Settings._metadata = bool(metadata_flag)
      self.save_settings()

  @property
  def text(self):
    return Settings._text

  @text.setter
  def text(self, text_flag):
    if text_flag is not None:
      Settings._text = bool(text_flag)
      self.save_settings()

  @property
  def play_sounds(self):
    return Settings._play_sounds

  @play_sounds.setter
  def play_sounds(self, play_sounds_flag):
    if play_sounds_flag is not None:
      Settings._play_sounds = bool(play_sounds_flag)
      self.save_settings()

  @property
  def show_errors(self):
    return Settings._show_errors

  @show_errors.setter
  def show_errors(self, show_errors_flag):
    if show_errors_flag is not None:
      Settings._show_errors = bool(show_errors_flag)
      self.save_settings()

  @property
  def show_updates(self):
    return Settings._show_updates

  @show_updates.setter
  def show_updates(self, show_updates_flag):
    if show_updates_flag is not None:
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

    with open(utils.CONFIG_PATH, 'w') as configfile:
      config.write(configfile)