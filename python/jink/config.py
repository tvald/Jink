
class Config(object):
  def __init__(self, config=None):
    self.settings = dict(config)
  
  def set(self, key_or_dict, value_or_none=None):
    if value_or_none == None:
      self.settings.update(key_or_dict)
    else:
      self.settings[key_or_dict] = value_or_none
  
  def get(self, key, default=None):
    return self.settings.get(key, default)
  
  def append(self, key, value):
    old = self.settings.setdefault(key, None)
    if type(old) != list:
      self.settings[key] = [old]
    self.settings[key].append(value)

