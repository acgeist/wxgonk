#!/usr/bin/env python3
# wxgonk.py

import coord_man

<<<<<<< HEAD
import random
=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
import re 
import sys
import urllib.request
import webbrowser
<<<<<<< HEAD
from typing import List
=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
# reference http://www.diveintopython3.net/your-first-python-program.html
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

<<<<<<< HEAD
# TEST_FIELDS = 'KSEA RKSO KVAD KDMA'.split()
# DEST_ID = TEST_FIELDS[0]
FILING_MINS = {'vis': 1.5, 'ceiling': 500}
=======
TEST_FIELDS = 'KSEA RKSO RPLC LBPG EEEI'.split()
DEST_ID = TEST_FIELDS[0]
FILING_MINS = {'vis': 5.0, 'ceiling': 500}
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
ALT_REQ = {'vis': 3.0, 'ceiling': 2000}
ALT_MINS = {'vis': 2.0, 'ceiling': 1000}
NO_CEIL_VAL = 9999
timeRegex = ''

<<<<<<< HEAD
def makeUrl(dataType:str, stationList:List[str], country:str = 'de') -> str:
    '''Make the URL for each dataset'''
    dataType_valid = False
    if not isinstance(dataType, str):
        raise InvalidFunctionInput("Data type must be a string")
    if not dataType.upper() in ['TAFS', 'TAF', 'METAR', 'METARS', 'FIELD', 'FIELDS',
            'COUNTRY']:
        raise InvalidFunctionInput("Data type must be 'TAFS', 'TAF', " 
        + "'METAR', 'METARS', 'FIELD', 'FIELDS', or COUNTRY")
    if not re.search('[a-z]{2}', country):
        raise InvalidFunctionInput("country must be a 2-letter abbreviation " + 
                "in accordance with ISO-3166-1 ALPHA-2. Reference " + 
                "https://laendercode.net/en/2-letter-list.html")
=======
def makeUrl(dataType:str, stationList) -> str:
    '''Make the URL for each dataset'''
    dataType_valid = False
    if dataType.upper() in ['TAFS', 'TAF', 'METAR', 'METARS', 'FIELD', 'FIELDS']:
        dataType_valid = True
    if not dataType_valid:
        raise InvalidDataType("Data type must be 'TAFS', 'TAF', " 
        + "'METAR', 'METARS', 'FIELD', or 'FIELDS'")
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
    url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?'
    url += 'requestType=retrieve'
    url += '&format=xml'
    if dataType.upper() in ['TAFS', 'TAF']:
        url += '&dataSource=tafs'
        url += '&hoursBeforeNow=24'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['METAR', 'METARS']:
        url += '&dataSource=metars'
<<<<<<< HEAD
        # Don't use METAR if unable to get one newer than 3 hours
=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
        url += '&hoursBeforeNow=3'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['FIELDS', 'FIELD']:
        url += '&dataSource=stations'
<<<<<<< HEAD
    elif dataType.upper() in ['COUNTRY']:
        url += '&dataSource=stations'
        # TODO: error checking to make sure country is a valid 2-letter code
        url += '&stationString=~' + country
        return url
=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
    else:
        return 'https://www.aviationweather.gov/adds/dataserver_current'
    url += '&stationString='
    url += '%20'.join(stationList)
    return url

<<<<<<< HEAD
class InvalidFunctionInput(Exception):
=======
class InvalidDataType(Exception):
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
    pass

def getRoot(url:str):
    return etree.fromstring(urllib.request.urlopen(url).read())
    
