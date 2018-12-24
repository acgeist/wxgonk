#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""Generate URLs for requests made to the Aviation Weather Center AWC)'s
Text Data Server (TDS). Reference https://aviationweather.gov/dataserver/
"""

import logging
import re
from typing import List

def make_adds_url(
        dataType:str, stationList:List[str] = [], country:str = ' ') -> str:
    """Make the URL for each dataset"""
    logging.debug('make_adds_url(datatype = ' + dataType
            + ', stationList = ' + ' '.join(stationList) + ', country = '
            + country + ') returns: ')
    valid_tafs_inputs = 'TAF TAFS FORECAST FORECASTS'.split()
    valid_metars_inputs = 'METAR METARS OBSERVATION OBSERVATIONS'.split()
    valid_stations_inputs = \
            'FIELD FIELDS STATION STATIONS AIRFIELD AIRFIELDS'.split() 
    valid_country_inputs = 'COUNTRY NATION REGION'.split()
    all_valid_inputs = \
            valid_tafs_inputs + valid_metars_inputs \
            + valid_stations_inputs + valid_country_inputs
    if not isinstance(dataType, str):
        raise InvalidFunctionInput("dataType must be a string")
    if not dataType.upper() in all_valid_inputs:
        raise InvalidFunctionInput("dataType must be one of: " \
                + ', '.join(all_valid_inputs))
    if not re.search('[a-z]{2}', country.lower()) and dataType in valid_country_inputs:
        raise InvalidFunctionInput("country must be a 2-letter abbreviation " 
                + "in accordance with ISO-3166-1 ALPHA-2.  Function was passed "
                + country)
    url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?'
    url += 'requestType=retrieve'
    url += '&format=xml'
    if dataType.upper() in ['TAFS', 'TAF', 'FORECAST']:
        url += '&dataSource=tafs'
        url += '&hoursBeforeNow=24'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['METAR', 'METARS', 'OBSERVATION']:
        url += '&dataSource=metars'
        # Don't use METAR if unable to get one newer than 3 hours
        url += '&hoursBeforeNow=3'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['FIELDS', 'FIELD', 'STATION', 'AIRFIELD']:
        url += '&dataSource=stations'
    elif dataType.upper() in ['COUNTRY']:
        url += '&dataSource=stations'
        url += '&stationString=~' + country
        logging.debug('<a href="' + url + '">' + url + '</a>')
        return url
    else:
        logging.debug('<a href="https://www.aviationweather.gov/adds/' 
                + 'dataserver_current">https://www.aviationweather.gov/'
                + 'adds/dataserver_current</a>')
        return 'https://www.aviationweather.gov/adds/dataserver_current'
    url += '&stationString='
    url += '%20'.join(stationList)
    logging.debug('<a href="' + url + '">' + url + '</a>')
    return url

def make_metar_taf_url(stationList:List[str]) -> str:
    url = 'https://www.aviationweather.gov/adds/metars?station_ids='
    url += '+'.join(stationList)
    url += '&submitmet=Get+Weather&std_trans=standard&chk_metars=on'
    url += '&hoursStr=most+recent+only&chk_tafs=on'
    return url

class InvalidFunctionInput(Exception):
    pass
