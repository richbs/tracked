from django.conf.urls.defaults import *
from tracked import settings
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^dates/(?P<date_from>\d{8})-(?P<date_to>\d{8})/?', 'tracked.geo.views.dates'),
    # (r'^upload/?', 'tracked.geo.views.upload'),
    (r'^track/(?P<track_id>[0-9]+)/?$','tracked.geo.views.show_track'),
    (r'^track/(?P<track_id>[0-9]+).kml/?$','tracked.geo.views.kml_track'),    
    (r'^getphotos/(?P<track_id>[0-9]+)/?$','tracked.geo.views.get_photos'),    
    (r'^os-track/(?P<track_id>[0-9]+)/?$','tracked.geo.views.show_os_track'),
    (r'^os-route/?$','tracked.geo.views.os_route'),    
    (r'^btracks/?$','tracked.geo.views.between_tracks'),
    (r'^geotag/?$','tracked.geo.views.geo_tag'),
    (r'^fauth/?$','tracked.geo.views.callback'),    
    (r'^/?$', 'tracked.geo.views.home_page'),
    (r'index', 'tracked.geo.views.home_page'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
             (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )