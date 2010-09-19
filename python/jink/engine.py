from __future__ import with_statement
import re, os, os.path
import mimetypes
from jinja2 import Environment, BaseLoader, TemplateNotFound

class Engine(object):
  def __init__(self, source, sink):
    self.source = source
    self.sink   = sink
    
    self.config = {
      'mime': _mime,
      'path': _path,
      'all' : _all,
      'copy':   'copy',
      'render': 'render',
      'ignore': 'ignore',
      }
    
    exec self.source.cdata() in self.config
    if 'TARGET' not in self.config:
      raise Exception('fatal: no TARGET specified in site-config')
    self.source.configure(self.config)
    self.sink.configure(self.config)
    
    def doload(env, tmpl):
      try:
        return self.source.loadTemplate(tmpl)
      except Exception, e:
        raise TemplateNotFound(tmpl)
    
    loader = BaseLoader()
    loader.get_source = doload
    
    self.engine = Environment(loader = loader)
    self.templates = self.config.get('DEFAULT_TEMPLATE',[])
    self.tmplrx = re.compile(r'{%\s*extends\s*"(.*)"\s*%}')
    self.filters = self.config.get('FILTERS',[(lambda x: True,'render')])
  
  
  def build(self, target):
    """
    Build a particular object, as identified by its relative
    location within the repository.
    """
    
    # filter properties
    prop = {
      'mime_type': mimetypes.guess_type(target)[0] or '',
      'path': target
      }
    
    # filter cascade
    for (f,action) in self.filters:
      if f(prop):
        # matched rule, now execute action
        if action == 'copy':
          print '  Copying "%s"...' % target
          self.sink.write(target, self.source.read(target))
        elif action == 'ignore':
          print '  Ignoring "%s"...' % target
        elif action == 'render':
          print '  Rendering "%s"...' % target
          self.sink.write(target, self.render(prop,self.source.read(target),
                                            dict(path=target) ))
        else:
          print 'WARNING: Unknown action [%s] on "%s"...' % \
              (action, target)
        return
    
    # failed to match anything
    print 'WARNING: No action specified for "%s"...' % target
  
  
  def render(self, prop, data, context):
    """ render template to text """
    # check if inheritance is specified
    if not self.tmplrx.search(data[:data.find(u'\n')]):
      # no, so insert default template
      for f,t in self.templates:
        if f(prop):
          data = '\n'.join(['{%% extends "%s" %%}' % t, data])
          break
    
    # render
    return self.engine.from_string(data).render(context)


#############
# UTILITIES #
#############
def _mime(txt, extra):
  r = re.compile(txt)
  return (lambda x: r.search(x['mime_type']), extra)

def _path(txt, extra):
  r = re.compile(txt)
  return (lambda x: r.search(x['path']), extra)

def _all(extra):
  return (lambda x: True, extra)


###############
# Source/Sink #
###############

class TestSink(object):
  def __init__(self, verbose = False):
    self.verbose = verbose
  
  def configure(self, config):
    self.root = config['TARGET']

  def clean(self):
    if os.path.exists(self.root):
      print '  TEST:cleaning target [%s]' % self.root
  
  def write(self, target, data):
    path = os.path.join(self.root,target)
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
      print '  TEST: creating "%s"' % dir
    
    print '  TEST: write "%s"' % path
    if self.verbose:
      print '------------------------------'
      print data
      print '------------------------------'
