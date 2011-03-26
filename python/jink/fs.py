from __future__ import with_statement
import os, os.path, stat, types
import jink.prototype

FS_TAG = '_FS_'

  
class SourceFS(jink.prototype.ISource):
  def __init__(self, path_or_uri, context):
    if isinstance(path_or_uri, types.StringTypes):
      self.root = path_or_uri
    else:
      uri = path_or_uri
      if uri.scheme == 'file' or uri.scheme == '':
        if uri.netloc is not '':
          raise Exception('file:// protocol must have empty network location')
      self.root = uri.path
    self.context = context
  
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

  def update(self, handle, data):
    path = self.locate(handle)
    
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
      self.context.log(1, '   creating directory: ' + dir)
      if not self.context.config.get('trial-run', False):
        os.makedirs(dir)
    
    self.context.log(1, '   write: ' + path)
    if not self.context.config.get('trial-run', False):
      with open(path,'w') as f:
        f.write(data)


class SinkFS(jink.prototype.ISink):
  def __init__(self, uri, context):
    self.root = context.source.locate(
      context.createHandle(uri.path, tag=FS_TAG))
    self.context = context
  
  def locate(self, handle):
    if handle.tag != 'content':
      raise Exception('cannot locate target "%s" in data sink' % handle)
    return os.path.join(self.root,handle.ref)
  
  def clean(self):
    if os.path.exists(self.root):
      self.context.log(1, '  cleaning target [%s]' % self.root)
      if self.context.config.get('trial-run', False):
        return
      
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
      self.context.log(1, '   creating directory: ' + dir)
      if not self.context.config.get('trial-run', False):
        os.makedirs(dir)
    
    self.context.log(1, '   write: ' + path)
    if not self.context.config.get('trial-run', False):
      with open(path,'w') as f:
        f.write(data)
