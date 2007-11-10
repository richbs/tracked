from django.db import models

# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    latitude = models.FloatField(max_digits=12, decimal_places=9)
    longitude = models.FloatField(max_digits=12, decimal_places=9)
    altitude = models.FloatField(max_digits=10, decimal_places=6)
    time = models.DateTimeField()
    
    class Admin:
        pass

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
            
    name        = models.CharField(blank=True, maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    filename    = models.FileField(upload_to='xml')
    waypoints   = models.ManyToManyField(WayPoint)

    def process():
        """
        Convert XML points to WayPoint modes
        """
        pass

class Track(models.Model):
    """(Track description)"""
    def __str__(self):
        return "Track"

    name        = models.CharField( maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    length = models.FloatField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint)

    class Admin:
        pass

class Trip(models.Model):
    def __str__(self):
        return "Trip"
        
    """(Trip description)"""
    name        = models.CharField( maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    length = models.FloatField(max_digits=10, decimal_places=5)
    tracks = models.ManyToManyField(Track)
    
    class Admin:
        pass



    