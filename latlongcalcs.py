#!/usr/bin/python3
#-*- coding: utf-8 -*-
# latlongcalcs.py
"""Do stuff with coordinates.

Still learning about docstrings, lookup 
https://www.python.org/dev/peps/pep-0257/
"""

import logging
import math

def hav(angle:float) -> float:
    """Return the haversine of an angle (input in radians)"""
    try:
        float(angle)
    except TypeError:
        raise Exception("Input to hav must be numeric, received " + angle)
    else:
        return math.sin(angle/2)**2

def dist_between_coords(lat1, long1, lat2, long2, units:str = 'nm') -> float:
    """Use Haversine formula to calculate dist. in nm between two points"""
    # *treats the earth as a sphere, so some inherent inaccuracy.
    # Close enough for government work though.
    # TODO: write test cases!
    # TODO: include capability to use different units
    # TODO: add error handling/input validation
    r = 3959.0   # Radius of the earth in statute miles 
    r *= 0.868976 # conversion from sm to nm
    lat1 = math.radians(float(lat1))
    long1 = math.radians(float(long1))
    lat2 = math.radians(float(lat2))
    long2 = math.radians(float(long2))
    # Reference https://en.wikipedia.org/wiki/Haversine_formula
    return 2 * r * math.asin(math.sqrt(hav(lat2 - lat1) + math.cos(lat1) \
        * math.cos(lat2) * hav(long2 - long1)))

def hdg_between_coords(lat1, long1, lat2, long2) -> float:
    # Reference: https://www.movable-type.co.uk/scripts/latlong.html
    # TODO: change the output so it spits out a cardinal/subcardinal
    # TODO: input validation
    """Return heading (true) from point 1 to point 2"""
    debug_str = 'hdg_between_coords(lat1 = ' + str(lat1) \
            + ', long1 = ' + str(long1) + ', lat2 = ' + str(lat2) \
            + ', long2 = ' + str(long2) + ') returns '
    lat1 = math.radians(float(lat1))
    long1 = math.radians(float(long1))
    lat2 = math.radians(float(lat2))
    long2 = math.radians(float(long2))
    d_long = long2 - long1
    x = math.cos(lat2) * math.sin(d_long)
    y = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(d_long)
    return_val = math.degrees(math.atan2(x, y))
    return_val %= 360
    debug_str += '{:.1f}'.format(return_val) + 'nm.'
    logging.debug(debug_str)
    return return_val

def card_from_hdg(hdg:float) -> str:
    hdg %= 360
    if hdg >= 337.5 or hdg < 22.5:
        return 'N'
    elif hdg >= 22.5 and hdg < 67.5:
        return 'NE'
    elif hdg >= 67.5 and hdg < 112.5:
        return 'E'
    elif hdg >= 112.5 and hdg < 157.5:
        return 'SE'
    elif hdg >= 157.5 and hdg < 202.5:
        return 'S'
    elif hdg >= 202.5 and hdg < 247.5:
        return 'SW'
    elif hdg >= 247.5 and hdg < 292.5:
        return 'W'
    elif hdg >= 292.5 and hdg < 337.5:
        return 'NW'
    else:
        raise Exception("Invalid input or impossible case reached")
        return 'ERROR'
