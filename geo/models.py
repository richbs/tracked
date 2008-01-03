from django.db import models
from xml.dom import pulldom
from datetime import datetime
# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    latitude = models.FloatField(max_digits=12, decimal_places=9, db_index=True)
    longitude = models.FloatField(max_digits=12, decimal_places=9, db_index=True)
    altitude = models.FloatField(max_digits=10, decimal_places=6, db_index=True)
    time = models.DateTimeField(db_index=True)
    
    class Admin:
        pass

    def __str__(self):
                return str(self.altitude) + ' ' + self.time.strftime('%Y-%m-%d %H:%M:%S')


class GpxFile(models.Model):
    """
    The record of the XML file uploaded.
    Linked to some waypoints
    """
    class Admin:
        """docstring for Admin"""
        pass
            
    name        = models.CharField(blank=True, maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    filename    = models.FileField(upload_to='xml')
    waypoints   = models.ManyToManyField(WayPoint)

    def process(self):
        """
        Convert XML points to WayPoint nodes
        """
        gpxlog = pulldom.parse(self.filename)

        for event,node in gpxlog:
            # Only construct a dom from the track points
            if event == 'START_ELEMENT' and node.nodeName == 'trkpt':
                # we can expand the node to use the DOM API
                gpxlog.expandNode(node)
                # We only want track points with a time stamp
                if node.getElementsByTagName('time'):
                    timenode = node.getElementsByTagName('time')
                    elenode = node.getElementsByTagName('ele')
                    timestring = ''.join([x.nodeValue for x in timenode[0].childNodes])
                    elestring = ''.join([x.nodeValue for x in elenode[0].childNodes])
                    lat = node.getAttribute('lat')
                    lon = node.getAttribute('lon')
                    
                    # Try get or create here
                    w = WayPoint()
                    w.latitude = lat
                    w.longitude = lon
                    w.altitude = elestring
                    
                    try:
                        w.time =  datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        print node.toxml()

                    w.save()
                    self.waypoints.add(w)
                    self.save()


                else:
                    pass # This is not a active log way point

class Track(models.Model):
    """(Track description)"""
    def __str__(self):
        return self.name + ' ' + strftime('%Y-%m-%d %H:%M:%S', self.start_time)

    name        = models.CharField( maxlength=100,db_index=True)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.FloatField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint)

    class Admin:
        pass

class Trip(models.Model):
    def __str__(self):
        return "Trip"
        
    """(Trip description)"""
    name        = models.CharField( maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.FloatField(max_digits=10, decimal_places=5)
    tracks = models.ManyToManyField(Track)
    
    class Admin:
        pass



    