# Create your views here.
from datetime import datetime, timedelta
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response
from tracked.geo.helpers import UTC
from django.template import Template, Context, loader
from tracked.geo.models import WayPoint, Track, GpxFile
from tracked.geo.forms import UploadForm, UploadFormTwo

def upload(request):
    form = None

    # Typically, we'd do a permissions check here.
    #if not request.user.has_perm('pix.add_picture'):
    #    return http.HttpResponseForbidden('You cannot add pictures.')

    if request.POST:

        form = UploadFormTwo(request.POST,request.FILES)

        if form.is_valid():
            g = form.save()
            g.processXML()
            g.createTracks(60,3500,1)
            return HttpResponse('yes')
        else:

            return render_to_response('upload.html', {'form':form})
    else:
        form = UploadFormTwo()
        return render_to_response('upload.html', {'form':form})
    
def show_track(request, track_id):
    track   = Track.objects.get(id=track_id)
    # track.get_photos()
    
    gpxfile = track.gpxfile_set.all()[0]
    wps = track.waypoints.order_by('localtime')
    return render_to_response('track.html', {'track':track, 'gpxfile':gpxfile, 'waypoints':wps}
    
    )

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
    
