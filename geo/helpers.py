import math
from django.utils.tzinfo import FixedOffset
from geopy.distance import GreatCircleDistance as Distance
#from geopy.distance import VincentyDistance as Distance

UTC = FixedOffset(0)

def get_distance( wp1, wp2):
    # TODO: fix math error
    print wp1,wp2
    return Distance((wp1.latitude, wp1.longitude,),(wp2.latitude,wp2.longitude,)).miles
    
 

#def get_distance( wp1, wp2):
#    '''Returns the distance between two points on the earth.
#
#    Inputs used are:
#        Longitude (in radians) of the first location,
#        Latitude (in radians) of the first location,
#        Longitude (in radians) of the second location, and
#        Latitude (in radians) of the second location.
#    To convert to radians (from degrees), use pythons math.radian function (Note: already done 
#    for you in the constructor above).  Returns the distance in miles.'''
#
#    long_1 = math.radians(float(wp1.longitude))
#    lat_1  = math.radians(float(wp1.latitude))
#
#    long_2 = math.radians(float(wp2.longitude))
#    lat_2  = math.radians(float(wp2.latitude))
#
#    dlong = long_2 - long_1
#    dlat = lat_2 - lat_1
#    a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
#    c = 2 * math.asin(min(1, math.sqrt(a)))
#    dist = 3956 * c
#    return dist
