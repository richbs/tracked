
def gmap_key_processor(request):
    from django.conf import settings
    return {'GMAP_KEY': settings.GOOGLE_MAPS_KEY }

def ip_address_processor(request):
    return {'ip_address': request.META['REMOTE_ADDR']}