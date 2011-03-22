import types

class LazyFactory(object):
  def __init__(self, module_str, callable_str):
    self.module_str = module_str
    self.callable_str = callable_str
    self.factory = None
  
  def resolve(self):
    if self.factory == None:
      self.factory = reduce(lambda x, y: getattr(x, y),
                            module_str.split('.')[1:] +
                            callable_str.split('.'),
                            __import__(self.module_str))
    return self.factory
  
  def instantiate(self, *args, **kw):
    self.resolve()
    return self.factory(*args, **kw)

  def __call__(self, *args, **kw):
    self.instantiate(*args, **kw)


class Registry(object):
  def __init__(self):
    self._registry = dict()
  
  def register(self, keys, factory):
    try: iter(keys)
    except TypeError, e: keys = (keys)
    for k in keys: self._registry[k] = factory
  
  def get(self, key):
    return self._registry[key]
  
source = Registry()
sink   = Registry()


__all__ = ['LazyFactory', 'source', 'sink', 'Registry']
