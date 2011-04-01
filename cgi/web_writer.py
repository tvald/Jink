#!/usr/bin/python
from __future__ import with_statement
import cgi, cgitb; cgitb.enable()

# send header so that cgitb can print an HTML stack trace if we goof
print "Content-Type: text/html"
print

# config
JINK_PATH = '/path/to/jink/library'
REPO_PATH = '/path/to/repo.jink'

# set up basic dependencies
import os, os.path
REPO_PATH = os.path.abspath(REPO_PATH)
JINK_PATH = os.path.abspath(JINK_PATH)

import sys; sys.path.append(JINK_PATH)

# record errors
errors = []
def error(*msgs, **kw):
  errors.extend(map(lambda m: '<span style="color:%s">%s</span>' % (kw.get('color','red'),cgi.escape(m)), msgs))


# start doing complicated stuff that might fail
try:
  # load query string and form fields
  form = cgi.FieldStorage()
  return_url     = form.getfirst('return', None)
  target         = form.getfirst('target', None)
  form_data      = form.getfirst('data', None)
  form_checksum  = form.getfirst('checksum', None)
  submit_type    = form.getfirst('submit','Save')
  
  URL_THIS_PAGE  = os.environ.get('REQUEST_URI', '#')
  action         = (os.environ.get('REQUEST_METHOD', 'GET') == 'POST' and \
                      submit_type != 'Reload File') and 'POST' or 'GET'
  
  field_data     = form_data
  field_checksum = form_checksum
  
  target_checksum = None
  target_data     = None
  
  TARGET_EXISTS = False
  TARGET_ISTEXT = False
  TARGET_FORCE  = False
  
  
  # load libraries and access the repository
  import hashlib, jink, subprocess
  try:
    J = jink.Jink( REPO_PATH, { 'trial-run' : True, 'quiet' : True } )
  except Exception, e:
    error(str(e))
    raise Exception('fatal: unable to access repo ['+REPO_PATH+']')
  
  
  # perform basic sanity checks
  if target == None: raise Exception('fatal: no target specified')
  target_handle = J.createHandle(target, tag='content')
  try:
    J.sink.locate( target_handle )  # security check
  except Exception, e:
    raise Exception('fatal: invalid target')
  
  
  # check the target
  TARGET_EXISTS = os.path.exists( J.source.locate(target_handle) )
  if TARGET_EXISTS:
    # try to sniff file type
    import subprocess
    try:
      _ftype = subprocess.Popen(['/usr/bin/file', '-bi', J.source.locate(target_handle)],
                               stdout=subprocess.PIPE).communicate()[0]
    except Exception, e:
      error(str(e))
      raise Exception('fatal: error while sniffing file type')
    TARGET_ISTEXT = _ftype.startswith('text')
    if not TARGET_ISTEXT: raise Exception('fatal: target is not a text file ['+_ftype+']')
    
    # calculate checksum so we know if file has changed
    try:
      target_data = cgi.escape( J.source.read( target_handle ) )
    except Exception, e:
      error(str(e))
      raise Exception('fatal: unable to read target while calculating checksum')
    target_checksum = hashlib.md5(target_data).hexdigest()
    
    field_checksum = target_checksum
    field_data     = target_data
  
  
  if action == 'POST':
    # validate submissions
    if form_data == None:
      raise Exception('fatal: no data received with POST')
    else:
      # fix up line endings
      form_data = form_data.replace( '\r', '' )
      
      # and reset data + checksum again
      field_data     = form_data
      field_checksum = form_checksum
    
    
    # test submission before accepting
    _read = J.source.read
    J.source.read = lambda h: (h == target_handle and form_data or _read(h))
    try:
      J.build( target_handle )
    except Exception, e:
      error(str(e))
      raise Exception('fatal: jink test build failed')
    
    J.config.update({'trial-run':False})
    J.source.read = _read
    
    
    # lock repository so our change doesn't hit problems
    import time
    lockfile = J.source.locate(J.createHandle('.jink.cgi.lock'))
    locked   = False
    retries  = 3
    while retries > 0 and not locked:
      try:
        fd = os.open(lockfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        locked = True
        os.close(fd)
      except Exception, e:
        retries -= 1
        time.sleep(.3)
    
    if not locked: raise Exception('fatal: unable to obtain repo lock ['+lockfile+']')
    
    
    try:
      # TODO: case if !TARGET_ISTEXT
      
      # calculate checksum of submitted data so we can check against target
      new_checksum = hashlib.md5(cgi.escape(form_data)).hexdigest()
      
      
      # check if file has changed since we began editing
      if not TARGET_EXISTS or submit_type == 'Overwrite File':
        target_checksum = new_checksum  # skip check
      else:
        try:
          # this is inefficient (we already calculated the checksum above)
          # but we need to have the lock before calculating the checksum
          target_checksum = hashlib.md5(cgi.escape(J.source.read( target_handle ))).hexdigest()
        except Exception, e:
          error(str(e))
          raise Exception('fatal: unable to open target while calculating checksum (2)')
        
        if form_checksum != target_checksum:
          TARGET_FORCE = True
          raise Exception('Warning: this file has changed since you started editing it.')
      
      
      # do the update
      if new_checksum != form_checksum:
        try:
          J.source.update( target_handle , form_data )
        except Exception, e:
          error(str(e))
          raise Exception('fatal: unable to open target for update')
        
        # successful, so update the checksum
        field_checksum = new_checksum
        TARGET_EXISTS = True
        TARGET_ISTEXT = True
        
        try:
          import jink.plugin
          J.plugin.dispatch(jink.plugin.Event('onAfterCGIUpdate', J, handle=target_handle))
        except Exception, e:
          error(str(e))
          raise Exception('fatal: cgi update hook died unexpectedly')
      
      
      # do a build, whether or not the file changed
      try:
        J.build( target_handle )
      except Exception, e:
        error(str(e))
        raise Exception('fatal: jink build failed')
    
    finally:
      # unlock the repository
      os.remove(lockfile)
    
    
    # record that the POST was successful
    error('Your changes have been saved!', color='green')
  
  # no more processing left
  
# record any problems we encounter
except Exception, e:
  error(str(e))


# finally render page
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

# render errors
if len(errors) > 0:
  errors.reverse()
  print "<div style='color:red'>"+"<br>".join(errors)+"</div>"

# render edit field
if TARGET_EXISTS and TARGET_ISTEXT:
  if return_url:
    print "<form action='"+URL_THIS_PAGE+"' method='post'><div><a href='" + return_url + "'>" + target + "</a>"
  else:
    print "<form action='"+URL_THIS_PAGE+"' method='post'><div>" + target
  print "<input type='hidden' name='checksum' value='" + field_checksum + "'>"
  if TARGET_FORCE:
    print "<input style='float:right' type='submit' name='submit' value='Overwrite File'>"
    print "<input style='float:right' type='submit' name='submit' value='Reload File'>"
  else:
    print "<input style='float:right' type='submit' name='submit' value='Save Changes'>"
  print "</div><textarea name='data' rows='30' cols='80'>" + field_data + "</textarea></form>"
  
elif not TARGET_EXISTS and target:
  print "<div style='color:green'>Note: this page does not yet exist.</div>"
  if return_url:
    print "<form action='"+URL_THIS_PAGE+"' method='post'><div><a href='" + return_url + "'>" + target + "</a>"
  else:
    print "<form action='"+URL_THIS_PAGE+"' method='post'><div>" + target
  print "<input style='float:right' type='submit' name='submit' value='Create Page'>"
  if field_data != None:
    print "</div><textarea name='data' rows='30' cols='80'>" + field_data + "</textarea></form>"
  else:
    print "</div><textarea name='data' rows='30' cols='80'></textarea></form>"

print "</body></html>"

