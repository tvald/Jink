

class ISource(object):
  def iter_all(self):
    raise NotImplementedError('ISource.iter_all()')
  
  def locate(self, target):
    raise NotImplementedError('ISource.locate(target)')

  def stat(self, target):
    raise NotImplementedError('ISource.stat(target)')
  
  def read(self, target):
    raise NotImplementedError('ISource.read(target)')
  

class ISink(object):
  def configure(self, source, config):
    raise NotImplementedError('ISink.configure(source, config)')
  
  def locate(self, target):
    raise NotImplementedError('ISink.locate(target)')
  
  def clean(self):
    raise NotImplementedError('ISink.clean(target)')

  def stat(self, target):
    raise NotImplementedError('ISink.stat(target)')
  
  def write(self, target, data):
    raise NotImplementedError('ISink.write(target, data)')

