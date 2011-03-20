

class ISource(object):
  def iter_all(self, context):
    raise NotImplementedError('ISource.iter_all(context)')
  
  def locate(self, handle):
    raise NotImplementedError('ISource.locate(handle)')

  def stat(self, handle):
    raise NotImplementedError('ISource.stat(handle)')
  
  def read(self, handle):
    raise NotImplementedError('ISource.read(handle)')

  def update(self, handle, data):
    raise NotImplementedError('ISource.update(handle, data)')
  

class ISink(object):
  def configure(self, source, config, log_callback):
    raise NotImplementedError('ISink.configure(source, config)')
  
  def locate(self, handle):
    raise NotImplementedError('ISink.locate(handle)')
  
  def clean(self):
    raise NotImplementedError('ISink.clean(handle)')

  def stat(self, handle):
    raise NotImplementedError('ISink.stat(handle)')
  
  def write(self, handle, data):
    raise NotImplementedError('ISink.write(handle, data)')

