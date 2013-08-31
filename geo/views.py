# Create your views here.
from datetime import datetime, timedelta
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from geo.helpers import UTC
from django.template import Template, RequestContext, loader
from geo.models import WayPoint, Track, GpxFile
from geo.forms import DateSearch
from django.db import connection

ONE_DAY = timedelta(days=1)


import flickrapi
from django.conf import settings
import logging
logging.basicConfig()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def require_flickr_auth(view):
    '''View decorator, redirects users to Flickr when no valid
    authentication token is available.
    '''

    def protected_view(request, *args, **kwargs):
        if 'token' in request.session:
            token = request.session['token']
            log.info('Getting token from session: %s' % token)
        else:
            token = None
            log.info('No token in session')

        f = flickrapi.FlickrAPI(api_key=settings.FLICKR_KEY,
               secret=settings.FLICKR_SECRET, token=token,
               store_token=False)

        if token:
            # We have a token, but it might not be valid


            log.info('Verifying token')
            try:
                f.auth_checkToken()
                if f.auth_checkToken().auth[0].perms[0].text == 'read':
                    token = None
                    del request.session['token']
            except flickrapi.FlickrError:
                token = None
                del request.session['token']

        if not token:
            # No valid token, so redirect to Flickr
            log.info('Redirecting user to Flickr to get frob')
            url = f.web_login_url(perms='write')
            return HttpResponseRedirect(url)

        # If the token is valid, we can call the decorated view.
        log.info('Token is valid')

        return view(request, *args, **kwargs)

    return protected_view

def callback(request):
    log.info('We got a callback from Flickr, store the token')

    f = flickrapi.FlickrAPI(api_key=settings.FLICKR_KEY,
           secret=settings.FLICKR_SECRET, store_token=False)

    frob = request.GET['frob']
    token = f.get_token(frob)
    request.session['token'] = token

    return HttpResponseRedirect('/')

@require_flickr_auth
def content(request):
    return HttpResponse('Welcome, oh authenticated user!')

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
                return HttpResponseRedirect('/dates/%s-%s' % (from_formatted, to_formatted))
            else:
                message = "No tracks recorded in this time frame"
    else:
        d = DateSearch()
    home_tracks = Track.objects.all().order_by('-start_time')[:9]

    return render_to_response('index.html', {'tracks':home_tracks, 'search_form':d, 'message':message, 'qs': connection.queries}, context_instance=RequestContext(request))

def upload(request):
    form = None

    # Typically, we'd do a permissions check here.
    # if not request.user.has_perm('pix.add_picture'):
    #    return http.HttpResponseForbidden('You cannot add pictures.')

    if request.POST:

        form = UploadFormTwo(request.POST, request.FILES)

        if form.is_valid():
            g = form.save()
            g.processXML()
            g.createTracks(60, 3500, 1)
            return HttpResponse('yes')
        else:

            return render_to_response('upload.html', {'form':form})
    else:
        form = UploadFormTwo()
        return render_to_response('upload.html', {'form':form})

@require_flickr_auth
def get_photos(request, track_id):

    track = Track.objects.select_related().get(id=track_id)
    mins_offset = 0
    if 'offset' in request.GET:
        mins_offset = int(request.GET['offset'])
    print track.get_photos(offset_minutes=mins_offset, token=request.session['token'])
    prev = None
    next = None
    found_prev = False
    found_next = False

    alltracks = track.gpx_file.track_set.all().order_by('start_time')

    for tr in alltracks:
        if tr.start_time == track.start_time:
            found_prev = prev
        if prev:
            if prev.start_time == track.start_time:
                found_next = tr
        prev = tr

    first_current = track.waypoints.all().order_by('localtime')[0]
    last_current = track.waypoints.all().order_by('-localtime')[0]

    if found_prev:
        last_old = found_prev.waypoints.all().order_by('-localtime')[0]
        print last_old, first_current
    if found_next:
        first_next = found_next.waypoints.all().order_by('localtime')[0]
        print last_current, first_next
    # geophotos = track.get_photos()
    # gpxfile = track.gpx_file
    # assert False, track.random_photos()
    return render_to_response('track.html', {'track':track}, context_instance=RequestContext(request))

