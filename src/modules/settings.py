import configparser

current_version = 1

class Settings:
  source = 'genius'
  approximate = False
  info = False
  remove_brackets = True
  tag = True

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
    if 'tag' in config_settings:
      self.set_tag(config_settings.getboolean('tag'))

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

  def set_tag(self, tag_flag):
    self.tag = tag_flag
    self.save_settings()

  def get_tag(self):
    return self.tag

  def save_settings(self):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'source': self.source,
                          'approximate': self.approximate,
                          'info': self.info,
                          'remove_brackets': self.remove_brackets,
                          'tag': self.tag}
    config['ABOUT'] = {'version': 1}
    with open('./modules/settings.ini', 'w') as configfile:
      config.write(configfile)