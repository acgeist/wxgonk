# coord_man.py

import math

def hav(angle):
    """Return the haversine of an angle (input in radians)"""
    return math.sin(angle/2)**2

def dist_between_coords(lat1, long1, lat2, long2):
    """Use the Haversine formula to calculate distance between two points"""
    # TODO: write test cases!
    r = 3959.0   # Radius of the earth in statute miles 
    lat1 = math.radians(float(lat1))
    long1 = math.radians(float(long1))
    lat2 = math.radians(float(lat2))
    long2 = math.radians(float(long2))
    # Reference https://en.wikipedia.org/wiki/Haversine_formula
    return 2 * r * math.asin(math.sqrt(hav(lat2 - lat1) + math.cos(lat1) \
        * math.cos(lat2) * hav(long2 - long1)))
