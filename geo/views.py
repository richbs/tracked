# Create your views here.
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import Template, Context, loader
from tracked.geo.models import WayPoint, Track
import math
def dates(request,date_from,date_to):

    t = loader.get_template('dates.html')
    df = datetime.strptime(date_from, '%Y%m%d')
    oneday = timedelta(days=1)
    dt = datetime.strptime(date_to, '%Y%m%d')
    dt = dt + oneday
    waypoints = WayPoint.objects.filter(time__gte=df).filter(time__lte=dt).order_by('time')
    
    min_interval    = 60
    max_interval    = 3500
    min_length      = 1
    distance        = 0
    previous        = False
    tracks = []
    track = Track()
    track.length = 0
    track.start_time = df
    track.end_time = dt
    track.name = ''
    track.description = ''
    track.save()
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
                    tracks.append(track)

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
        tracks.append(track)                

    c = Context({
        'tracks': tracks,
        'track': tracks[1]
    })
    return HttpResponse(t.render(c))
    
    
def get_distance( wp1, wp2):
        '''Returns the distance between two points on the earth.

        Inputs used are:
            Longitude (in radians) of the first location,
            Latitude (in radians) of the first location,
            Longitude (in radians) of the second location, and
            Latitude (in radians) of the second location.
        To convert to radians (from degrees), use pythons math.radian function (Note: already done 
        for you in the constructor above).  Returns the distance in miles.'''

        long_1 = math.radians(float(wp1.longitude))
        lat_1  = math.radians(float(wp1.latitude))

        long_2 = math.radians(float(wp2.longitude))
        lat_2  = math.radians(float(wp2.latitude))

        dlong = long_2 - long_1
        dlat = lat_2 - lat_1
        a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
        c = 2 * math.asin(min(1, math.sqrt(a)))
        dist = 3956 * c
        return round( dist, 5)