from django.db import models
from xml.dom import pulldom
from datetime import datetime
from tracked.geo.helpers import get_distance, UTC
from tracked.settings import MEDIA_ROOT

# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    latitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    altitude = models.DecimalField(max_digits=12, decimal_places=7, db_index=True)
    time = models.DateTimeField(db_index=True)
    
    class Admin:
        pass

    def __str__(self):
        return str(self.altitude) + ' ' + self.time.strftime('%Y-%m-%d %H:%M:%S')


class Track(models.Model):
    """(Track description)"""
    def __str__(self):
        return self.name + ' ' + self.start_time.strftime('%Y-%m-%d %H:%M:%S')

    name        = models.CharField( max_length=100,db_index=True)
    description = models.CharField(blank=True, max_length=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.DecimalField(max_digits=10, decimal_places=5)
    ascent = models.DecimalField(max_digits=10, decimal_places=5)
    descent = models.DecimalField(max_digits=10, decimal_places=5)
    altitude_max = models.DecimalField(max_digits=10, decimal_places=5)
    altitude_min = models.DecimalField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint)
    
    def update_data(self):
        pass
    
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
            
    name        = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=255)
    filename    = models.FileField(upload_to='xml')
    waypoints   = models.ManyToManyField(WayPoint)
    tracks      = models.ManyToManyField(Track)

    def createTracks(self, min_interval, max_interval, min_length):
        """
        min_interval    = 60
        max_interval    = 3500
        min_length      = 1        
        """
        # Our waypoints for this jaunt
        waypoints = self.waypoints.all().order_by("time")

        # Set up accumulating variables
        length          = 0
        ascent          = 0
        descent         = 0
        altitude_max    = 0
        altitude_min    = 1000
        previous        = False
        # Create first track and 0 out variables
        track           = Track()
        track.name      = ''
        track.description   = ''
        track.length        = 0
        track.ascent          = 0
        track.descent         = 0
        track.altitude_max    = 0
        track.altitude_min    = 1000
        # Set the first times on the trap
        first_wp = waypoints[0]
        track.start_time = first_wp.time
        track.end_time = first_wp.time
        track.save()

        # Loop through waypoints and measure distances
        for wp in waypoints:

            too_long    = False
            too_far     = False
            too_short   = False

            if not previous:
                track.start_time = wp.time             
                track.waypoints.add( wp )
                previous = wp
            else:
                secs_elapsed = wp.time - previous.time
                if secs_elapsed.seconds > max_interval or secs_elapsed.days > 0:
                    too_long = True
                    #assert False, [wp,previous,secs_elapsed.seconds,max_interval]
                if secs_elapsed.seconds < min_interval:
                    too_short = True

                if too_long:
                    
                    # Create track here
                    track.length    = round(length,5)
                    track.ascent    = round(ascent,5)
                    track.descent   = round(descent,5)
                    track.altitude_max = round(altitude_max,5)
                    track.altitude_min = round(altitude_min,5)
                    track.end_time  = previous.time
                    # maybe pop off waypoint first and last here then write a function for track to update itself
                    track.waypoints.all().order_by('time')[0].delete()
                    track.waypoints.all().order_by('-time')[0].delete()
                    track.save()
                    
                    # Add track if it's long enough
                    if length > min_length:
                        self.tracks.add(track)
                    else:
                        track.delete()
                    
                    # Create first track and 0 out variables
                    track               = Track()
                    track.name          = ''
                    track.description   = ''
                    track.length        = 0
                    track.ascent        = 0
                    track.descent       = 0
                    track.altitude_max  = 0
                    track.altitude_min  = 1000
                    track.start_time    = wp.time
                    track.end_time      = wp.time
                    track.save()
                    
                    # Set up accumulating variables
                    previous        = False
                    length          = 0
                    ascent          = 0
                    descent         = 0
                    altitude_max    = 0
                    altitude_min    = 1000                    
                    track.waypoints.add(wp)
                    previous = wp
                elif too_short:
                    previous = previous
                else:
                    length += get_distance(previous,wp)
                    
                    #Only do altitude calculations after second waypoint
                    if track.waypoints.count() > 1:
                        #assert False, [wp.altitude,previous.altitude]
                        # If there's an ascent, add it
                        if wp.altitude > previous.altitude:
                            ascent  += (wp.altitude - previous.altitude)
                        else:
                            descent += (previous.altitude - wp.altitude)
                        # Check if we have a new high
                        if wp.altitude > altitude_max:
                            altitude_max = wp.altitude
                        # Check if we have a new low
                        if wp.altitude < altitude_min:
                            altitude_min = wp.altitude

                    track.waypoints.add(wp)
                    previous = wp

        track.length    = round(length,5)
        track.ascent    = round(ascent,5)
        track.descent   = round(descent,5)
        track.altitude_max = round(altitude_max,5)
        track.altitude_min = round(altitude_min,5)
        track.end_time    = previous.time
        track.save()

        if length > min_length:
            self.tracks.add(track)                
        else:
            track.delete()

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
                    #timeob2 = datetime(2007,8,26,18,33,0,0,tzinfo=UTC)
                    timeob = datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
                    #timeob = timeob.replace(tzinfo=UTC)
                    #assert False, timeob2
                    # Try get or create here
                    try:
                        w, created = WayPoint.objects.get_or_create(latitude=lat,longitude=lon,altitude=elestring,time=timeob)
                        w.save()
                        self.waypoints.add(w)                        
                    except ValueError:
                        print node.toxml()
                    self.save()
                    
                else:
                    pass # This is not a active log way point

class Trip(models.Model):
    def __str__(self):
        return "Trip"
        
    """(Trip description)"""
    name        = models.CharField( max_length=100)
    description = models.CharField(blank=True, max_length=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.DecimalField(max_digits=10, decimal_places=5)
    tracks = models.ManyToManyField(Track)
    
    class Admin:
        pass


    