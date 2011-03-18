"""
Jink Template Framework
author: Tony Valderrama <tvald@galadore.net>
"""
import jink.core, jink.fs, urlparse

def Jink(source, sink, config):
  # configure source for client
  if type(source) is str:
    uri = urlparse.urlparse(source)
    if uri.scheme == 'file' or uri.scheme == '':
      if uri.netloc is not '':
        raise Exception('file:// protocol must have empty network location')
      source = jink.fs.SourceFS(source)
    else:
      raise Exception("unrecognized source protocol '%s'" % uri.scheme)
  
  # configure sink for client
  if type(sink) is str:
    uri = urlparse.urlparse(sink)
    if uri.scheme == 'file' or uri.scheme == '':
      if uri.netloc is not '':
        raise Exception('file:// protocol must have empty network location')
      sink = jink.fs.SinkFS()
    else:
      raise Exception("unrecognized sink protocol '%s'" % uri.scheme)
  
  return jink.core.Engine(source, sink, config)

__all__ = ['Jink']
