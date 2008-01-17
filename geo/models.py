from django.db import models
from xml.dom import pulldom
from datetime import datetime
import time
from tracked.geo.helpers import get_distance, UTC
from tracked.settings import MEDIA_ROOT, FLICKR_KEY
import flickrapi

# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    latitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    altitude = models.DecimalField(max_digits=12, decimal_places=7, db_index=True)
    localtime = models.DateTimeField(db_index=True)
    gmtime = models.DateTimeField(db_index=True)
    class Admin:
        pass

    def __str__(self):
        return str(self.altitude) + ' ' + self.gmtime.strftime('%Y-%m-%d %H:%M:%S')


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
    def get_photos(self, flickr_user="38584744@N00"):
        
        flickr = flickrapi.FlickrAPI(FLICKR_KEY)
        result = flickr.photos_search(user_id=flickr_user, max_taken_date=self.end_time, min_taken_date=self.start_time,extras='date_taken')
        return [
                        result.xml,
        result.photos[0].photo[0]['datetaken'],

                self.end_time,
                self.start_time ]
                
    def update_data(self):
        
        # Set up accumulating variables
        previous        = False
        length          = 0
        ascent          = 0
        descent         = 0
        altitude_max    = 0
        altitude_min    = 1000
        
        for wp in self.waypoints.all().order_by('localtime'):
            if not previous:
                self.start_time = wp.localtime             
                previous = wp
            else:
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
            
                length += get_distance(previous,wp)
                # make this waypoint the previous one
                previous = wp
                
        # Create track here
        self.length    = round(length,5)
        self.ascent    = round(ascent,5)
        self.descent   = round(descent,5)
        self.altitude_max = round(altitude_max,5)
        self.altitude_min = round(altitude_min,5)
        self.end_time  = previous.localtime
        self.save()
    
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
        waypoints = self.waypoints.all().order_by('gmtime')

        # Set up accumulating variables
        previous        = False
        length = 0
        # Set the first times on the trap
        first_wp = waypoints[0]
        # Create first track and 0 out variables
        track           = Track()
        track.name      = ''
        track.description   = ''
        track.length        = 0
        track.ascent          = 0
        track.descent         = 0
        track.altitude_max    = 0
        track.altitude_min    = 1000

        track.start_time = first_wp.gmtime
        track.end_time = first_wp.gmtime
        track.save()

        # Loop through waypoints and measure distances
        for wp in waypoints:

            too_long    = False
            too_far     = False
            too_short   = False

            if not previous:            
                track.waypoints.add( wp )
                previous = wp
            else:
                secs_elapsed = wp.gmtime - previous.gmtime
                if secs_elapsed.seconds > max_interval or secs_elapsed.days > 0:
                    too_long = True
                    #assert False, [wp,previous,secs_elapsed.seconds,max_interval]
                if secs_elapsed.seconds < min_interval:
                    too_short = True

                if too_long:
                    
                    # Add track if it's long enough
                    if length > min_length:
                        track.save()
                        self.tracks.add(track)
                        track.waypoints.all().order_by('gmtime')[0].delete()
                        track.waypoints.all().order_by('-gmtime')[0].delete()
                        track.update_data()                                     
                        
                    else:
                        track.delete()


                    # maybe pop off waypoint first and last here then write a function for track to update itself


                    # Create first track and 0 out variables
                    track               = Track()
                    track.name          = ''
                    track.description   = ''
                    track.length        = 0
                    track.ascent        = 0
                    track.descent       = 0
                    track.altitude_max  = 0
                    track.altitude_min  = 1000
                    track.start_time    = wp.gmtime
                    track.end_time      = wp.gmtime
                    track.save()
                    
                    # Set up accumulating variables
                    previous        = False
                    length = 0
                    track.waypoints.add(wp)
                    previous = wp
                elif too_short:
                    previous = previous
                else:
                    length += get_distance(previous,wp)
                    track.waypoints.add(wp)
                    previous = wp


        # Add track if it's long enough
        if length > min_length:
            track.save()
            self.tracks.add(track)
            track.waypoints.all().order_by('gmtime')[0].delete()
            track.waypoints.all().order_by('-gmtime')[0].delete()
            track.update_data()                                     
    
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
                    timeob = datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
                    timeob2 = timeob.replace(tzinfo=UTC)
                    timo = time.mktime( timeob2.timetuple() )
                    tupelo = time.localtime(timo)
                    localtime = datetime(tupelo[0],tupelo[1],tupelo[2],tupelo[3],tupelo[4], tupelo[5])
                    
                    #assert False, timeob2
                    # Try get or create here
                    try:
                        w, created = WayPoint.objects.get_or_create(latitude=lat,longitude=lon,altitude=elestring,gmtime=timeob,localtime=localtime)
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


    