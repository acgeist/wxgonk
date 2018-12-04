#!/usr/bin/env python3

from typing import List

def make_adds_url(dataType:str, stationList:List[str], country:str = 'us') -> str:
    '''Make the URL for each dataset'''
    if not isinstance(dataType, str):
        raise InvalidFunctionInput("Data type must be a string")
    if not dataType.upper() in ['TAFS', 'TAF', 'METAR', 'METARS', 'FIELD', 'FIELDS',
            'COUNTRY']:
        raise InvalidFunctionInput("Data type must be 'TAFS', 'TAF', " 
        + "'METAR', 'METARS', 'FIELD', 'FIELDS', or COUNTRY")
    if not is_valid_country(country.upper()):
        raise InvalidFunctionInput("Function make_adds_url was passed " + country +
                ", which was not recognized as a valid 2-letter identifier." +
                " reference https://laendercode.net/en/2-letter-list.html.")
    if not re.search('[a-z]{2}', country.lower()):
        raise InvalidFunctionInput("country must be a 2-letter abbreviation " + 
                "in accordance with ISO-3166-1 ALPHA-2.")
    url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?'
    url += 'requestType=retrieve'
    url += '&format=xml'
    if dataType.upper() in ['TAFS', 'TAF']:
        url += '&dataSource=tafs'
        url += '&hoursBeforeNow=24'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['METAR', 'METARS']:
        url += '&dataSource=metars'
        # Don't use METAR if unable to get one newer than 3 hours
        url += '&hoursBeforeNow=3'
        url += '&mostRecentForEachStation=true'
    elif dataType.upper() in ['FIELDS', 'FIELD']:
        url += '&dataSource=stations'
    elif dataType.upper() in ['COUNTRY']:
        url += '&dataSource=stations'
        url += '&stationString=~' + country
        return url
    else:
        return 'https://www.aviationweather.gov/adds/dataserver_current'
    url += '&stationString='
    url += '%20'.join(stationList)
    return url