def kml_track(request, track_id):
    track = Track.objects.select_related().get(id=track_id)
    return render_to_response('kml_track.xml', {'track':track}, context_instance=RequestContext(request))

def show_track(request, track_id):

    track = Track.objects.select_related().get(id=track_id)

    if 'offset' in request.GET:
        mins_offset = int(request.GET['offset'])
        track.get_photos(offset_minutes=mins_offset)

        # print last_old, first_current, last_current, first_next
    # geophotos = track.get_photos()
    # gpxfile = track.gpx_file
    # assert False, track.random_photos(
    track_minutes = (track.end_time - track.start_time).seconds / 60.0
    pace = track_minutes / float(track.length)
    speed = float(track.length) / (track_minutes / 60.0)

    intensity = speed * 0.0277
    calories = intensity * track_minutes * 76
    track_context = {'track':track, 'pace':pace, 'speed':speed, 'calories':calories, 'track_minutes':track_minutes}
    return render_to_response('track.html', track_context, context_instance=RequestContext(request))

def show_os_track(request, track_id):
    track = Track.objects.select_related().get(id=track_id)
    # geophotos = track.get_photos()
    # gpxfile = track.gpx_file
    # assert False, track.random_photos()

    return render_to_response('os_track.html', {'track':track}, context_instance=RequestContext(request))

def os_route(request):
    # geophotos = track.get_photos()
    # gpxfile = track.gpx_file
    # assert False, track.random_photos()

    return render_to_response('os_route.html', context_instance=RequestContext(request))

def between_tracks(request):

    if 'file_id' in request.GET:
        if 'offset' in request.GET:
            mins_offset = int(request.GET['offset'])
        else:
            mins_offset = 0

        offset_td = timedelta(seconds=int(mins_offset) * 60)
        token = None
        gpx = GpxFile.objects.get(id=request.GET['file_id'])
        trx = gpx.track_set.all().order_by('start_time')

        prev = None

        for t in trx:

            if prev:
                last_old = prev.waypoints.all().order_by('-localtime')[0]
                first_new = t.waypoints.all().order_by('localtime')[0]

                flickr = flickrapi.FlickrAPI(api_key=settings.FLICKR_KEY, secret=settings.FLICKR_SECRET, token=token)
                result = flickr.photos_search(user_id=settings.FLICKR_USER, max_taken_date=first_new.localtime + offset_td, min_taken_date=last_old.localtime + offset_td, extras='date_taken')

                geophotos = []
                print last_old, first_new, result.photos[0]["total"]
                if int(result.photos[0]["total"]) > 0:
                    for ph in result.photos[0].photo:
                        print ph['title']
            prev = t
    return HttpResponse(gpx)

@require_flickr_auth
def geo_tag(request):

    if 'track_id' in request.POST:
        track = Track.objects.select_related().get(id=request.POST['track_id'])

        fps = track.photos()
        flickr = flickrapi.FlickrAPI(api_key=settings.FLICKR_KEY, secret=settings.FLICKR_SECRET, token=request.session['token'])

        for pho in fps:
            print 'Tagging: ' + str(pho.photo_title)
            print flickr.photos_geo_setLocation(api_key=settings.FLICKR_KEY, photo_id=pho.photo_id, lat=pho.latitude, lon=pho.longitude)

        return HttpResponseRedirect('/track/' + str(track.id))
    else:
        return HttpResponseRedirect('/')

def dates(request, date_from, date_to):

    t = loader.get_template('dates.html')
    df = datetime.strptime(date_from, '%Y%m%d')
    dt = datetime.strptime(date_to, '%Y%m%d')
    dt = dt + ONE_DAY
    tracks = Track.objects.filter(start_time__gte=df, end_time__lte=dt).order_by('start_time')

    track = tracks[0];

    c = RequestContext(request, {
        'date_from':df,
        'date_to':dt,
        'track':track,
        'tracks': tracks,
        'waypoints': track.waypoints.order_by('localtime'),

    })
    return HttpResponse(t.render(c))

