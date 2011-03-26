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
  uri = urlparse.urlparse(source)
  config['source.uri'] = uri
  try:
    def src_factory(engine):
      return jink.extension.source.get(uri.scheme).instantiate(uri, engine)
  except KeyError, e:
    raise Exception("unrecognized source protocol '%s'" % uri.scheme)
  
  return jink.core.Engine(src_factory, config)

__all__ = ['Jink']
