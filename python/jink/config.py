
class Config(object):
  def __init__(self, config=None):
    self.settings = dict(config)
  
  def set(self, key_or_dict, value_or_none=None):
    if value_or_none == None:
      self.settings.update(key_or_dict)
    else:
      self.settings[key_or_dict] = value_or_none
  
  def append(self, key, value):
    old = self.settings.setdefault(key, None)
    if type(old) != list:
      self.settings[key] = [old]
    self.settings[key].append(value)
  
  def clone(self, *args, **kw):
    x = dict(self.settings)
    for d in args: x.update(d)
    x.update(kw)
    return x
  
  def get(self, key, parse, default=None):
    return parse(self.settings.get(key, default))
  
  def getStr(self, key, default=None):
    return self.get(key, str, default)
  
  def getBool(self, key, default=None):
    return self.get(key, lambda x: bool(x) and str(x).lower() != 'false', default)
  
  def getInt(self, key, default=None):
    return self.get(key, int, default)
  
  def getFloat(self, key, default=None):
    return self.get(key, float, default)
  
  def getList(self, key, default=None):
    return self.get(key, list, default)
  
  def getObj(self, key, default=None):
    return self.get(key, lambda x: x, default)
