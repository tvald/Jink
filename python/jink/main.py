"""
jink   Git-based template build-out
Usage: jink COMMAND [arguments]
"""
from __future__ import with_statement, absolute_import
import os, os.path


################
#   COMMANDS   #
################
cmdset = {};
def command(f):
    cmdset[f.func_name] = f
    return f


@command
def init():
  """Create a site repository"""
  from jink.init import init
  init('.')


@command
def rebuild():
  """Clean and rebuild all targets"""
  CreateEngine()
  engine.sink.clean()
  for x in engine.source.iter_all():
    engine.build(x)


@command
def build(*targets):
  """Build a set of targets"""
  CreateEngine()
  for x in targets:
    engine.build(engine.source.locate(x))


@command
def update():
  """Rebuild changes based on the most recent diff"""
  raise Exception("Not yet implemented")


@command
def help(cmd=None):
  """Documentation"""
  if cmd == None:
    print __doc__
    for c in sorted(cmdset.keys()):
      print '   %s  \t%s' % (c,cmdset[c].__doc__)
    print "\nSee 'jink help COMMAND' for more information on a specific command."
  elif cmd in cmdset:
    c = cmdset[cmd]
    print 'jink-%s\t%s' % (cmd,c.__doc__)
    
    varargs  = (c.func_code.co_flags & 0x04) != 0
    argnames = c.func_code.co_varnames[ : c.func_code.co_argcount + \
                                            (varargs and 1 or 0) ]
    
    defc     = len(argnames)-len(c.func_defaults or ())
    
    print 'Usage:\tjink %s %s%s%s' % \
        (cmd,
         ' '.join(argnames[:defc]),
         ' '.join(map(lambda x:'[%s]'%x, argnames[defc:])),
         varargs and '...' or '')
  else:
    print 'jink help: Unknown command: %s' % cmd


#############
#   UTILS   #
#############
flags = []
args  = []

def main(*sysargs):
  global flags, args
  for x in sysargs:
    if x.startswith('-'):
      flags.append(x[1:])
    else:
      args.append(x)
  
  if len(args) == 0:
    die(__doc__)
  
  # sanity checks prior to dispatch
  cmd = args[0]
  args = args[1:]
  
  c = cmdset.get(cmd,False) or die('Unknown command: %s' % cmd)
  l = len(args)
  
  mx = c.func_code.co_argcount
  mm = mx - len(c.func_defaults or [])
  if l < mm or (l > mx and not (c.func_code.co_flags & 0x04)):
    help(cmd)
    die('')
  
  # dispatch the command
  try:
    c(*args)
  except:
    raise
  #except Exception, e:
  #  die(str(e))


def die(msg):
  import sys
  print msg
  sys.exit(1)


def CreateEngine():
  global engine
  from jink.engine import Engine
  
  # just testing
  if 't' in flags:
    from jink.engine import TestSink
    sink = TestSink('v' in flags)
  else:
    from jink.fs import SinkFS
    sink = SinkFS()
  
  from jink.fs import SourceFS
  source = SourceFS(*FindRepo())
  
  engine = Engine(source, sink)


def FindRepo():
  cwd = os.path.abspath(os.getcwd())
  fixup = cwd
  while not os.path.exists(os.path.join(cwd,'.jink')):
    t = os.path.dirname(cwd)
    b = os.path.basename(cwd)
    if t == cwd: # reached fs root
      raise Exception('fatal: not a jink repository')
    cwd = t
  return (cwd, fixup != cwd and fixup[:len(cwd)+1] or '')


#TODO: hooks (auto-stage with a post-build hook)
#TODO: switch to FunctionLoader
#TODO: add README to content (auto?)
#TODO: don't rebuild completely (trace dependencies)
