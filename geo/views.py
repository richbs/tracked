# Create your views here.
from datetime import datetime, timedelta
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from tracked.geo.helpers import UTC
from django.template import Template, RequestContext, loader
from tracked.geo.models import WayPoint, Track, GpxFile
from tracked.geo.forms import DateSearch
from django.db import connection

ONE_DAY = timedelta(days=1)

def home_page(request):
    
    message = None
    
    # do we have a search?
    if 'from_date_year' in request.GET:
        d = DateSearch(request.GET)
        if d.is_valid():
            df = d.cleaned_data['from_date']
            dt = d.cleaned_data['to_date']
            tracks = Track.objects.filter(start_time__gte=df, end_time__lte=dt).order_by('start_time')
            if len(tracks) > 0:
                from_formatted = d.cleaned_data['from_date'].strftime('%Y%m%d')
                to_formatted = d.cleaned_data['to_date'].strftime('%Y%m%d')
                return HttpResponseRedirect('/dates/%s-%s'% (from_formatted,to_formatted))
            else:
                message = "No tracks recorded in this time frame"
    else:
        d = DateSearch()
    home_tracks = Track.objects.all().order_by('-start_time')[:9]

    return render_to_response('index.html', {'tracks':home_tracks, 'search_form':d, 'message':message,'qs': connection.queries}, context_instance=RequestContext(request))

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
    track = Track.objects.select_related().get(id=track_id)
    #geophotos = track.get_photos()
    #gpxfile = track.gpx_file
    return render_to_response('track.html', {'track':track, 'qs':connection.queries, 'GOOGLE_MAPS_KEY':GOOGLE_MAPS_KEY})


def dates(request,date_from,date_to):

    t = loader.get_template('dates.html')
    df = datetime.strptime(date_from, '%Y%m%d')
    dt = datetime.strptime(date_to, '%Y%m%d')
    dt = dt + ONE_DAY
    tracks = Track.objects.filter(start_time__gte=df, end_time__lte=dt).order_by('start_time')
    track = tracks[0];
    c = Context({
        'date_from':df,
        'date_to':dt,        
        'track':track,
        'tracks': tracks,
        'waypoints': track.waypoints.order_by('localtime'),
        
    })
    return HttpResponse(t.render(c))
    
