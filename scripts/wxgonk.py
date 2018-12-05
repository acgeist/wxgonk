#!/usr/bin/env python3
# wxgonk.py

# TODO:
# -turn all print statements into a debug string, then generate html
#  using yattag.  Html debugging page should include links to metars,
#  tafs, fields, and a google map, and should have a whole report of
#  all testing that has been done.  In the end this should be used
#  to present the data (i.e. build the display table). For troubleshooting
#  purposes, can also turn this into an AFI 11-202v3 tutorial.
# -Include an option for using USAF rules vice FAA rules.  Under FAA rules,
#  we can just classify everything as VFR, MVFR, IFR, LIFR.
# -keep a running list of countries with bad weather to make subsequent
#  searches (on the same day) faster. Specifically, once we've queried
#  a country and there aren't even any fields found, we shouldn't search
#  that country again.  However, it should still remain available in the 
#  list of countries.

import countries
import latlongcalcs
import mapurlmaker
import wxurlmaker

import datetime
import logging
import random
import re 
import requests
import sys
import urllib.request
import webbrowser
from typing import List

# reference http://www.diveintopython3.net/your-first-python-program.html
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

FILING_MINS = {'vis': 1.5, 'ceiling': 500}
ALT_REQ = {'vis': 3.0, 'ceiling': 2000}
ALT_MINS = {'vis': 2.0, 'ceiling': 1000}
NO_CEIL_VAL = 99999
COUNTRY_DICT = countries.make_country_dict()
TEST_FIELDS = []

class InvalidFunctionInput(Exception):
    pass
class InvalidDataType(Exception):
    pass

def getRoot(url:str):
    return etree.fromstring(urllib.request.urlopen(url).read())
    
def can_file_metar(metar_node, field:str) -> bool:
    '''Return filing legality based on current conditions'''
    vis_at_dest = float(metar_node.findall('.//*[station_id="' + DEST_ID 
        + '"]/visibility_statute_mi')[0].text)
    print('In function "can_file_metar" the visibility at ' + DEST_ID + ' is ' 
            + '{:.1f}'.format(vis_at_dest) + 'sm, which is ', end='')
    if vis_at_dest >= FILING_MINS['vis']:
        print('greater than or equal to ', end='')
    else:
        print('less than ', end='')
    # Reference: https://mkaz.blog/code/python-string-format-cookbook/
    print('FILING_MINS["vis"] (' + '{:.1f}'.format(FILING_MINS['vis']) + 'sm)')
    return vis_at_dest > FILING_MINS['vis'] 

def has_ceiling(node) -> bool:
    '''Return whether or not node contains a BKN/OVC/OVX line'''
    layers = list(filter(lambda layer: 
        layer.get('sky_cover') in ['BKN', 'OVC', 'OVX'], node)) 
    return False if len(layers) == 0 else True

def get_ceiling(node) -> int:
    '''Return the ceiling in feet AGL, or 9999 if no ceiling exists'''
    if not has_ceiling(node):
        return NO_CEIL_VAL
    else:
        layers = list(filter(lambda layer: 
            layer.get('sky_cover') in ['BKN', 'OVC', 'OVX'], node)) 
        layers = list(map(lambda layer: 
            int(layer.get('cloud_base_ft_agl')), layers))
        return min(layers)

def get_vis(node) -> str:
    return node.find('visibility_statute_mi').text

def req_alt(node) -> bool:
    '''Return whether or not an alternate is required'''
    vis_at_dest = float(node.findall('.//*[station_id="' + DEST_ID 
        + '"]/visibility_statute_mi')[0].text)
    print('In function "req_alt" the visibility at ' + DEST_ID + ' is ' 
            + '{:.1f}'.format(vis_at_dest) + 'sm, which is ', end='')
    if vis_at_dest >= ALT_REQ['vis'] :
        print('greater than or equal to ', end='')
    else:
        print('less than ', end='')
    print('ALT_REQ["vis"] (' + '{:.1f}'.format(ALT_REQ['vis']) + 'sm)')
    ceil_at_dest = get_ceiling(node)
    print('In function "req_alt" the ceiling at ' + DEST_ID + ' is '
            + '{:.0f}'.format(ceil_at_dest) + 'ft agl, which is ', end='')
    if ceil_at_dest >= ALT_REQ['ceiling']:
        print('greater than or equal to ', end='')
    else:
        print('less than ', end='')
    print('ALT_REQ["ceiling"] (' + '{:.0f}'.format(ALT_REQ['ceiling']) + 'ft)')
    return vis_at_dest < ALT_REQ['vis'] or ceil_at_dest < ALT_REQ['ceiling']

def valid_alt(node, field:str) -> bool:
    '''Return whether or not a field is a valid alternate based on wx'''
    vis_at_alt = float(node.findall('.//*[station_id="' + DEST_ID
        + '"]/visibility_statute_mi')[0].text)
    ceil_at_alt = get_ceiling(node)
    return vis_at_alt < ALT_MINS['vis'] or ceil_at_alt < ALT_MINS['ceiling']

