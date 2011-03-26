
class MutableObject(object):
  def __init__(self, **kw):
    self.__dict__.update(kw)


class Event(object):
  def __init__(self, name, context, **kw):
    self.name = name
    self.context = context
    self.extra = MutableObject(**kw)
    self._cancel = False
  
  def cancel(self):
    self._cancel = True
  
  def isCancelled(self):
    return self._cancel


class PluginManager(object):
  def __init__(self):
    self._hooks = dict()
  
  def register(self, name, callback):
    """
    Register a callback for the specified event name.  The callback
    will be passed (plugin.Event) as its arguments
    """
    self._hooks.setdefault(name, []).append(callback)
  
  def unregister(self, name, callback):
    """
    Unegister a callback for the specified event name.  All instances
    of the callback will be removed.
    """
    self._hooks[name] = filter(lambda x: x is not callback,
                                 self._hooks.setdefault(name, []))
  
  def getCallbacks(self, name):
    return self._hooks.setdefault(name, [])
  
  def dispatch(self, evt, permit_cancel=False):
    for callback in self.getCallbacks(evt.name):
      callback(evt)
      if permit_cancel and evt.isCancelled():
        break
    return evt


__all__ = ['PluginManager', 'Event']
