from xml.dom import pulldom
print pulldom.__name__

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
gpx.name = 'My Yorkshire Trip'
gpx.filename = 'yorkshire.gpx'
gpx.save()

print gpx

gpxlog = pulldom.parse('yorkshire.gpx')


for event,node in gpxlog:
    # Only construct a dom from the track points
    if event == 'START_ELEMENT' and node.nodeName == 'trkpt':
        # we can expand the node to use the DOM API
        gpxlog.expandNode(node)
        # We only want track points with a time stamp
        if node.getElementsByTagName('time'):
            timenode = node.getElementsByTagName('time')
            elenode = node.getElementsByTagName('ele')
            timestring = timenode[0].firstChild.nodeValue
            elestring = elenode[0].firstChild.nodeValue
            lat = node.getAttribute('lat')
            lon = node.getAttribute('lon')

            w = WayPoint()
            w.latitude = lat
            w.longitude = lon
            w.altitude = elestring
            w.time =  datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
            w.save()
            gpx.waypoints.add(w)
            gpx.save()
            
            
        else:
            pass # This is not a active log way point