def print_raw_metar(field:str) -> None:
    '''Print the raw metar for a given 4-letter identifier'''
    if not isinstance(field, str) or re.match(r'\b[a-zA-Z]{4}\b', field) == None:
        raise InvalidFunctionInput("Invalid input at print_raw_metar: " + field)
    if field in TEST_FIELDS:
        print(metar_root.findall('.//*[station_id="' + field.upper()
            + '"]/raw_text')[0].text)
    else:
        temp_url = wxurlmaker.make_adds_url('METAR', field.split())
        temp_root = getRoot(temp_url)
        print(
                temp_root.findall('.//raw_text')[0].text if 
                int(temp_root.find('data').attrib['num_results']) > 0 else
                'METAR for ' + field + ' not found.')

def print_node(node, indent:int = 0):
    '''Print an XML tree'''
    # TODO: include attributes
    print(indent * '\t', end='')
    print(node.tag if node.text == None else node.tag + ': ' + node.text)
    if len(node.findall('*')) > 0:
        for child in node:
            print_node(child, indent + 1)

def make_coord_list():
    '''Make a list of all field locations. Used to generate map URL.'''
    field_list = []
    for field in field_root.findall('.//Station'):
        field_list.append({
            'station_id': field.find('station_id').text,
            'name': field_root.findall('.//*.[station_id="'
                + field.find('station_id').text
                + '"]/site')[0].text,
            'lat': field.find('latitude').text,
            'lon': field.find('longitude').text})
    return field_list
        
def gen_bad_fields(country:str = '00') -> List[str]:
    is_valid_choice = False
    while not is_valid_choice:
        country_choice = ''.join(random.sample(COUNTRY_DICT.keys(),1)) if \
                country == '00' or not countries.is_valid_country(country) else \
                country
        print('Looking for bad weather in ' + country_choice + ' (' 
                + countries.country_name_from_code(country_choice) + '), ', end = ' ')
        bad_field_url = wxurlmaker.make_adds_url('country', [], country_choice)
        bad_field_root = getRoot(bad_field_url)
        bad_fields_list = [] 
        print(bad_field_root.find('data').attrib['num_results']
                + ' fields found.')
        if bad_field_root.find('data').attrib['num_results'] == 0:
            country_list.remove(country_choice)
            continue
        for field in bad_field_root.findall('.//Station'):
            bad_fields_list.append(field.find('station_id').text)
        rand_field_list = []
        # http requests start to break with >1000 fields
        for i in range(0, min(1000, len(bad_fields_list))):
            rand_field_list.append(random.choice(bad_fields_list))
        bad_metar_url = wxurlmaker.make_adds_url('METAR', stationList = rand_field_list)
        bad_metar_root = getRoot(bad_metar_url)
        bad_metars = bad_metar_root.findall('.//METAR')
        bad_metars = list(filter(lambda metar:
            not re.search('\d+', metar.find('station_id').text) and
            metar.find('visibility_statute_mi') is not None and
            float(metar.find('visibility_statute_mi').text) < ALT_REQ['vis'],
            bad_metars))
        if len(bad_metars) > 2:
            is_valid_choice = True
        else:
            print('No fields in ' + countries.country_name_from_code(country_choice) 
                    + ' currently have visibility', 
                    '< ' + str(ALT_REQ['vis']) + '. Picking another country.')
    print(str(len(bad_metars)) + ' fields in ' 
            + countries.country_name_from_code(country_choice) 
            + ' currently have visibility < ' + 
            str(ALT_REQ['vis']))
    if len(bad_metars) > 10:
        del bad_metars[10:]
    bad_field_ids = []
    for metar in bad_metars:
        bad_field_ids.append(metar.find('station_id').text)
    return bad_field_ids

