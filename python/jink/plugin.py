
class Event(object):
  def __init__(self, handle, context, result, args, kw):
    self.handle = handle
    self.context = context
    self.result = result
    self.args = args
    self.kw = kw
    self._cancel = False
  
  def cancel(self):
    self._cancel = True
  
  def isCancelled(self):
    return self._cancel


class PluginManager(object):
  def __init__(self, context=None):
    self._hooks = dict()
    if context:
      self.bind(context)
  
  def bind(self, context):
    context.__plugins__ = self
    
  def register(self, handle, callback):
    """
    Register a callback for the specified event handle.  The callback
    will be passed (plugin.Event) as its arguments
    """
    self._hooks.setdefault(handle, []).append(callback)
  
  def unregister(self, handle, callback):
    """
    Unegister a callback for the specified event handle.  All instances
    of the callback will be removed.
    """
    self._hooks[handle] = filter(lambda x: x is not callback,
                                 self._hooks.setdefault(handle, []))
  
  def getCallbacks(self, handle):
    return self._hooks.setdefault(handle, [])


def api_prehook(handle, permit_cancel=False, permit_argmod=False):
  """
  Specify an external API hook which should precede execution of
  the specified function.  MUST decorate a *bound* method.
  """
  # define the decorator
  def api_decorator(f):
    # define the method call interceptor
    def intercept(context, *args, **kw):
      # dispatch to all listeners, in order registered
      for callback in context.__plugins__.getCallbacks(handle):
        evt = Event(handle, context, None, list(args), dict(kw))
        callback(evt)
        
        if permit_cancel and evt.isCancelled():
          return evt.result  # abort
        
        if permit_argmod:
          # replace the arguments
          args = evt.args
          kw = evt.kw
      
      # finally call the actual recipient
      return f(context, *args, **kw)
    
    # replace target with intercept
    return intercept
  
  # return the decorator
  return api_decorator


__all__ = ['api_prehook', 'PluginManager']
