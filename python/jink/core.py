from __future__ import with_statement
import re, os, os.path

import jink.plugin
import jinja2, jinja2.meta

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
    
    exec self.source.read('site-config') in self.config
    self.sink.configure(self.source, self.config, self.log)
    
    def doload(tmpl):
      try:
        return self.source.read('templates/'+tmpl), tmpl, lambda: True
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
  
  
  def build(self, target):
    """
    Build a particular object, as identified by its relative
    location within the repository.
    """
    
    if len(target) < 8 or target[:8] != 'content/':
      raise Exception('cannot build non-content target "%s"' % target)
    f_target = target[8:]
    
    # filter cascade
    action = self._filter(f_target, self.filters, 'ignore')
    
    if action == 'copy':
      self.log(1, '  Copying "%s"...' % target)
      self.sink.write(target, self.source.read(target))
    elif action == 'ignore':
      self.log(1, '  Ignoring "%s"...' % target)
    elif action == 'render':
      self.log(1, '  Rendering "%s"...' % target)
      self.sink.write(target, self._render(f_target,
                                           self.source.read(target)))
    elif action == None:
      self.log(1, 'WARNING: No action specified for "%s"...' % target)
    else:
      self.log(1, 'WARNING: Unknown action [%s] on "%s"...' % (action, target))
  
  
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

  def get_templates(self, target):
    """ list all templates from which the target inherits """
    
    # sanity check...
    if len(target) < 8 or target[:8] != 'content/':
      raise Exception('cannot build non-content target "%s"' % target)
    f_target = target[8:]
    action = self._filter(f_target, self.filters, 'ignore')
    if action != 'render': return []
    
    t = []
    first = True
    from collections import deque
    Q = deque()
    
    while True:
      if target in self.tmpl_cache:
        Q.extend(self.tmpl_cache[target])
        first = False
      else:
        a = []
        data = self.source.read(target)
        
        refs = jinja2.meta.find_referenced_templates(self.engine.parse(data))
        refs = [x for x in refs]
        
        if len(refs) > 0:
          Q.extend(refs)
          a.extend(refs)
        elif first:
          f_target = target[8:]  # trim leading 'content/'
          tmpl = self._filter(f_target, self.templates)
          if tmpl:
            Q.append(tmpl)
            a.append(tmpl)
        
        if first:
          first = False
        else:
          self.tmpl_cache[target] = a
      
      if len(Q) == 0: return t
      target = 'templates/'+Q.popleft()
      t.append(target)

