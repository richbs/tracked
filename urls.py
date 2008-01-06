from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^tracked2/', include('tracked2.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^dates/(?P<date_from>\d{8})-(?P<date_to>\d{8})/?', 'tracked.geo.views.dates'),
    (r'^upload/?', 'tracked.geo.views.upload'),
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/richbs/Sites/tracked/assets/', 'show_indexes': True})
)
