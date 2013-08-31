from django.conf.urls.defaults import include, patterns
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^dates/(?P<date_from>\d{8})-(?P<date_to>\d{8})/?', 'geo.views.dates'),
    # (r'^upload/?', 'geo.views.upload'),
    (r'^track/(?P<track_id>[0-9]+)/?$', 'geo.views.show_track'),
    (r'^track/(?P<track_id>[0-9]+).kml/?$', 'geo.views.kml_track'),
    (r'^getphotos/(?P<track_id>[0-9]+)/?$', 'geo.views.get_photos'),
    (r'^os-track/(?P<track_id>[0-9]+)/?$', 'geo.views.show_os_track'),
    (r'^os-route/?$', 'geo.views.os_route'),
    (r'^btracks/?$', 'geo.views.between_tracks'),
    (r'^geotag/?$', 'geo.views.geo_tag'),
    (r'^fauth/?$', 'geo.views.callback'),
    (r'^/?$', 'geo.views.home_page'),
    (r'index', 'geo.views.home_page'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
             (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
