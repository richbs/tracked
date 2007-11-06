from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^tracked2/', include('tracked2.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls'))
)
