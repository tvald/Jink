"""
Jink Template Framework
author: Tony Valderrama <tvald@galadore.net>
"""
import jink.core

def Jink(source, sink, config):
  return jink.core.Engine(source, sink, config)

__all__ = ['Jink']
