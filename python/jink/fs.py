from __future__ import with_statement
import os, os.path


class SourceFS(object):
  def __init__(self, root):
    self.root = root
  
  def cdata(self):
    with open(os.path.join(self.root,'site-config')) as f:
      return f.read()
  
  def loadTemplate(self, tmpl):
    with open(os.path.join(self.root,'templates',tmpl)) as f:
      return f.read(), tmpl, lambda: True
  
  def iter_all(self):
    root = os.path.join(self.root,'content')
    trim = len(root)+1
    for (r,d,f) in os.walk(root):
      for x in f:
        yield os.path.join(r,x)[trim:]
  
  def read(self, target):
    with open(os.path.join(self.root,'content',target)) as f:
      return f.read()
  
  def configure(self, config):
    config['TARGET'] = os.path.join(self.root,config['TARGET'])


class SinkFS(object):
  def __init__(self):
    pass
  
  def configure(self, config):
    self.root = config['TARGET']

  def clean(self):
    if os.path.exists(self.root):
      print '  cleaning target [%s]' % self.root
      import shutil
      for x in os.listdir(self.root):
        x = os.path.join(self.root,x)
        if os.path.isdir(x): shutil.rmtree(x)
        else:                os.remove(x)
  
  def write(self, target, data):
    path = os.path.join(self.root,target)
    dir = os.path.dirname(path)
    if not os.path.exists(dir): os.makedirs(dir)
    with open(path,'w') as f:
      print '   write:',path
      f.write(data)

