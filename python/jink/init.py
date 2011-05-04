"""
Create a template jink repo.
"""
from __future__ import with_statement

def init(path):
  import os, os.path
  
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
  
  with open(os.path.join(repopath,'templates','html5.tmpl'),'w') as f:
    f.write(HTML5_TMPL)
  
  print 'Writing default content...'
  with open(os.path.join(repopath,'content','index.html'),'w') as f:
    f.write(INDEX_HTML)
  
  print 'Creating .jink cache file...'
  with open(os.path.join(repopath,'.jink'),'w') as f:
    f.write('# jink repository')
  
  print 'Done!'


## DATA ##
DEFAULT_CONFIG="""config.set({
 'build.target' : 'path/to/target', # CHANGE ME
 'build.template.rules' : [
   ( r'.*\.html' , 'master.tmpl' ),
 ],
 'build.rules' : [
   (r'.*\.html', 'render'),
   (r'.*', 'copy')
 ],
 'site.url.base' : '/'
})
"""

HTML5_TMPL="""<!DOCTYPE html>
<html>
  <head>
  <meta charset="US-ASCII">
  {% block htmlhead %}{{ '<title>%s</title>' % title if title is defined }}{% endblock %}
  </head>
  <body>
  {% block htmlbody %}{% endblock %}
  </body>
</html>
"""

MASTER_TMPL="""{% extends "html5.tmpl" %}
{% set title = 'Jink demo page!' %}
{% macro page_url(txt)  %}{{ [config('site.url.base'),txt]|join('/') }}{% endmacro %}

{% block htmlbody %}
{% block content %}
Whoops! Templating seems to have failed...
{% endblock %}
{% endblock htmlbody %}
"""

INDEX_HTML="""{% extends "master.tmpl" %}
{% block content %}
It works!
{% endblock %}
"""
