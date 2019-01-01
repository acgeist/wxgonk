#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# wxgonk.py

# TODO:
#  Eventually, index.html should be used
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
import usingcgi
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

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

# TODO: This should perhaps be in a "main.py" file
logging.basicConfig( \
        level=logging.DEBUG, \
        filename = '.logs/test.log', \
        filemode='w', \
        format='\n%(asctime)s - %(filename)s: line %(lineno)s, %(funcName)s: %(message)s')

FILING_MINS = {'vis': 1.5, 'ceiling': 500}
ALT_REQ = {'vis': 3.0, 'ceiling': 2000}
ALT_MINS = {'vis': 2.0, 'ceiling': 1000}
NO_CEIL_VAL = 99999
COUNTRY_DICT = countries.make_country_dict()
TEST_FIELDS = []
USING_CGI = usingcgi.called_from_cgi()

class InvalidFunctionInput(Exception):
    pass
class InvalidDataType(Exception):
    pass

def get_root(url:str):
    '''Return the root node of an xml file'''
    return etree.fromstring(urllib.request.urlopen(url).read())
    
def node_contains_field(node, field:str) -> bool:
    '''Return whether or not a particular node contains a given station'''
    # if no result is found, [] (an empty list) will be returned, which
    # is a so-called falsey value in python
    if re.match(r'\b[a-zA-Z]{4}\b', field) == None:
        return false
    return node.findall('.//*[station_id="' + field.upper() + '"]/raw_text') 
    
def can_file_metar(metar_node, field:str) -> bool:
    '''Return filing legality based on current conditions'''
    vis_at_dest = float(metar_node.findall('.//*[station_id="' + DEST_ID 
        + '"]/visibility_statute_mi')[0].text)
    debug_str = 'In function "can_file_metar" the visibility at ' + DEST_ID + ' is ' 
    debug_str += '{:.1f}'.format(vis_at_dest) + 'sm, which is '
    debug_str += '>=' if vis_at_dest >= FILING_MINS['vis'] else '<'
    debug_str += ' FILING_MINS["vis"] (' + '{:.1f}'.format(FILING_MINS['vis']) + 'sm)'
    logging.debug(debug_str)
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
    ceil_at_dest = get_ceiling(node)
    debug_str = '\nIn function "req_alt" the visibility at ' + DEST_ID + ' is '
    debug_str += '{:.1f}'.format(vis_at_dest) + 'sm, which is '
    debug_str += '>=' if vis_at_dest >= ALT_REQ['vis'] else '<'
    debug_str += ' ALT_REQ["vis"] (' + '{:.1f}'.format(ALT_REQ['vis']) + 'sm)'
    debug_str += '\nIn function "req_alt" the ceiling at ' + DEST_ID + ' is '
    debug_str += '{:.0f}'.format(ceil_at_dest) + 'ft agl, which is '
    debug_str += '>=' if ceil_at_dest >= ALT_REQ['ceiling'] else '<'
    debug_str += ' ALT_REQ["ceiling"] (' + '{:.0f}'.format(ALT_REQ['ceiling']) + 'ft)'
    logging.debug(debug_str)
    return vis_at_dest < ALT_REQ['vis'] or ceil_at_dest < ALT_REQ['ceiling']

def valid_alt(node, field:str) -> bool:
    '''Return whether or not a field is a valid alternate based on wx'''
    vis_at_alt = float(node.findall('.//*[station_id="' + DEST_ID
        + '"]/visibility_statute_mi')[0].text)
    ceil_at_alt = get_ceiling(node)
    return vis_at_alt < ALT_MINS['vis'] or ceil_at_alt < ALT_MINS['ceiling']

