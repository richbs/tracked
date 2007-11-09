from django.db import models


# Create your models here.
class WayPoint(models.Model):
    """(WayPoint description)"""
    
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
        
        
class Trip(models.Model):
    """(Trip description)"""
    name        = models.CharField( maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    length = models.FloatField(max_digits=10, decimal_places=5)

    class Admin:
        pass

    def __str__(self):
        return "Trip"

class Track(models.Model):
    """(Track description)"""
    name        = models.CharField( maxlength=100)
    description = models.CharField(blank=True, maxlength=255)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    length = models.FloatField(max_digits=10, decimal_places=5)
    waypoints   = models.ManyToManyField(WayPoint)
    class Admin:
        pass
        
    def __str__(self):
        return "Track"

