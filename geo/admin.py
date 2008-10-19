from django.contrib import admin
from django import forms
from tracked.geo.models import GpxFile, Track, WayPoint, Trip


class GpxFileAdminForm(forms.ModelForm):
    class Meta:
        model = GpxFile
    
    def clean_filename(self):
        if not self.cleaned_data['filename'].name.endswith('.gpx'):
            raise forms.ValidationError('filename must end with .gpx')
        
        if self.cleaned_data['filename'].size > 1300000:
            raise forms.ValidationError('%s is too large.' % self.cleaned_data['filename'])
        
        return self.cleaned_data['filename']
        


class GpxFileAdmin(admin.ModelAdmin):
    
    form = GpxFileAdminForm
    
    fieldsets = (
        (None, {
            'fields':('name','description','filename')
        }),
    )
    
admin.site.register(GpxFile, GpxFileAdmin)


class WayPointAdmin(admin.ModelAdmin):
    
    pass

admin.site.register(WayPoint, WayPointAdmin)

class TrackAdmin(admin.ModelAdmin):
    
    date_hierarchy = 'start_time'
    list_display = ('name', 'start_time','length',)
    ordering = ['-start_time',]
admin.site.register(Track, TrackAdmin)

class TripAdmin(admin.ModelAdmin):
    
    date_hierarchy = 'start_time'
    filter_horizontal = ('tracks',)
    list_display = ('name', 'start_time','length',)
    ordering = ['-start_time',]
admin.site.register(Trip, TripAdmin)