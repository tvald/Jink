# to enable, put these lines in site-config:
#import sys; sys.path.append('path/to/this/file')
#from git_hook import create_git_hook
#plugin.register('onAfterCGIUpdate', create_git_hook('Web User <admin@%foo%.com>','edited via cgi script'))

def create_git_hook(author, message):
  def git_hook(evt):
    import subprocess, os
    if evt.context.config.getBool('trial-run', False):
      return
  
    DEVNULL = open(os.devnull, 'w')
    subprocess.check_call(
        ['git','add',evt.extra.handle.uid],
        cwd = evt.context.source.locate(evt.context.createHandle('')),
        stdout = DEVNULL,
        stderr = DEVNULL,
      )
    subprocess.check_call(
        ['git','commit','-q',evt.extra.handle.uid,'-m',message,'--author="'+author+'"'],
        cwd = evt.context.source.locate(evt.context.createHandle('')),
        stdout = DEVNULL,
        stderr = DEVNULL,
      )
  return git_hook

