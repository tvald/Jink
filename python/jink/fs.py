from __future__ import with_statement
import os, os.path, stat
import jink.prototype

FS_TAG = '_FS_'

class SourceFS(jink.prototype.ISource):
  def __init__(self, root):
    self.root = root
  
  def locate(self, handle):
    tag = handle.tag
    if tag == FS_TAG: tag = '.'  # deal with explicit FS case
    return os.path.abspath(os.path.join(self.root, tag, handle.ref))
  
  def stat(self, handle):
    path = self.locate(handle)
    return os.path.exists(path) and os.stat(path)[stat.ST_MTIME] or 0
  
  def read(self, handle):
    with open(self.locate(handle)) as f:
      return f.read()
  
  def iter_all(self, context):
    trim = len(self.root)+1
    for (r,d,f) in os.walk(self.locate(context.createHandle('content'))):
      for x in f:
        yield context.createHandle(os.path.join(r,x)[trim:])


class SinkFS(jink.prototype.ISink):
  def __init__(self):
    pass
  
  def configure(self, source, config, context):
    self.root = source.locate(context.createHandle(config['TARGET'],
                                                   tag=FS_TAG))
    self.trial = config.get('trial-run', False)
    self.log = context.log
  
  def locate(self, handle):
    if handle.tag != 'content':
      raise Exception('cannot locate target "%s" in data sink' % handle)
    return os.path.join(self.root,handle.ref)
  
  def clean(self):
    if os.path.exists(self.root):
      self.log(1, '  cleaning target [%s]' % self.root)
      if self.trial: return
      
      import shutil
      for x in os.listdir(self.root):
        x = os.path.join(self.root,x)
        if os.path.isdir(x): shutil.rmtree(x)
        else:                os.remove(x)
  
  def stat(self, handle):
    path = self.locate(handle)
    return os.path.exists(path) and os.stat(path)[stat.ST_MTIME] or 0
  
  def write(self, handle, data):
    path = self.locate(handle)
    
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
      self.log(1, '   creating directory: ' + dir)
      if not self.trial:
        os.makedirs(dir)
    
    self.log(1, '   write: ' + path)
    if not self.trial:
      with open(path,'w') as f:
        f.write(data)