def test():
    print('TEST_FIELDS = ' + ' '.join(TEST_FIELDS))
    print('Home station/destination = ' + DEST_ID, end=' ')
    home_lat = float(field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/latitude')[0].text) 
    home_lon = float(field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/longitude')[0].text) 
    print('('
        + field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/site')[0].text + '), located at lat/long: ' 
        + str(home_lat) + ', '+ str(home_lon))
    for root in roots:
        print('Received ' + root.find('data').attrib['num_results']
                + ' ' +  root.find('data_source').attrib['name'] + ': ', 
                end='')
        for id in root.findall('.//station_id'):
            print(id.text, end=' ')
        print()
    for field in field_root.findall('.//Station'):
        if not field.find('station_id').text in DEST_ID:
            print(field.find('station_id').text + '('
                    + field_root.findall('.//*.[station_id="' 
                        + field.find('station_id').text
                        + '"]/site')[0].text + ') is ' 
                    + str(round(latlongcalcs.dist_between_coords(home_lat, home_lon,
                        field.find('latitude').text, 
                        field.find('longitude').text)))
                    + ' statute miles from ' 
                    + DEST_ID)

    # https://docs.python.org/2/library.xml.etree.elementtree.html#elementtree-xpath
    metars = metar_root.findall('.//METAR')

    for metar in metars:
        print(metar.find('raw_text').text)

    print('Can I legally file to ' + DEST_ID + '?')
    print_raw_metar(DEST_ID)
    print('can_file_metar: ' + str(can_file_metar(metar_root, DEST_ID)))
    print('has_ceiling: ' + str(has_ceiling(metar_root.findall('.//*[station_id="' 
        + DEST_ID + '"]/sky_condition'))))
    print('ceiling: ' + str(get_ceiling(metar_root.findall('.//*[station_id="'
        + DEST_ID + '"]/sky_condition'))))
    print('visibility: ' + get_vis(metar_root.find('.//*[station_id="'
        + DEST_ID + '"]')))
    if can_file_metar(metar_root, DEST_ID):
        print('Do I require an alternate to file to ' + DEST_ID + '?')
        print('req_alt: ' + str(req_alt(metar_root)))


    # Times follow format YYYY-mm-ddTHH:MM:SSZ
    metar_times_list = metar_root.findall('.//METAR/observation_time')
    example_time_string = random.choice(metar_times_list).text
    print('example_time_string = ' + example_time_string)
    #TODO: do time zone stuff
    date_obj = datetime.datetime.strptime(example_time_string, \
            '%Y-%m-%dT%H:%M:%SZ')
    print('date_obj = ' + str(date_obj))

logging.basicConfig(level=logging.DEBUG, filename = 'test.log', filemode='w', \
        format='\n%(asctime)s - %(levelname)s - %(message)s')

if len(sys.argv) > 1:
    """Process command-line arguments"""
    # TODO: put some kind of limitation on number of fields that can be searched.
    logging.debug('sys.argv = ' + ' '.join(sys.argv) + '\n')
    # If there's only one argument and it is a valid two-letter country 
    # identifier, search that country for bad weather.
    if re.match(r'\b[a-zA-Z]{2}\b', sys.argv[1]) and \
            len(sys.argv) == 2 and \
            countries.is_valid_country(sys.argv[1]):
        TEST_FIELDS = gen_bad_fields(sys.argv[1])
    else:
        for arg in sys.argv[1:]:
            # Reference https://aviation.stackexchange.com/a/14593 and FAA Order 
            # JO 7350.9. We're only going 
            # to use/deal with 4-letter fields, as two-letter, two-number ids likely
            # reference private fields or fields smaller than we'll be using for 
            # military flying.
            if re.match(r'\b[a-zA-Z]{4}\b', arg) == None:
                logging.warning('The command line argument "' + arg + '" did not match '
                        + 'the pattern for a valid ICAO identifier.\n')
                break
            else:
                TEST_FIELDS.append(arg.upper())
    logging.debug('TEST_FIELDS set to ' + ', '.join(TEST_FIELDS) + '\n')
else:
    logging.debug('No command-line arguments detected. Picking random fields.\n')
    TEST_FIELDS = gen_bad_fields()
DEST_ID = TEST_FIELDS[0]
logging.debug('set DEST_ID to TEST_FIELDS[0], which is ' + TEST_FIELDS[0] + '.\n')

logging.debug('making ADDS URLs...\n')
taf_url = wxurlmaker.make_adds_url('tafs', TEST_FIELDS)    
metar_url = wxurlmaker.make_adds_url('metars', TEST_FIELDS)    
field_url = wxurlmaker.make_adds_url('fields', TEST_FIELDS)    
urls = [taf_url, metar_url, field_url]

taf_root = getRoot(taf_url)
metar_root = getRoot(metar_url)
field_root = getRoot(field_url)
roots = [taf_root, metar_root, field_root]

map_url = mapurlmaker.make_map_url(make_coord_list())
map_request = requests.get(map_url)
with open('../images/map.jpg', 'wb') as map_img:
    map_img.write(map_request.content)

file_contents_string = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
file_contents_string += '<meta charset="utf-8">\n<title>WxGonk Troubleshooting'
file_contents_string += '</title>\n</head>\n<body>\n<h1>Most recent URLs:</h1>'
file_contents_string += '\n<a href=' + metar_url + '>METARs</a></br>'
file_contents_string += '\n<a href=' + taf_url + '>TAFs</a></br>'
file_contents_string += '\n<a href=' + field_url + '>FIELDs</a></br>'
file_contents_string += '\n<a href=images/map.jpg>Google Map</a></br>'
with open('test.log', newline='\n') as f:
    for line in f:
        file_contents_string += '<p>' + line + '</p>'
file_contents_string += '</body>\n</html>'
with open('index.html', 'w') as url_file:
    url_file.write(file_contents_string)
    
# reference https://stackoverflow.com/a/419185
if __name__ == '__main__':
    pass