"""
jink   Jinja2-based templating build system
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
  """Rebuild based on changes since the last build"""
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

def dispatch(*sysargs):
  """ Dispatches a jink command. """
  global flags, args
  
  # dirt-simple argument processing
  for x in sysargs:
    # all flags are assumed to be of the form '-flag'
    if x.startswith('-'):
      flags.append(x[1:])
    # everything else is an argument
    else:
      args.append(x)
  
  # we must have a command to dispatch
  if len(args) == 0:
    die(__doc__)
  
  cmd = args[0]
  args = args[1:]
  
  # check for proper arguments prior to dispatch
  c = cmdset.get(cmd,False) or die('Unknown command: %s' % cmd)
  l = len(args)
  
  mx = c.func_code.co_argcount         # maximum argument count
  mm = mx - len(c.func_defaults or []) # minimum argument count
  
  # "co_flags & 0x04" checks whether the varargs flag is set
  if l < mm or (l > mx and not (c.func_code.co_flags & 0x04)):
    help(cmd)
    die('')
  
  # dispatch the command
  try:
    c(*args)
  # DEBUG (python exception handling sucks...)
  except:
    raise
  # !DEBUG
  #except Exception, e:
  #  die(str(e))


def die(msg):
  """ Displays an error message and then exits. """
  import sys
  print msg
  sys.exit(1)


def CreateEngine():
  """ Creates the Jink engine which controls rendering. """
  global engine
  from jink.engine import Engine
  
  # use the test (dummy) data sink
  if 't' in flags:
    from jink.engine import TestSink
    sink = TestSink('v' in flags)
  else:
    from jink.fs import SinkFS
    sink = SinkFS()
  
  # for now, filesystem is the only supported data source
  # eventually we'll support git, and maybe others
  from jink.fs import SourceFS
  source = SourceFS(*FindRepo())
  
  engine = Engine(source, sink)


def FindRepo():
  """ Search up the filesystem hierarchy to locate the repository root. """
  root = os.path.abspath(os.getcwd())
  fixup = root
  while not os.path.exists(os.path.join(root,'.jink')):
    next = os.path.dirname(root)
    if next == root: # reached fs root
      raise Exception('fatal: not a jink repository')
    root = next
  # return the root directory, plus the relative path to the cwd
  return (root, fixup != root and fixup[len(root)+1:] or '')


#TODO: hooks (auto-stage with a post-build hook)
#TODO: switch to FunctionLoader
#TODO: add README to content (auto?)
#TODO: don't rebuild completely (trace dependencies)
