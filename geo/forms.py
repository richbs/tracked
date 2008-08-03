from django import forms
from tracked.settings import MEDIA_ROOT
from tracked.geo.models import GpxFile
from django.forms.extras import SelectDateWidget

import os

SELECT_YEARS = (2006,2007,2008,2009)

class DateSearch(forms.Form):
    from_date = forms.DateField(widget=SelectDateWidget(years=SELECT_YEARS))
    to_date   = forms.DateField(widget=SelectDateWidget(years=SELECT_YEARS))


class UploadFormTwo(forms.ModelForm):
    class Meta:
        model = GpxFile
        fields = ('name','description','filename')
    
    def clean_filename(self):

        if 'filename' in self.cleaned_data:
            filename = self.cleaned_data['filename']
            #assert False, len(filename.get('content'))
            #assert False, len(filename.content)
            
            if not filename.filename.endswith('.gpx'):
                msg = 'Only .gpx XML files are allowed.'
                raise forms.ValidationError(msg)
            if len(filename.content) > 1049000:
                msg = 'Maximum 1mb filesize'
                raise forms.ValidationError(msg)
            return filename

class UploadForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()
    filename = forms.Field( 
        widget = forms.FileInput(attrs={'class': 'fun'})
    )
    """
    def save(self):
        xml_data = self.clean_data['filename']['content']
        xml_filename = self.clean_data['filename']['filename']
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
    """