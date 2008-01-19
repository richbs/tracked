# Create your views here.
from datetime import datetime, timedelta
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response
from tracked.geo.helpers import UTC
from django.template import Template, Context, loader
from tracked.geo.models import WayPoint, Track, GpxFile
from tracked.geo.forms import UploadForm, UploadFormTwo


def home_page(request):
    pass

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
    
    gpxfile = track.gpx_file
    wps = track.waypoints.order_by('localtime')
    return render_to_response('track.html', {'track':track, 'gpxfile':gpxfile, 'waypoints':wps}
    
    )

def dates(request,date_from,date_to):

    t = loader.get_template('dates.html')
    df = datetime.strptime(date_from, '%Y%m%d')
    oneday = timedelta(days=1)
    dt = datetime.strptime(date_to, '%Y%m%d')
    dt = dt + oneday
    tracks = Track.objects.filter(start_time__gte=df, end_time__lte=dt).order_by('start_time')            

    c = Context({
        'tracks': tracks,
        'track': tracks[1]
    })
    return HttpResponse(t.render(c))
    
