#!/usr/bin/env python3
# map_points.py

from typing import Dict
from typing import List

def make_map_url(points:List[Dict[str, float]], country:str = 'us')->str:
    '''
    Make a URL for a set of points.  
    Points should be a dictionary in the form:
    some_point = {'lat': 41.98, 'lon': -87.67}
    '''
    # https://developers.google.com/maps/documentation/maps-static/intro
    map_url = 'https://maps.googleapis.com/maps/api/staticmap?'
    # with no center and zoom parameters, Maps Static API automatically 
    # constructs an image which contains the supplied markers.
    # map_url += 'center=40.7,-74.1'
    # map_url ++ 'zoom=5' # Zoom 1 = World, 5 = landmass/continent, 10 = city
    map_url += 'size=500x500' #max is 512x512 or 1024x1024 if scale set to 2
    map_url += '&scale=2' # [1|2] (2 = same image, twice as many pixels.)
    map_url += '&format=jpg' # [png8|png|png32|gif|jpg|jpg-baseline]
    map_url += '&maptype=satellite' # [roadmap|satellite|terrain|hybrid]
    if len(points) > 0:
        # '%7C' is the escape sequence for a pipe (i.e., |)
        map_url += '&markers=size:mid%7Ccolor:blue%7C'
        # homestation marker
        map_url += str(points[0]['lat']) + ',' + str(points[0]['lon'])
    if len(points) > 1:
        map_url += '&markers=size:tiny%7Ccolor:red' # alternates markers
        for point in points[1:]:
            map_url += '%7C' + str(point['lat']) + ',' + str(point['lon'])
    map_url += '&language=eng'
    map_url += '&region=' + country
    map_url += '&key='
    # Store key separately so it's not hard-coded in.
    with open('google_map_key.txt') as f:
        map_url += f.readline().strip()
    return map_url
