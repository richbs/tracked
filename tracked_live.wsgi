import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tracked.settings'

path = '/Users/barrettsmall/Sites'
sys.path = ['/home/offspinner/webapps/wsgi/tracked', '/home/offspinner/webapps/wsgi/lib/python2.7'] + sys.path
if path not in sys.path:
    sys.path.append(path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

