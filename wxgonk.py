#!/usr/bin/env python3
# wxgonk.py

import coord_man

import re 
import sys
import urllib.request
import webbrowser
# reference http://www.diveintopython3.net/your-first-python-program.html
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

TEST_FIELDS = 'KSEA RKSO RPLC LBPG EEEI'.split()
DEST_ID = TEST_FIELDS[0]
FILING_MINS = {'vis': 5.0, 'ceiling': 500}
ALT_REQ = {'vis': 3.0, 'ceiling': 2000}
ALT_MINS = {'vis': 2.0, 'ceiling': 1000}
NO_CEIL_VAL = 9999
timeRegex = ''

def makeUrl(dataType:str, stationList) -> str:
    '''Make the URL for each dataset'''
    dataType_valid = False
    if dataType.upper() in ['TAFS', 'TAF', 'METAR', 'METARS', 'FIELD', 'FIELDS']:
        dataType_valid = True
    if not dataType_valid:
        raise InvalidDataType("Data type must be 'TAFS', 'TAF', " 
        + "'METAR', 'METARS', 'FIELD', or 'FIELDS'")
    url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?'
    url += 'requestType=retrieve'
    url += '&format=xml'
    if dataType.upper() in ['TAFS', 'TAF']:
        url += '&dataSource=tafs'
        url += '&hoursBeforeNow=24'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['METAR', 'METARS']:
        url += '&dataSource=metars'
        url += '&hoursBeforeNow=3'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['FIELDS', 'FIELD']:
        url += '&dataSource=stations'
    else:
        return 'https://www.aviationweather.gov/adds/dataserver_current'
    url += '&stationString='
    url += '%20'.join(stationList)
    return url

class InvalidDataType(Exception):
    pass

def getRoot(url:str):
    return etree.fromstring(urllib.request.urlopen(url).read())
    
def can_file_metar(metar_node) -> bool:
    '''Return filing legality based on current conditions'''
    vis_at_dest = float(metar_node.findall('.//*[station_id="' + DEST_ID 
        + '"]/visibility_statute_mi')[0].text)
    print('In function "can_file_metar" the visibility at ' + DEST_ID + ' is ' 
            + '{:.1f}'.format(vis_at_dest) + 'sm, which is ', end='')
    if vis_at_dest >= FILING_MINS['vis']:
        print('greater than or equal to ', end='')
    else:
        print('less than ', end='')
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

def req_alt(node):
    pass

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
            print(field.find('station_id').text + ' is ' 
                    + '{:5.0f}'.format(coord_man.dist_between_coords(home_lat, 
                        home_lon, 
                        field.find('latitude').text, 
                        field.find('longitude').text)) 
                    + ' statute miles from ' 
                    + DEST_ID)

    # webbrowser.open(taf_url)
    # webbrowser.open(metar_url)
    # webbrowser.open(field_url)

    # https://docs.python.org/2/library.xml.etree.elementtree.html#elementtree-xpath
    metars = metar_root.findall('.//METAR')
    for metar in metars:
        print(metar.find('raw_text').text)

    print('Can I legally file to ' + DEST_ID + '?')
    print_raw_metar(DEST_ID)
    print('can_file_metar: ' + str(can_file_metar(metar_root)))
    print('has_ceiling: ' + str(has_ceiling(metar_root.findall('.//*[station_id="' 
        + DEST_ID + '"]/sky_condition'))))
    print('ceiling: ' + str(get_ceiling(metar_root.findall('.//*[station_id="'
        + DEST_ID + '"]/sky_condition'))))
    print('visibility: ' + get_vis(metar_root.find('.//*[station_id="'
        + DEST_ID + '"]')))
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

taf_url = makeUrl('tafs', TEST_FIELDS)    
metar_url = makeUrl('metars', TEST_FIELDS)    
field_url = makeUrl('fields', TEST_FIELDS)    
urls = [taf_url, metar_url, field_url]
    
taf_root = getRoot(taf_url)
metar_root = getRoot(metar_url)
field_root = getRoot(field_url)
roots = [taf_root, metar_root, field_root]

if __name__ == '__main__':
    pass

