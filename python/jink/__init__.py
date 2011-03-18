import jink.engine

def Jink(source, sink, config):
  return jink.engine.Engine(source, sink, config)

__all__ = ['Jink']
