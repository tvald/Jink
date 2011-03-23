#!/usr/bin/python
from __future__ import with_statement

import cgi
import cgitb; cgitb.enable()

print "Content-Type: text/html"
print

JINK_PATH = '/path/to/jink/library'
CONTENT_PATH = '/path/to/repo.jink'

import os, os.path, sys
REPO_PATH = os.path.abspath(REPO_PATH)
sys.path.append(JINK_PATH)
os.chdir(REPO_PATH)


def compose_url(action, target):
  return '?action=%s&target=%s' % (action, target)


## actions
data = None
def edit():
  global ERROR_MSG, data
  if not data:
    try:
      with open('content/'+TARGET) as f:
        data = cgi.escape(f.read())
    except Exception, e:
      ERROR_MSG = 'Error: unable to open target.'
      error()
      return
  
  print "<form action='"+compose_url('submit',TARGET)+"' method='post'>"
  print "<div>"
  print "<code>"+TARGET+"</code>"
  print "<input style='float:right' type='submit' value='Submit Changes'>"
  print "</div>"
  print "<textarea name='text' rows='30' cols='80'>"
  print data + "</textarea>"
  print "</form>"


def submit():
  global ERROR_MSG, data
  if 'text' not in form:
    ERROR_MSG = 'Error: no text supplied.'
    error()
    edit()
    return
  
  data = form.getfirst('text').replace( '\r', '' )

  import jink
  def callback(evt):
    evt.args[1] = data
  
  try:
    J = jink.Jink( REPO_PATH, { 'trial-run' : True, 'quiet' : True } )
    J.plugin.register('onBeforeRender', callback)
    J.build('content/'+TARGET)
  except Exception, e:
    ERROR_MSG = 'Error: jink test build failed<br>%s' % str(e)
    error()
    edit()
    return
  
  try:
    with open('content/'+TARGET, 'w') as f:
      f.write(data)
  except Exception, e:
    ERROR_MSG = 'Error: unable to open target.'
    error()
    edit()
    return
  
  try:
    J = jink.Jink( REPO_PATH, { 'quiet' : True } )
    J.build('content/'+TARGET)
  except Exception, e:
    ERROR_MSG = 'Error: jink build failed<br>%s' % str(e)
    error()
    edit()
    return
  
  print "<div><b>Job submitted!</b><br>"
  print "<a href="+compose_url('edit',TARGET)+">continue editing</a><br>"
  print "</div>"


ERROR_MSG = False
def error():
  global ERROR_MSG
  if not ERROR_MSG:
    ERROR_MSG = "Whoops! We encountered an error while processing your request."
  print "<div style='color:red'>"+ERROR_MSG+"</div>"



# determine which action to perform
from collections import defaultdict
ACTION_MAP = defaultdict(lambda:error,
  edit = edit,
  submit = submit,
  error = error
)
ACTION='edit'


form = cgi.FieldStorage()
if 'target' in form:
  TARGET = os.path.abspath(form.getfirst('target'))
  if not TARGET.startswith(os.path.join(REPO_PATH,'')):
    ACTION = 'error'
    ERROR_MSG = 'Error: invalid path.'
  else:
    TARGET = TARGET[len(REPO_PATH)+1:]
    if 'action' in form:
      ACTION = form.getfirst('action').lower()
else:
  ACTION = 'error'
  ERROR_MSG = 'Error: no target provided.'


# print content
print """<!DOCTYPE html>
<html>
<head>
  <title>Jink Edit Script</title>
  <style type='text/css'>
    body{background:#ccc}
    div{background:#ffa; width:645px; padding:5px 10px}
  </style>
</head>
<body>"""

ACTION_MAP[ACTION]()

print "</body></html>"

