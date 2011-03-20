from __future__ import with_statement
import re, os, os.path

import jink.plugin
import jinja2, jinja2.meta
import collections

### Models ###
class Handle(object):
  """
  Encapsulates a reference to an object in the jink repo.  Client
  code will never have a reason to interact directly with an
  instance  of this class.
  """
  def __init__(self, tag, ref):
    self.tag = tag
    self.ref = ref
    self.uid = self.tag+'/'+self.ref
  
  def __repr__(self):
    return self.uid

  @classmethod
  def normalize(cls, target):
    """ 
    Normalizes the target reference.
    Note: A//B, A/B/, A/./B and A/foo/../B all become A/B
    """
    parts = collections.deque()
    for p in target.split('/'):
      if (p is '' or p is '.') and len(parts) > 0:
        pass
      elif p is '..' and len(parts) > 0:
        parts.pop()
      else:
        parts.append(p)
    return '/'.join(parts)
    
  @classmethod
  def create(cls, target, tag=None):
    """ Create a handle which can be used within the jink engine"""
    norm = cls.normalize(target)
    
    if tag == None:
      norm = norm.split('/',1)
      if len(norm) == 1:
        norm.append('')
    else:
      norm = (tag,norm)
    
    return cls(*norm)

  @classmethod
  def getOrCreate(cls, maybeHandle):
    if type(maybeHandle) is str:
      return Handle.create(maybeHandle)
    elif isinstance(maybeHandle, Handle):
      return maybeHandle
    else:
      raise Exception('Cannot convert %s to jink.Handle' %
                      str(type(maybeHandle)))


class Engine(object):
  def __init__(self, source, sink, config):
    self.source = source
    self.sink   = sink
    self.plugin = jink.plugin.PluginManager(self)
    self.config = {}
    
    self.config.update(config)
    self.config.update({
      'copy':   lambda x: (re.compile(x), 'copy'),
      'render': lambda x: (re.compile(x), 'render'),
      'ignore': lambda x: (re.compile(x), 'ignore'),
      'template': lambda x, y: (re.compile(x), y),
      })
    
    exec self.source.read(self.createHandle('site-config')) in self.config
    self.sink.configure(self.source, self.config, self)
    
    def doload(tmpl):
      try:
        tmpl_data = self.source.read(self.createHandle('templates/'+tmpl))
        return (tmpl_data, tmpl, lambda: True)
      except Exception, e:
        raise jinja2.TemplateNotFound(tmpl)
    
    self.engine = jinja2.Environment(loader = jinja2.FunctionLoader(doload),
                              trim_blocks=True)
    
    self.templates = self.config.get('TEMPLATES',[])
    self.tmpl_cache = {}
    self.filters = self.config.get('FILTERS',[])
    
    self.log_level = 1
    if self.config.get('verbose',False):
      self.log_level += 1
    if self.config.get('quiet',False):
      self.log_level -= 1
  
  
  def log(self, level, msg):
    if level <= self.log_level:
      print msg
  
  def createHandle(self, target, tag = None):
    return Handle.create(target, tag = tag)
  
  def build(self, handle):
    """
    Build a particular object, as identified by its relative
    location within the repository.
    """
    
    if handle.tag != 'content':
      raise Exception('cannot build non-content target "%s"' % handle)
    
    # filter cascade
    action = self._filter(handle.ref, self.filters, 'ignore')
    
    if action == 'copy':
      self.log(1, '  Copying "%s"...' % handle)
      self.sink.write(handle, self.source.read(handle))
    elif action == 'ignore':
      self.log(1, '  Ignoring "%s"...' % handle)
    elif action == 'render':
      self.log(1, '  Rendering "%s"...' % handle)
      self.sink.write(handle, self._render(handle.ref,
                                           self.source.read(handle)))
    elif action == None:
      self.log(1, 'WARNING: No action specified for "%s"...' % handle)
    else:
      self.log(1, 'WARNING: Unknown action [%s] on "%s"...' % (action, handle))
  
  
  def _filter(self, data, filters, default = None):
    for r,t in filters:
      if r.search(data):
        return t
    return default
  
  
  @jink.plugin.api_prehook('onBeforeRender',
                           permit_argmod=True, permit_cancel=True)
  def _render(self, f_target, data):
    """ render template to text """
    
    # check if inheritance is specified
    refs = jinja2.meta.find_referenced_templates(self.engine.parse(data))
    try:
      refs.next()
    except StopIteration, e:
      # no, so insert default template
      t = self._filter(f_target, self.templates)
      if t: data = ( '{%% extends "%s" %%}\n' % t ) + data
    
    # render
    data = self.engine.from_string(data).render(dict(path = f_target))
    self.log(2, '------------------------------')
    self.log(2, data)
    self.log(2, '------------------------------')
    return data

  def get_templates(self, handle):
    """ list all templates from which the target inherits """
    
    # sanity check...
    if handle.tag != 'content':
      raise Exception('cannot build non-content target "%s"' % handle)
    
    action = self._filter(handle.ref, self.filters, 'ignore')
    if action != 'render': return []
    
    t = []
    first = True
    Q = collections.deque()
    
    while True:
      if handle.uid in self.tmpl_cache:
        Q.extend(self.tmpl_cache[handle.uid])
        first = False
      else:
        a = []
        data = self.source.read(handle)
        
        refs = jinja2.meta.find_referenced_templates(self.engine.parse(data))
        refs = [x for x in refs]
        
        if len(refs) > 0:
          Q.extend(refs)
          a.extend(refs)
        elif first:
          tmpl = self._filter(handle.ref, self.templates)
          if tmpl:
            Q.append(tmpl)
            a.append(tmpl)
        
        if first:
          first = False
        else:
          self.tmpl_cache[handle.uid] = a
      
      if len(Q) == 0: return t
      handle = Handle.create('templates/'+Q.popleft())
      t.append(handle)

