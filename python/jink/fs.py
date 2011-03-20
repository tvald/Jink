from __future__ import with_statement
import os, os.path, stat
import jink.prototype

class SourceFS(jink.prototype.ISource):
  def __init__(self, root):
    self.root = root
  
  def locate(self, target):
    return os.path.abspath(os.path.join(self.root,target))
  
  def stat(self, target):
    path = self.locate(target)
    return os.path.exists(path) and os.stat(path)[stat.ST_MTIME] or 0
  
  def read(self, target):
    with open(self.locate(target)) as f:
      return f.read()
  
  def iter_all(self):
    trim = len(self.root)+1
    for (r,d,f) in os.walk(self.locate('content')):
      for x in f:
        yield os.path.join(r,x)[trim:]


class SinkFS(jink.prototype.ISink):
  def __init__(self):
    pass
  
  def configure(self, source, config, log_callback):
    self.root = source.locate(config['TARGET'])
    self.trial = config.get('trial-run', False)
    self.log = log_callback
  
  def locate(self, target):
    if len(target) < 8 or target[:8] != 'content/':
      raise Exception('cannot locate target "%s" in data sink' % target)
    return os.path.join(self.root,target[8:])
  
  def clean(self):
    if os.path.exists(self.root):
      self.log(1, '  cleaning target [%s]' % self.root)
      if self.trial: return
      
      import shutil
      for x in os.listdir(self.root):
        x = os.path.join(self.root,x)
        if os.path.isdir(x): shutil.rmtree(x)
        else:                os.remove(x)
  
  def stat(self, target):
    path = self.locate(target)
    return os.path.exists(path) and os.stat(path)[stat.ST_MTIME] or 0
  
  def write(self, target, data):
    path = self.locate(target)
    
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
      self.log(1, '   creating directory: ' + dir)
      if not self.trial:
        os.makedirs(dir)
    
    self.log(1, '   write: ' + path)
    if not self.trial:
      with open(path,'w') as f:
        f.write(data)
