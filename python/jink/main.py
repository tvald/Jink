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
def init(context):
  """Create a site repository"""
  import jink.init
  jink.init.init('.')


@command
def rebuild(context):
  """Clean and rebuild all targets"""
  engine = context.createEngine()
  engine.sink.clean()
  for x in engine.source.iter_all(engine):
    engine.build(x)


@command
def build(context, *targets):
  """Build a set of targets"""
  engine = context.createEngine()
  for x in targets:
    engine.build(engine.createHandle(
            os.path.join(context.relpath,x)))


@command
def update(context):
  """Rebuild based on changes since the last build"""
  engine = context.createEngine()
  for x in engine.source.iter_all(engine):
    if max(map(lambda y: engine.source.stat(y),
               engine.get_templates(x)+[x])) \
           > engine.sink.stat(x):
      engine.build(x)


@command
def help(context, cmd=None):
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
    argnames = c.func_code.co_varnames[ 1 : c.func_code.co_argcount + \
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
flag_map = { 't':'trial-run', 'v':'verbose', 'q':'quiet' }

class RuntimeContext(object):
  def __init__(self, *sysargs):
    self.getOpts(sysargs)
    self.engine = None
    self.relpath = ''

  def getOpts(self, sysargs):
    global flag_map
    
    self.flags = {}
    self.args  = []
    self.cmd   = None
    self.cmd_call = die
    
    # dirt-simple argument processing
    for x in sysargs:
      # all flags are assumed to be of the form '-flag'
      if x.startswith('--'):
        self.flags[x[2:]] = True
      elif x.startswith('-'):
        if x[1:] not in flag_map:
          die("unrecognized flag '%s'" % x)
        self.flags[flag_map[x[1:]]] = True
      # everything else is an argument
      else:
        self.args.append(x)
    
    # we must have a command to dispatch
    if len(self.args) == 0:
      print __doc__
      print "See 'jink help' for a list of commands."
      die()
    
    self.cmd = self.args[0]
    self.args = self.args[1:]
  
    # validate command and arguments
    c = cmdset.get(self.cmd,False) or die('Unknown command: %s' % self.cmd)
    l = len(self.args)
    
    mx = c.func_code.co_argcount - 1     # maximum argument count
    mm = mx - len(c.func_defaults or []) # minimum argument count
    if c.func_code.co_flags & 0x04: mm += 1  # bump by one for varargs
    
    # "co_flags & 0x04" checks whether the varargs flag is set
    if l < mm or (l > mx and not (c.func_code.co_flags & 0x04)):
      help(self.cmd)
      die('incorrect number of arguments')
    
    self.cmd_call = c
  
  
  def dispatch(self):
    """ Dispatch the command. """
    try:
      self.cmd_call(self, *self.args)
    # DEBUG (python exception handling sucks...)
    except:
      raise
    # !DEBUG
    #except Exception, e:
    #  die(str(e))

  def createEngine(self):
    """ Creates the Jink engine which controls rendering. """
    # Search up the filesystem hierarchy to locate the repository root.
    cwd = os.path.abspath(os.getcwd())
    root = cwd
    while not os.path.exists(os.path.join(root,'.jink')):
      next = os.path.dirname(root)
      if next == root: # reached fs root
        raise Exception('fatal: not a jink repository')
      root = next
    self.relpath = cwd != root and cwd[len(root)+1:] or ''
    
    import jink
    self.engine = jink.Jink(root, self.flags)
    return self.engine


class JinkCommandException(Exception):
  pass

def die(msg = None, status = 1):
  """ Displays an error message and then exits. """
  raise JinkCommandException(msg and ('jink: fatal error - ' + msg), status)


if __name__ == '__main__':
  import sys
  try:
    RuntimeContext(*sys.argv[1:]).dispatch()
  except JinkCommandException, e:
    if e.args[0]: print e.args[0]
    sys.exit(e.args[1])

