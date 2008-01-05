from xml.dom import pulldom
import urllib2, re, codecs, os, sys
import time, datetime

def setup_environ(settings_mod):
    """
    Configure the runtime environment. This can also be used by external
    scripts wanting to set up a similar environment to manage.py.
    """
    # Add this project to sys.path so that it's importable in the conventional
    # way. For example, if this file (manage.py) lives in a directory
    # "myproject", this code would add "/path/to/myproject" to sys.path.
    project_directory = os.path.dirname(settings_mod.__file__)
    project_name = os.path.basename(project_directory)
    sys.path.append(os.path.join(project_directory, '..'))
    project_module = __import__(project_name, {}, {}, [''])
    sys.path.pop()

    # Set DJANGO_SETTINGS_MODULE appropriately.
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.%s' % (project_name, settings_mod.__name__)
    return project_directory

import settings
setup_environ(settings)


from tracked.geo.models import Trip, Track, WayPoint, GpxFile

gpx = GpxFile()
gpx.name = 'My Year Trip'
gpx.filename = 'neth.gpx'
gpx.save()
gpx.process()
print gpx.waypoints.count()