def get_raw_text(field:str, metar_or_taf:str) -> str:
    '''Print the raw metar or taf for a given 4-letter ICAO identifier'''
    ### INPUT VALIDATION ###
    # TODO: write a function to validate ICAO identifiers.  Should figure out
    # how to pull a list of all valid identifiers from an official database
    # and do a simple lookup.
    if not isinstance(field, str) or not isinstance(metar_or_taf, str):
        err_str = 'One of the inputs to get_raw_text was not ' + 'a string.\n'
        err_str += 'field = ' + str(field) + ', type(field) = '
        err_str += str(type(field)) + '\nmetar_or_taf = ' + str(metar_or_taf)
        err_str += ', type(metar_or_taf) = ' + str(type(metar_or_taf))
        logging.warning(err_str)
        raise InvalidFunctionInput(err_str)
    if re.match(r'\b[a-zA-Z]{4}\b', field) == None:
        err_str = 'Invalid value for field in function get_raw_text: ' + field
        logging.warning(err_str)
        raise InvalidFunctionInput(err_str)
    if not re.match(r'(METAR|TAF|BOTH)', metar_or_taf.upper()):
        err_str = 'Invalid input at get_raw_text, second argument must be '
        err_str += '"metar", "taf", or "both" (case insensitive). Received ' 
        err_str += metar_or_taf
        logging.warning(err_str)
        raise InvalidFunctionInput(err_str)
    logging.debug('get_raw_text called with parameters: field = ' + field \
            + ', metar_or_taf = ' + metar_or_taf.upper())
    ### ACTUALLY DOING THE THING ###
    result_str = ''
    if field in TEST_FIELDS: 
    #TODO: this should check if there is actually a metar or taf for the given
    # field rather than just checking if the field is in TEST_FIELDS
        temp_root = metar_root if metar_or_taf.upper() == 'METAR' else \
                taf_root
        result_str = '' if not node_contains_field(temp_root, field) else \
                temp_root.findall('.//*[station_id="' + field.upper()
                        + '"]/raw_text')[0].text
    else:
        temp_url = wxurlmaker.make_adds_url('METAR', field.split()) if \
                metar_or_taf.upper() == 'METAR' else \
                wxurlmaker.make_adds_url('TAF', field.split())
        temp_root = get_root(temp_url)
        result_str = temp_root.findall('.//raw_text')[0].text if \
                int(temp_root.find('data').attrib['num_results']) > 0 else \
                metar_or_taf.upper() + ' for ' + field + ' not found.'
    # Add newlines to make raw text TAFs easier to read
    if metar_or_taf.upper() == 'TAF' or metar_or_taf.upper() == 'BOTH':
        result_str = re.sub(r'(TAF|FM|TEMPO|BECMG)', r'\n\1', result_str)
    if metar_or_taf.upper() == 'BOTH':
        result_str = get_raw_text(field, 'METAR') + '\n' + result_str
    return result_str

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
    temp_node = {}
    for field in field_root.findall('.//Station'):
        temp_node = { 
            'station_id': field.find('station_id').text,
            'name': field_root.findall('.//*.[station_id="'
                + field.find('station_id').text
                + '"]/site')[0].text,
            'lat': field.find('latitude').text,
            'lon': field.find('longitude').text}
        # Homestation/destination needs to be first item in the list.
        # This affects the Google Map that is created later on.
        if temp_node['station_id'] == DEST_ID:
            field_list.insert(0, temp_node)
        else:
            field_list.append(temp_node)
    return field_list
        
