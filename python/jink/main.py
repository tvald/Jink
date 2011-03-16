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
    engine.build(os.path.join(relpath,x))


@command
def update():
  """Rebuild based on changes since the last build"""
  CreateEngine()
  for x in engine.source.iter_all():
    if max(map(lambda y: engine.source.stat(y),
               engine.get_templates(x)+[x])) \
           > engine.sink.stat(x):
      engine.build(x)


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
flags = {}
args  = []
flag_map = { 't':'trial-run', 'v':'verbose', 'q':'quiet' }
relpath = ''
engine = None

def dispatch(*sysargs):
  """ Dispatches a jink command. """
  global flags, args, flag_map
  flags = {}
  args  = []
  
  # dirt-simple argument processing
  for x in sysargs:
    # all flags are assumed to be of the form '-flag'
    if x.startswith('--'):
      flags[x[2:]] = True
    elif x.startswith('-'):
      if x[1:] not in flag_map:
        die("unrecognized flag '%s'" % x)
      flags[flag_map[x[1:]]] = True
    # everything else is an argument
    else:
      args.append(x)
  
  # we must have a command to dispatch
  if len(args) == 0:
    print __doc__
    print "See 'jink help' for a list of commands."
    die()
    
  
  cmd = args[0]
  args = args[1:]
  
  # check for proper arguments prior to dispatch
  c = cmdset.get(cmd,False) or die('Unknown command: %s' % cmd)
  l = len(args)
  
  mx = c.func_code.co_argcount         # maximum argument count
  mm = mx - len(c.func_defaults or []) # minimum argument count
  if c.func_code.co_flags & 0x04: mm += 1  # bump by one for varargs
  
  # "co_flags & 0x04" checks whether the varargs flag is set
  if l < mm or (l > mx and not (c.func_code.co_flags & 0x04)):
    help(cmd)
    die('incorrect number of arguments')
  
  # dispatch the command
  try:
    c(*args)
  # DEBUG (python exception handling sucks...)
  #except:
  #  raise
  # !DEBUG
  except Exception, e:
    die(str(e))


class JinkExitException(BaseException):
  pass

def die(msg = None, status = 1):
  """ Displays an error message and then exits. """
  raise JinkExitException(msg and ('jink: fatal error - ' + msg), status)


def CreateEngine():
  """ Creates the Jink engine which controls rendering. """
  global flags, engine, relpath

  # Search up the filesystem hierarchy to locate the repository root.
  cwd = os.path.abspath(os.getcwd())
  root = cwd
  while not os.path.exists(os.path.join(root,'.jink')):
    next = os.path.dirname(root)
    if next == root: # reached fs root
      raise Exception('fatal: not a jink repository')
    root = next
  relpath = cwd != root and cwd[len(root)+1:] or ''
  
  from jink.engine import Engine
  from jink.fs import SourceFS, SinkFS
  
  # for now, filesystem is the only supported data source/sink
  # eventually we'll support git, and maybe others
  engine = Engine(SourceFS(root), SinkFS(), flags)



if __name__ == '__main__':
  import sys
  try:
    dispatch(*sys.argv[1:])
  except JinkExitException, e:
    if e.args[0]: print e.args[0]
    sys.exit(e.args[1])


#TODO: more environment variables for templates (path-to-root, etc.)
#TODO: hooks (auto-stage with a post-build hook)
#TODO: switch to FunctionLoader
#TODO: add README to content (auto?)
#TODO: don't rebuild completely (trace dependencies)
