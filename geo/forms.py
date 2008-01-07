from django import newforms as forms
from tracked.settings import MEDIA_ROOT
from tracked.geo.models import GpxFile
import os


class UploadForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()
    gpx_file = forms.Field( 
        widget = forms.FileInput(attrs={'class': 'fun'})
    )
    def clean_gpx_file(self):
        
        if 'gpx_file' in self.clean_data:
            gpx_file = self.clean_data['gpx_file']
            #assert False, len(gpx_file.get('content'))
            #assert False, gpx_file.get('content-type')
            if not gpx_file.get('filename').endswith('.gpx'):
                msg = 'Only .gpx XML files are allowed.'
                raise forms.ValidationError(msg)
            if len(gpx_file.get('content')) > 1049000:
                msg = 'Maximum 1mb filesize'
                raise forms.ValidationError(msg)
            return gpx_file
            
    def save(self):
        xml_data = self.clean_data['gpx_file']['content']
        xml_filename = self.clean_data['gpx_file']['filename']
        f = open(MEDIA_ROOT + '/xml/' + xml_filename, 'w')
        f.write(xml_data)
        f.close()
        # create GPX file object
        g = GpxFile()
        g.name = self.clean_data['name']
        g.description = self.clean_data['description']
        g.filename =  'xml/' + xml_filename
        g.save()        
        g.processXML()
        g.createTracks(60,3500,1)
        return True