def gen_bad_fields(country:str = '00', num_results:int = 10) -> List[str]:
    '''Generate a list of ICAO ids where the visibility is currently bad'''
    # TODO: develop some persistent data to keep track of which countries
    # rarely yield bad weather and stop choosing those as often.  Perhaps
    # weight the countries based on how many fields are there? Could also
    # consider querying every country and removing from my countries data 
    # file all countries that return 0 fields.
    is_valid_choice = False
    country_choices = list(COUNTRY_DICT.keys())
    num_countries_tried = 0 # For debugging/data gathering
    countries_tried_str = ''
    while not is_valid_choice:
        num_countries_tried += 1
        country_choice = random.choice(country_choices) if \
                not countries.is_valid_country(country) else \
                country
        countries_tried_str += country_choice + ' '
        logging.debug('Looking for bad weather in ' + country_choice + ' (' 
                + countries.country_name_from_code(country_choice) + '), ')
        bad_field_url = wxurlmaker.make_adds_url('country', [], country_choice)
        bad_field_root = get_root(bad_field_url)
        bad_fields_list = [] 
        logging.debug(bad_field_root.find('data').attrib['num_results']
                + ' fields found.')
        # if not many results were returned, we 
        # don't want to try this country again.
        if int(bad_field_root.find('data').attrib['num_results']) < 10:
            country_choices.remove(country_choice)
            continue
        for field in bad_field_root.findall('.//Station'):
            # Ensure field has TAF capability
            if field.findall('.//TAF'):
                bad_fields_list.append(field.find('station_id').text)
        rand_field_list = []
        # Based on trial/error, http requests start to break with >1000 fields
        for i in range(0, min(1000, len(bad_fields_list))):
            new_addition = random.choice(bad_fields_list)
            if not new_addition in rand_field_list:
                rand_field_list.append(new_addition)
        bad_metar_url = wxurlmaker.make_adds_url('METAR', \
                stationList = rand_field_list)
        bad_metar_root = get_root(bad_metar_url)
        bad_metars = bad_metar_root.findall('.//METAR')
        bad_metars = list(filter(lambda metar:
            not re.search('\d+', metar.find('station_id').text) and
            metar.find('visibility_statute_mi') is not None and
            float(metar.find('visibility_statute_mi').text) < ALT_REQ['vis'],
            bad_metars))
        # TODO: filter bad metars by whether or not the site itself has
        # TAF capability.  This is listed in the station xml file under
        # <Station><site_type><TAF/></site_type></Station>
        if len(bad_metars) > 2:
            is_valid_choice = True
        else:
            logging.debug('No fields in ' 
                    + countries.country_name_from_code(country_choice) 
                    + ' currently have visibility < ' 
                    + str(ALT_REQ['vis']) + '. Picking another country.')
            country_choices.remove(country_choice)
    logging.debug('Tried ' + str(num_countries_tried - 1) \
            + ' countries unsuccessfully: ' + countries_tried_str[:-3])
    logging.debug(str(len(bad_metars)) + ' fields in ' 
            + countries.country_name_from_code(country_choice) 
            + ' currently have visibility < ' + str(ALT_REQ['vis']))
    if len(bad_metars) > num_results:
        del bad_metars[num_results:]
    bad_field_ids = []
    for metar in bad_metars:
        bad_field_ids.append(metar.find('station_id').text)
    return bad_field_ids

