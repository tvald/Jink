"""
Jink Template Framework
author: Tony Valderrama <tvald@galadore.net>
"""
import jink.core, jink.extension, urlparse

jink.extension.source.register(
    ['file',''], jink.extension.LazyFactory('jink.fs','SourceFS'))
jink.extension.sink.register(
    ['file',''], jink.extension.LazyFactory('jink.fs','SinkFS'))


def Jink(source, sink, config):
  # configure source for client
  if type(source) is str:
    uri = urlparse.urlparse(source)
    if uri.scheme == 'file' or uri.scheme == '':
      if uri.netloc is not '':
        raise Exception('file:// protocol must have empty network location')
    try:
      source = jink.extension.source.get(uri.scheme).instantiate(uri.path)
    except KeyError, e:
      raise Exception("unrecognized source protocol '%s'" % uri.scheme)
  
  # configure sink for client
  if type(sink) is str:
    uri = urlparse.urlparse(sink)
    if uri.scheme == 'file' or uri.scheme == '':
      if uri.netloc is not '':
        raise Exception('file:// protocol must have empty network location')
    try:
      sink = jink.extension.source.get(uri.scheme).instantiate()
    except KeyError, e:
      raise Exception("unrecognized sink protocol '%s'" % uri.scheme)
  
  return jink.core.Engine(source, sink, config)

__all__ = ['Jink']
