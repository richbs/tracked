from django.db import models
from xml.dom import pulldom
from datetime import datetime
import time
from tracked.geo.helpers import get_distance, UTC
from tracked.geo.validators import FilenameMatchesRegularExpression, HasAllowableSize
from tracked.settings import MEDIA_ROOT, FLICKR_KEY

import flickrapi

gpx_file_size = HasAllowableSize(min_size=10, max_size=1573000)
gpx_file_name = FilenameMatchesRegularExpression('^[^ ]{3,80}\.gpx$', 'Filename must end in GPX')
    
class WayPoint(models.Model):
    """A point in space and time
    
    Need to normalise Flickr info when QuerySet refactor is merged into trunk
    So select related will be more accessible
    """
    latitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, db_index=True)
    altitude = models.DecimalField(max_digits=12, decimal_places=7, db_index=True)
    localtime = models.DateTimeField(db_index=True)
    gmtime = models.DateTimeField(db_index=True)
    
    # Need to normalise this into flickrphoto model after queryset refactor
    photo_id = models.CharField(max_length=12,null=True)
    photo_title = models.CharField(max_length=256,null=True)
    photo_description = models.CharField(max_length=2000,null=True)
    photo_secret = models.CharField(max_length=10,null=True)
    photo_farm = models.PositiveSmallIntegerField(max_length=1,null=True)
    photo_server = models.PositiveSmallIntegerField(max_length=3,null=True)
    
    class Admin:
        pass

    def __unicode__(self):
        return "%s %sm" % (  self.gmtime.strftime('%Y-%m-%d %H:%M:%S'), str(self.altitude) )
        
class GpxFile(models.Model):
    """Details of the uploaded XML file

    Linked to some waypoints and some tracks
    
    """
    def __unicode__(self):
        return "%s %s" % ( self.name, self.filename )

    class Admin:
        """docstring for Admin"""
        fields = (
            (None, {
                'fields':('name','description','filename')
            }),
        )

    name        = models.CharField( max_length=100)
    description = models.CharField(blank=True, max_length=255)
    filename    = models.FileField(upload_to='xml',blank=True,validator_list=[gpx_file_size,gpx_file_name])
    waypoints   = models.ManyToManyField(WayPoint,blank=True,editable=False)

    def create_tracks(self, min_interval=60, max_interval=3500, min_length=1):
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
        track_count = 0
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
        track.gpx_file = self
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
                        track_count += 1
                        track.name = "%s %d" % ( self.name, track_count)
                        track.save()
                        self.track_set.add(track)
                         # maybe pop off waypoint first and last here then write a function for track to update itself                        
                        track.waypoints.all().order_by('gmtime')[0].delete()
                        track.waypoints.all().order_by('-gmtime')[0].delete()
                        track.update_data()                                     

                    else:
                        track.delete()

                    # Create new track and 0 out variables
                    track               = Track()
                    track.name          = "%s: %d" % ( self.name, track_count)
                    track.description   = ''
                    track.length        = 0
                    track.ascent        = 0
                    track.descent       = 0
                    track.altitude_max  = 0
                    track.altitude_min  = 1000
                    track.start_time    = wp.gmtime
                    track.end_time      = wp.gmtime
                    track.gpx_file = self                    
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
        #del(waypoints)

        # Add track if it's long enough
        if length > min_length:
            track_count += 1
            track.name = "%s %d" % ( self.name, track_count)            
            track.save()
            self.track_set.add(track)
            track.waypoints.all().order_by('gmtime')[0].delete()
            track.waypoints.all().order_by('-gmtime')[0].delete()
            track.update_data()                                     

        else:
            track.delete()

    def process_xml(self):
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
                        #w = WayPoint(latitude=lat,longitude=lon,altitude=elestring,gmtime=timeob,localtime=localtime)
                        #w.save()
                        w.gpxfile_set.add(self)
                        del(w)
                    #self.waypoints.add(w)                        
                    except ValueError:
                        assert False, node.toxml()

                    #del(created)
                else:
                    pass # This is not a active log way point
            del(node)
            
        del(gpxlog)
            
    def save(self):

        super(GpxFile, self).save() # Call the "real" save() method
        
        if self.track_set.count() < 1:
            # assert False, [ self.waypoints.count(), self.id, self.name, self.description, self.track_set]
            self.process_xml()
            self.create_tracks()



