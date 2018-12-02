#!/usr/bin/env python3
# map_points.py

from typing import Dict

def make_url(points:Dict[str, float])->str:
    '''
    Make a URL for a set of points.  
    Points should be a dictionary in the form:
    some_point = {'lat': 41.98, 'lon': -87.67}
    '''
    # https://developers.google.com/maps/documentation/maps-static/intro
    map_url = 'https://maps.googleapis.com/maps/api/staticmap?'
    return map_url

# TODO:
'''
-make home station a different color from alternates
-make map scale to fit all fields in the same picture
-pull key from a text file, ensure that text file is in .gitignore
-add text labels to fields
-create webpage with full debugging report (log in html format).
-use yattag? References:
    https://anh.cs.luc.edu/python/hands-on/3.1/handsonHtml/webtemplates.html
    http://www.yattag.org
'''
