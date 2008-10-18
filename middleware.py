from cStringIO import StringIO
import zipfile

class GEMiddleware(object):
    """
    Middleware for serving KML data or converting it to KMZ.
    """
    def process_response(self, request, response):
        if request.path.find('.kml') > -1:
            response['Content-Type']        = 'application/vnd.google-earth.kml+xml'
            response['Content-Disposition'] = 'attachment; filename=track.kml'
            response['Content-Description'] = 'A track from GPS Device'
            response['Content-Length']      = str(len(response.content))
            
        return response