class Track(models.Model):
    """(Track description)"""
    def __unicode__(self):
        return "%s %s-%s" % (self.name, self.start_time.strftime('%Y-%m-%d %H:%M:%S'), self.end_time.strftime('%H:%M:%S') )

    name        = models.CharField( max_length=100,db_index=True, core=True)
    description = models.CharField(blank=True, max_length=255)
    start_time  = models.DateTimeField(db_index=True)
    end_time    = models.DateTimeField(db_index=True)
    length = models.DecimalField(max_digits=10, decimal_places=5)
    ascent = models.DecimalField(max_digits=10, decimal_places=5)
    descent = models.DecimalField(max_digits=10, decimal_places=5)
    altitude_max = models.DecimalField(max_digits=10, decimal_places=5)
    altitude_min = models.DecimalField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint,editable=False)
    gpx_file = models.ForeignKey(GpxFile,edit_inline=models.TABULAR,core=True,num_extra_on_change=1,num_in_admin=1)
    
    def waypoints_ordered(self):
        """all waypoints for this track in order by time"""
        return self.waypoints.select_related().order_by('localtime')
    
    def random_photos(self):
        """10 waypoints from flickr"""
        return self.waypoints.filter(photo_id__isnull=False).order_by('?')[:10]
    
    def gps_points(self):
        """Waypoints with no photo"""
        return self.waypoints.filter(photo_id__isnull=True).order_by('localtime')
    
    def geotag_photo(self, xml_photo):
        """find the location of this photo using existing waypoints"""
        photo_dt = datetime.strptime(xml_photo['datetaken'], '%Y-%m-%d %H:%M:%S')
        prev_wp = None
        prev_photo = None
        found = False
        for w in self.waypoints.all():
            # Do we have a waypoint to compare with?
            
            if prev_wp:
                # If this photo is taken between the two waypoints in the loop
                if prev_wp.localtime < photo_dt and w.localtime > photo_dt:
                
                    
                    # get the timedelata between the waypoints
                    td = w.localtime - prev_wp.localtime
                    total_difference = td.seconds
                    
                    # calculate the timedelta between the first waypoint and the phot being taken
                    td = photo_dt - prev_wp.localtime
                    photo_difference = td.seconds
                    
                    # create a factor that plots the point between the two waypoint timings the photo was taken
                    dfactor = photo_difference / float(total_difference)
                    
                    # multiply the difference between the lat/lon/alt of the waypoins by this factor
                    photo_lat = float(prev_wp.latitude) + ((float(w.latitude) - float(prev_wp.latitude)) * dfactor)
                    photo_lon = float(prev_wp.longitude) + ((float(w.longitude) - float(prev_wp.longitude)) * dfactor)
                    photo_alt = float(prev_wp.altitude) + ((float(w.altitude) - float(prev_wp.altitude)) * dfactor)
                    
                    # Prepare a waypoint object to store the results of the geotagging calculations
                    
                    photo_waypoint, created = WayPoint.objects.get_or_create(
                            latitude=photo_lat,
                            longitude=photo_lon,
                            altitude=photo_alt,
                            gmtime=photo_dt,
                            localtime=photo_dt,
                            photo_id=xml_photo['id'],
                            photo_title=xml_photo['title'],
                            photo_description='hmm',
                            photo_secret=xml_photo['secret'],
                            photo_farm=xml_photo['farm'],
                            photo_server=xml_photo['server'],
                        );
                    photo_waypoint.save()
                    #except:
                     #   assert False, '.' + xml_photo['id'] + '.'
                    return photo_waypoint
            
            prev_wp = w
        
        return False
    
    def get_photos(self, flickr_user="38584744@N00"):
        
        flickr = flickrapi.FlickrAPI(FLICKR_KEY)
        result = flickr.photos_search(user_id=flickr_user, max_taken_date=self.end_time, min_taken_date=self.start_time,extras='date_taken')
                            
        geophotos = []

        if int(result.photos[0]["total"]) > 0:
            for ph in result.photos[0].photo:
                gp = self.geotag_photo(ph)
                if gp:
                    geophotos.append(gp)
                    self.waypoints.add(gp)
                    
        return geophotos
            
    
                
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
        self.get_photos()
    
    class Admin:
        pass

class Trip(models.Model):
    def __unicode__(self):
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


    