def test():
    home_lat = float(field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/latitude')[0].text) 
    home_lon = float(field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/longitude')[0].text) 
    logging.debug('Home station/destination = ' + DEST_ID + ' ('
        + field_root.findall('.//*.[station_id="' + DEST_ID 
            + '"]/site')[0].text + '), located at lat/long: ' 
        + str(home_lat) + ', '+ str(home_lon))
    for root in roots:
        results = 'Received ' + root.find('data').attrib['num_results']
        results += ' ' +  root.find('data_source').attrib['name'] + ': '
        for id in root.findall('.//station_id'):
            results += ' ' + id.text
        logging.debug(results)
    for field in field_root.findall('.//Station'):
        if field.find('station_id').text == DEST_ID:
            continue
        field_id = field.find('station_id').text 
        logging.debug(field_id + ' (' + field_root.findall('.//*.[station_id="' 
            + field_id + '"]/site')[0].text + ') is ' 
            + str(round(latlongcalcs.dist_between_coords(home_lat, home_lon, 
                field.find('latitude').text, field.find('longitude').text))) 
            + ' nautical miles from ' + DEST_ID + ' on a heading of ' 
            + '{:03d}'.format(round(latlongcalcs.hdg_between_coords(home_lat, 
                home_lon, field.find('latitude').text, 
                field.find('longitude').text))) 
            # Use the HTML escape if called from cgi, 
            # otherwise input unicode directly.  
            + ('&deg' if USING_CGI else u'\N{DEGREE SIGN}') + ' true.')
        logging.debug('\nCurrent METAR/TAF at ' \
                + field_id + ': \n' + get_raw_text(field_id, 'both'))

    # https://docs.python.org/2/library.xml.etree.elementtree.html#elementtree-xpath
    metars = metar_root.findall('.//METAR')

    logging.debug('Can I legally file to ' + DEST_ID + '?')
    logging.debug(get_raw_text(DEST_ID, 'METAR'))
    logging.debug('can_file_metar: ' + str(can_file_metar(metar_root, DEST_ID)))
    logging.debug('has_ceiling: ' + str(has_ceiling(metar_root.findall(
        './/*[station_id="' + DEST_ID + '"]/sky_condition'))))
    logging.debug('ceiling: ' + str(get_ceiling(metar_root.findall(
        './/*[station_id="' + DEST_ID + '"]/sky_condition'))))
    logging.debug('visibility: ' + get_vis(metar_root.find(
        './/*[station_id="' + DEST_ID + '"]')))
    if can_file_metar(metar_root, DEST_ID):
        logging.debug('Do I require an alternate to file to ' + DEST_ID + '?')
        logging.debug('req_alt: ' + str(req_alt(metar_root)))

    tafs = taf_root.findall('.//TAF')

    # Times follow format YYYY-mm-ddTHH:MM:SSZ
    metar_times_list = metar_root.findall('.//METAR/observation_time')
    example_time_string = random.choice(metar_times_list).text
    logging.debug('example_time_string = ' + example_time_string)
    #TODO: do time zone stuff
    date_obj = datetime.datetime.strptime(example_time_string, \
            '%Y-%m-%dT%H:%M:%SZ')
    logging.debug('date_obj = ' + str(date_obj))

if len(sys.argv) > 1:
    """Process command-line arguments"""
    # TODO: put some kind of limitation on number of fields that can be searched.
    logging.debug('sys.argv = ["' + '", "'.join(sys.argv) + '"]\n')
    # If there's only one argument and it is a valid two-letter country 
    # identifier, search that country for bad weather.
    if re.match(r'\b[a-zA-Z]{2}\b', sys.argv[1]) and \
            len(sys.argv) == 2 and \
            countries.is_valid_country(sys.argv[1]):
        TEST_FIELDS = gen_bad_fields(sys.argv[1])
    else:
        for arg in sys.argv[1:]:
            # Reference https://aviation.stackexchange.com/a/14593 and FAA Order
            # JO 7350.9. We're only going to use/deal with 4-letter fields, as 
            # two-letter, two-number ids likely reference private fields or 
            # fields smaller than we'll be using for military flying.
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

taf_root = get_root(taf_url)
metar_root = get_root(metar_url)
field_root = get_root(field_url)
roots = [taf_root, metar_root, field_root]

map_url = mapurlmaker.make_map_url(make_coord_list())
map_request = requests.get(map_url)
with open('images/map.jpg', 'wb') as map_img:
    map_img.write(map_request.content)
   
# reference https://stackoverflow.com/a/419185
if __name__ == '__main__':
    test()
    # TODO: this should be a pre-formatted html file that I can go into 
    # and only change the content within certain tags.
    # This first line (content-type) is required for CGI to work
    html_str = ''
    if USING_CGI:
        html_str += 'Content-type: text/html; charset=UTF-8\n\n'
        html_str += '<!DOCTYPE html><html lang="en"><head>'
        html_str += '<meta charset="utf-8"><title>WxGonk Troubleshooting'
        html_str += '</title><link rel="stylesheet" type="text/css"'
        html_str += 'href="styles/wxgonk.css" />'
        html_str += '</head><body>'
    html_str += '<h1>Most recent URLs:</h1>'
    html_str += '<a href=' + metar_url + '>METAR XML</a></br>'
    html_str += '<a href=' + taf_url + '>TAF XML</a></br>'
    html_str += '<a href=' + field_url + '>FIELD XML</a></br>'
    html_str += '<a href=' + wxurlmaker.make_metar_taf_url(TEST_FIELDS)
    html_str += '>Normal TAFs & METARs</a></br>'
    html_str += '<a href=images/map.jpg>Google Static Map</a></br></br>'
    html_str += '\n'
    with open('.logs/test.log', newline='\n') as f:
        for line in f:
            html_str += '<p>' + line + '</p>'
    if USING_CGI:
        print(html_str)
    else:
        html_str += '</body>\n</html>'
        with open('index.html', 'w') as url_file:
            url_file.write(html_str)
