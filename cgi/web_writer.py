#!/usr/bin/python
from __future__ import with_statement

import cgi
import cgitb; cgitb.enable()

print "Content-Type: text/html"
print

JINK_PATH = '/path/to/jink/library'
REPO_PATH = '/path/to/repo.jink'

import os, os.path
REPO_PATH = os.path.abspath(REPO_PATH)
os.chdir(REPO_PATH)

import sys; sys.path.append(JINK_PATH)
import jink
J = jink.Jink( REPO_PATH, { 'trial-run' : True, 'quiet' : True } )


def compose_url(action, target):
  return '?action=%s&target=%s' % (action, target)


## actions
data = None
def edit():
  global ERROR_MSG, data
  if not data:
    try:
      data = cgi.escape(J.source.read( TARGET_HANDLE ))
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

  def callback(evt):
    evt.extra.data = data
  
  try:
    J.plugin.register('onBeforeRender', callback)
    J.build( TARGET_HANDLE )
  except Exception, e:
    ERROR_MSG = 'Error: jink test build failed<br>%s' % str(e)
    error()
    edit()
    return
  
  J.config.update({'trial-run':False})
  
  import time
  locked = False
  retries = 3
  PID = str(os.getpid())
  while retries > 0:
    try:
      with open('.jink.cgi.lock', 'a') as f:
        f.write(PID+'\n')
      with open('.jink.cgi.lock', 'r') as f:
        if f.readlines()[0].strip() == PID:
          locked = True
          break
    except Exception, e:
      pass

    retries -= 1
    time.sleep(.3)

  if not locked:
    ERROR_MSG = 'Error: unable to obtain repo lock'
    error()
    edit()
    return
  
  try:
    try:
      J.source.update( TARGET_HANDLE , data )
    except Exception, e:
      ERROR_MSG = 'Error: unable to open target.<br>'+str(e)
      error()
      edit()
      return
    
    try:
      J.build( TARGET_HANDLE )
    except Exception, e:
      ERROR_MSG = 'Error: jink build failed<br>%s' % str(e)
      error()
      edit()
      return
  finally:
    os.remove('.jink.cgi.lock')
  
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
  TARGET = form.getfirst('target')
  TARGET_HANDLE = J.createHandle('content/'+TARGET)
  try:
    J.sink.locate( TARGET_HANDLE )  # security check
    if 'action' in form:
      ACTION = form.getfirst('action').lower()
  except Exception, e:
    ACTION = 'error'
    ERROR_MSG = 'Error: invalid target.'
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

