from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^tracked2/', include('tracked2.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^dates/(?P<date_from>\d{8})-(?P<date_to>\d{8})/?', 'tracked.geo.views.dates'),
    # (r'^upload/?', 'tracked.geo.views.upload'),
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/richbs/Sites/tracked/assets/', 'show_indexes': True}),
    (r'^track/(?P<track_id>[0-9]+)/?$','tracked.geo.views.show_track'),
    (r'^/?$', 'tracked.geo.views.home_page'),
        (r'index', 'tracked.geo.views.home_page'),
)
