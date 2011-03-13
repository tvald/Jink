
_hooks = dict()

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


def bind(context):
  """
  Mostly useful for @bind(None) for detached functions.
  """
  def bind_decorator(f):
    def bind_handler(*args, **kw):
      f(None, *args, **kw)
    return bind_handler
  return bind_decorator


def unbind(f):
  """
  Mostly useful for reversing @bind(None) before the actual call.
  """
  def unbind_handler(context, *args, **kw):
    f(*args, **kw)
  return unbind_handler


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
      for callback in _hooks.setdefault(handle, []):
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


def register(handle, callback):
  """
  Register a callback for the specified event handle.  The callback
  will be passed (plugin.Event) as its arguments
  """
  _hooks.setdefault(handle, []).append(callback)
