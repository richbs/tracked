from django.contrib import admin

from tracked.geo.models import GpxFile, Track, WayPoint, Trip

class GpxFileAdmin(admin.ModelAdmin):
    
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
    pass

admin.site.register(Track, TrackAdmin)

class TripAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trip, TripAdmin)