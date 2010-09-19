"""
Create a template jink repo.
"""
from __future__ import with_statement

def init(path):
  import os, os.path, shutil
  from subprocess import check_call
  
  repopath = os.path.abspath(os.path.normpath(path))
  
  print 'Creating repo location...'
  if os.path.exists(repopath):
    if not os.path.isdir(repopath):
      raise Exception('Cannot create "%s": path is not a directory' % repopath)
    elif len(os.listdir(repopath)) != 0:
      raise Exception('Cannot create "%s": path is not empty' % repopath)
  else:
    os.mkdir(repopath)
  
  print 'Initializing repo structure...'
  os.mkdir(os.path.join(repopath,'content'))
  os.mkdir(os.path.join(repopath,'templates'))
  
  print 'Configuring site...'
  with open(os.path.join(repopath,'site-config'),'w') as f:
    f.write(DEFAULT_CONFIG)
  
  print 'Writing default templates...'
  with open(os.path.join(repopath,'templates','master.tmpl'),'w') as f:
    f.write(MASTER_TMPL)
  
  print 'Writing default content...'
  with open(os.path.join(repopath,'content','index.html'),'w') as f:
    f.write(INDEX_HTML)
  
  print 'Creating .jink cache file...'
  with open(os.path.join(repopath,'.jink'),'w') as f:
    f.write('# jink repository')
  
  print 'Done!'


## DATA ##
DEFAULT_CONFIG="""TARGET_changeme = 'path/to/target'
DEFAULT_TEMPLATE = [
  all('master.tmpl')
  ]
FILTERS = [
  mime('^text/',render),
  all(copy)
  ]
"""


MASTER_TMPL="""<!DOCTYPE HTML>
<html>
<head>
<title>Jingawik demo page!</title>
</head>
<body>
{% block content %}
Hmm... templating seems to have failed.
{% endblock %}
</body>
</html>
"""

INDEX_HTML="""{% extends "master.tmpl" %}
{% block content %}
It works!
{% endblock %}
"""
