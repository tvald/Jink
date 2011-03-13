from __future__ import with_statement
import re, os, os.path

from jinja2 import Environment, BaseLoader, TemplateNotFound, meta

class Engine(object):
  def __init__(self, source, sink, config):
    self.source = source
    self.sink   = sink
    self.config = {}
    
    self.config.update(config)
    self.config.update({
      'copy':   lambda x: (re.compile(x), 'copy'),
      'render': lambda x: (re.compile(x), 'render'),
      'ignore': lambda x: (re.compile(x), 'ignore'),
      'template': lambda x, y: (re.compile(x), y),
      })
    
    exec self.source.read('site-config') in self.config
    self.sink.configure(self.source, self.config)
    
    def doload(env, tmpl):
      try:
        return self.source.read('templates/'+tmpl), tmpl, lambda: True
      except Exception, e:
        raise TemplateNotFound(tmpl)
    
    loader = BaseLoader()
    loader.get_source = doload
    self.engine = Environment(loader = loader)
    
    self.templates = self.config.get('TEMPLATES',[])
    self.re_tmpl = re.compile(r'{%-?\s+extends\s+"(.+)"\s+-?%}')
    self.re_macr = re.compile(r'{%-?\s+from\s+"(.+)"\simport\s.+\s+-?%}')
    self.tmpl_cache = {}
    self.filters = self.config.get('FILTERS',[])
  
  
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
      print '  Copying "%s"...' % target
      self.sink.write(target, self.source.read(target))
    elif action == 'ignore':
      print '  Ignoring "%s"...' % target
    elif action == 'render':
      print '  Rendering "%s"...' % target
      self.sink.write(target, self._render(f_target,
                                           self.source.read(target)))
    elif action == None:
      print 'WARNING: No action specified for "%s"...' % target
    else:
      print 'WARNING: Unknown action [%s] on "%s"...' % (action, target)
  
  
  def _filter(self, data, filters, default = None):
    for r,t in filters:
      if r.search(data):
        return t
    return default
  
  
  def _render(self, f_target, data):
    """ render template to text """
    
    # check if inheritance is specified
    refs = meta.find_referenced_templates(self.engine.parse(data))
    try:
      refs.next()
    except StopIteration, e:
      # no, so insert default template
      t = self._filter(f_target, self.templates)
      if t: data = ( '{%% extends "%s" %%}\n' % t ) + data
    
    # render
    data = self.engine.from_string(data).render(dict(path = f_target))
    if self.config.get('verbose',False):
      print '------------------------------'
      print data
      print '------------------------------'
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
        
        x = self.re_tmpl.search(data[:data.find('\n')])
        if x:
          Q.append(x.group(1))
          a.append(x.group(1))
        elif first:
          f_target = target[8:]  # trim leading 'content/'
          tmpl = self._filter(f_target, self.templates)
          if tmpl:
            Q.append(tmpl)
            a.append(tmpl)
        
        x = self.re_macr.findall(data)
        Q.extend(x)
        a.extend(x)
        
        if first:
          first = False
        else:
          self.tmpl_cache[target] = a
      
      if len(Q) == 0: return t
      target = 'templates/'+Q.popleft()
      t.append(target)

