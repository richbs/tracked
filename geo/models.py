from django.db import models
from xml.dom import pulldom
from datetime import datetime
from tracked.geo.helpers import get_distance
from tracked.settings import MEDIA_ROOT

# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    latitude = models.FloatField(max_digits=12, decimal_places=9, db_index=True)
    longitude = models.FloatField(max_digits=12, decimal_places=9, db_index=True)
    altitude = models.FloatField(max_digits=11, decimal_places=6, db_index=True)
    time = models.DateTimeField(db_index=True)
    
    class Admin:
        pass

    def __str__(self):
        return str(self.altitude) + ' ' + self.time.strftime('%Y-%m-%d %H:%M:%S')


class Track(models.Model):
    """(Track description)"""
    def __str__(self):
        return self.name + ' ' + self.start_time.strftime('%Y-%m-%d %H:%M:%S')

    name        = models.CharField( maxlength=100,db_index=True)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.FloatField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint)

    class Admin:
        pass


# Trips and GPX files should inherit same class
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
    tracks      = models.ManyToManyField(Track)

    def createTracks(self, min_interval, max_interval, min_length):
        """
        min_interval    = 60
        max_interval    = 3500
        min_length      = 1        
        """
        distance        = 0
        previous        = False
        track = Track()
        track.length = 0
        # assert False, dir(self.waypoints.all()[0])
        first_wp = self.waypoints.all()[0]
        track.start_time = first_wp.time
        track.end_time = first_wp.time
        track.name = ''
        track.description = ''
        track.save()
        for wp in self.waypoints.all():

            too_long    = False
            too_far     = False
            too_short   = False

            if not previous:
                track.start_time = wp.time             
                track.waypoints.add( wp )
                previous = wp
            else:
                secs_elapsed = wp.time - previous.time
                if secs_elapsed.seconds > max_interval:
                    too_long = True

                if secs_elapsed.seconds < min_interval:
                    too_short = True

                if too_long:
                    # Create track here

                    track.length    = distance
                    #assert False, len(tracks)
                    track.end_time  = previous.time
                    track.save()

                    if distance > min_length:
                        self.tracks.add(track)

                    track = Track()
                    track.length = 0
                    track.start_time = wp.time
                    track.end_time = wp.time
                    track.name = ''
                    track.description = ''
                    track.save()
                    previous = False
                    distance = 0
                    track.waypoints.add(wp)
                    previous = wp
                elif too_short:
                    previous = previous
                else:
                    distance += get_distance(previous,wp)
                    track.waypoints.add(wp)
                    previous = wp

        track.length   =  round(distance,5)
        track.end_time    = previous.time
        track.save()

        if distance > min_length:
            self.tracks.add(track)                


    def processXML(self):
        """
        Convert XML points to WayPoint nodes
        """
        gpxlog = pulldom.parse(MEDIA_ROOT +  self.filename)

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

                    try:
                        w, created = WayPoint.objects.get_or_create(latitude=lat,longitude=lon,altitude=elestring,time=datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ'))
                        w.save()
                        self.waypoints.add(w)                        
                    except ValueError:
                        print node.toxml()
                    except:
                        print node.toxml()

                    self.save()
                    
                else:
                    pass # This is not a active log way point

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


    