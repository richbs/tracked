from django.db import models


# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    

    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __str__(self):
        return "WayPoint"


class GpxFile(models.Model):
    """
    The record of the XML file uploaded.
    Linked to some waypoints
    """
    class Admin:
        """docstring for Admin"""
        pass
            
    name = models.CharField(blank=True, maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    filename = models.FileField(upload_to='xml')
    waypoints = models.ManyToManyField(WayPoint)



class Trip(models.Model):
    """(Trip description)"""

    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __str__(self):
        return "Trip"

class Track(models.Model):
    """(Track description)"""


    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __str__(self):
        return "Track"

