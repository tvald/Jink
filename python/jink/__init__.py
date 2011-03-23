"""
Jink Template Framework
author: Tony Valderrama <tvald@galadore.net>
"""
import jink.core, jink.extension, urlparse

jink.extension.source.register(
    ['file',''], jink.extension.LazyFactory('jink.fs','SourceFS'))
jink.extension.sink.register(
    ['file',''], jink.extension.LazyFactory('jink.fs','SinkFS'))


def Jink(source, config):
  # configure source for client
  if type(source) is str:
    uri = urlparse.urlparse(source)
    config['source.uri'] = uri
    try:
      source = jink.extension.source.get(uri.scheme).instantiate(uri)
    except KeyError, e:
      raise Exception("unrecognized source protocol '%s'" % uri.scheme)
  
  return jink.core.Engine(source, config)

__all__ = ['Jink']