<<<<<<< HEAD
def can_file_metar(metar_node, field_id:str) -> bool:
    '''Return filing legality based on current conditions'''
    vis_at_dest = float(metar_node.findall('.//*[station_id="' + field_id 
        + '"]/visibility_statute_mi')[0].text)
    print('In function "can_file_metar" the visibility at ' + field_id + ' is ' 
=======
def can_file_metar(metar_node) -> bool:
    '''Return filing legality based on current conditions'''
    vis_at_dest = float(metar_node.findall('.//*[station_id="' + DEST_ID 
        + '"]/visibility_statute_mi')[0].text)
    print('In function "can_file_metar" the visibility at ' + DEST_ID + ' is ' 
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
            + '{:.1f}'.format(vis_at_dest) + 'sm, which is ', end='')
    if vis_at_dest >= FILING_MINS['vis']:
        print('greater than or equal to ', end='')
    else:
        print('less than ', end='')
<<<<<<< HEAD
    # Reference: https://mkaz.blog/code/python-string-format-cookbook/
=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
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

<<<<<<< HEAD
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
    return vis_at_dest >= ALT_REQ['ceiling'] and ceil_at_dest >= ALT_REQ['ceiling']
=======
def req_alt(node):
    pass
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4

def print_raw_metar(field:str) -> None:
    '''Print the raw metar for a given 4-letter identifier'''
    print(metar_root.findall('.//*[station_id="' + field 
        + '"]/raw_text')[0].text)

def print_node(node, indent:int = 0):
    '''Print an XML tree'''
    print(indent * '\t', end='')
    print(node.tag if node.text == None else node.tag + ': ' + node.text)
    if len(node.findall('*')) > 0:
        for child in node:
            print_node(child, indent + 1)

<<<<<<< HEAD
def genBadFieldList() -> List[str]:
    country_string = 'ar br bg ca cl cn dk eg ee fr de in ie il it jp nl nz kp '
    country_string += 'no ph ru sg za kr tr ua ae gb us ve vn'
    country_list = country_string.split()
    country_choice = random.choice(country_list)
    print('country_choice is ' + country_choice)
    bad_field_url = makeUrl('country', [], country_choice)
    bad_field_root = getRoot(bad_field_url)
    bad_fields_list = [] 
    for field in bad_field_root.findall('.//Station'):
        bad_fields_list.append(field.find('station_id').text)
    print('bad_fields_list contains ' + str(len(bad_fields_list)) + ' elements')
    rand_field_list = []
    for i in range(0,1000):
        rand_field_list.append(random.choice(bad_fields_list))
    bad_metar_url = makeUrl('METAR', rand_field_list)
    bad_metar_root = getRoot(bad_metar_url)
    bad_metars = bad_metar_root.findall('.//METAR')
    bad_metars = list(filter(lambda metar:
        not re.search('\d+', metar.find('station_id').text) and
        metar.find('visibility_statute_mi') is not None and
        float(metar.find('visibility_statute_mi').text) < ALT_REQ['vis'],
        bad_metars))
    print(str(len(bad_metars)) + ' fields have visibility < ' + 
            str(ALT_REQ['vis']))
    bad_field_ids = []
    for metar in bad_metars:
        bad_field_ids.append(metar.find('station_id').text)
    return bad_field_ids

=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
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
<<<<<<< HEAD
#    for field in field_root.findall('.//Station'):
#        if not field.find('station_id').text in DEST_ID:
#            print(field.find('station_id').text + ' is ' 
#                    + '{:5.0f}'.format(coord_man.dist_between_coords(home_lat, 
#                        home_lon, 
#                        field.find('latitude').text, 
#                        field.find('longitude').text)) 
#                    + ' statute miles from ' 
#                    + DEST_ID)
=======
    for field in field_root.findall('.//Station'):
        if not field.find('station_id').text in DEST_ID:
            print(field.find('station_id').text + ' is ' 
                    + '{:5.0f}'.format(coord_man.dist_between_coords(home_lat, 
                        home_lon, 
                        field.find('latitude').text, 
                        field.find('longitude').text)) 
                    + ' statute miles from ' 
                    + DEST_ID)
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4

    # webbrowser.open(taf_url)
    # webbrowser.open(metar_url)
    # webbrowser.open(field_url)

    # https://docs.python.org/2/library.xml.etree.elementtree.html#elementtree-xpath
    metars = metar_root.findall('.//METAR')
<<<<<<< HEAD

    print('Can I legally file to ' + DEST_ID + '?')
    print_raw_metar(DEST_ID)
    print('can_file_metar: ' + str(can_file_metar(metar_root, DEST_ID)))
=======
    for metar in metars:
        print(metar.find('raw_text').text)

    print('Can I legally file to ' + DEST_ID + '?')
    print_raw_metar(DEST_ID)
    print('can_file_metar: ' + str(can_file_metar(metar_root)))
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
    print('has_ceiling: ' + str(has_ceiling(metar_root.findall('.//*[station_id="' 
        + DEST_ID + '"]/sky_condition'))))
    print('ceiling: ' + str(get_ceiling(metar_root.findall('.//*[station_id="'
        + DEST_ID + '"]/sky_condition'))))
    print('visibility: ' + get_vis(metar_root.find('.//*[station_id="'
        + DEST_ID + '"]')))
<<<<<<< HEAD
    if can_file_metar(metar_root, DEST_ID):
        print('Do I require an alternate to file to ' + DEST_ID + '?')
        print('req_alt: ' + str(req_alt(metar_root)))


=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
    timeRegex = re.compile(r'''       # Strings are of form YYYY-MM-DDTHH:MM:SSZ
        ^                   # start of string
        (?P<yr>20\d{2})-    # grab 4-digit year (as long as it is in the range
                            # 2000-2099) and put it in named group "yr"
        (?P<mon>\d{2})-     # grab 2-digit month and put it in named group "mon"
        (?P<day>\d{2})T     # grab 2-digit day/date and put in named group "day"
        (?P<hr>\d{2}):      # grab 2-digit hour and put in named group "hr"
        (?P<min>\d{2}):     # grab 2-digit minute and put in named group "min"
        \d{2}Z$             # no need to put seconds in a group
        ''', re.VERBOSE|re.IGNORECASE)
    test_time = metar_root.findall('.//METAR/observation_time')[0].text
    result = re.search(timeRegex, test_time).group()
    print('Result: ', result)

if len(sys.argv) > 1:
    list_valid = True
    for arg in sys.argv[1:]:
        if re.match(r'\b[a-zA-Z]{4}\b', arg) == None:
            list_valid = False
            print('The command line argument "' + arg + '" did not match '
                    + 'the pattern for a valid ICAO identifier.')
    if list_valid:
        TEST_FIELDS = sys.argv[1:]
        DEST_ID = TEST_FIELDS[0]

<<<<<<< HEAD
TEST_FIELDS = genBadFieldList()
DEST_ID = TEST_FIELDS[0]

=======
>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
taf_url = makeUrl('tafs', TEST_FIELDS)    
metar_url = makeUrl('metars', TEST_FIELDS)    
field_url = makeUrl('fields', TEST_FIELDS)    
urls = [taf_url, metar_url, field_url]
    
taf_root = getRoot(taf_url)
metar_root = getRoot(metar_url)
field_root = getRoot(field_url)
roots = [taf_root, metar_root, field_root]

<<<<<<< HEAD
# reference https://stackoverflow.com/a/419185
if __name__ == '__main__':
    pass
=======
if __name__ == '__main__':
    pass

>>>>>>> b3d1dd67d076534d98588a404b2c64f01bd363a4
