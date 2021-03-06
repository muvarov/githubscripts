#!/usr/bin/python
# encoding=utf8

# github pull request update script
#
# Script changes patch version and remove label Email_sent
# Note: version changed only on pull request update event.

import cgi
import pickle
import sys
import time
import json
from StringIO import StringIO
import sys, urllib
from cgi import parse_qs, escape
import re

from github3 import login
from github3 import pulls
from github3 import issues
from github3 import issue
import os
reload(sys)  
sys.setdefaultencoding('utf8')

configfile = '~/gscripts_config.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
import gscripts_config as gcfg

gh_login = gcfg.gcfg['gh']['login']
gh_password = gcfg.gcfg['gh']['pass']


qin = sys.stdin.read()
#f = open('mr_%s.dump' % time.time(), 'w')
#pickle.dump(qin, f)
#f.close()

#fname = "mr_1537464128.91.dump"
#qin  = pickle.load( open(fname, "rb" ) )

print("Content-type: text/html\n")
print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>some title</title>
        </head>
        <body>""")

io = StringIO(qin)
js = json.load(io)

gh = login(gh_login, gh_password)

action = js['action']
if action == "synchronize" or action == "opened":
	print("<h1>action is %s, process</h1>" % action)
else:
	print("<h1>action is %s, do nothing</h1>" % action)
	print("</body></html>")
	sys.exit(0)

pr_num  = js['pull_request']['number']
#pr = repo.pull_request(pr_num)
issue = gh.issue("Linaro", "odp", pr_num)


branch  = js['pull_request']['base']['ref']
print "branch = %s\n" % branch

title = issue.title

version = 0
for m in re.finditer(r'\[PATCH.*v([0-9]+)\]', title):
	version = int(m.group(1))

version += 1

m = re.search(r"\[PATCH.*?\] (.*)", title)
if m:
	title = m.group(1)

if branch == "api-next":
	issue.edit(title="[PATCH API-NEXT v%d] %s" % (version, title))
elif branch == "devel/native-drivers":
	issue.edit(title="[PATCH NATIVE-DRIVERS v%d] %s" % (version, title))
elif branch == "2.0":
	issue.edit(title="[PATCH 2.0 v%d] %s" % (version, title))
else:
	issue.edit(title="[PATCH v%d] %s" % (version, title))
print issue.title

commits = js['pull_request']['commits']
if commits > 20:
	issue.add_labels("No_Email_sent")
else:
	# return code does not reflect if event was actually
	# removed
	try:
		issue.remove_label("Email_sent")
	except:
		pass
try:
	issue.remove_label("checkpatch")
except:
	pass

print "body_text %s\n" % issue.body_text


print("<h1>all ok!</h1>")
print("</body></html>")
