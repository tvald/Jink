
def git_hook(evt):
  import subprocess, os
  if evt.context.config.get('trial-run', False):
    return
  
  DEVNULL = open(os.devnull, 'w')
  subprocess.check_call(
      ['git','commit','-q','-i',evt.extra.handle.uid,'-m','testing!','--author="Testing <tvald@galadore.net>"'],
      cwd = evt.context.source.locate(evt.context.createHandle('')),
      stdout = DEVNULL,
      stderr = DEVNULL,
    )

