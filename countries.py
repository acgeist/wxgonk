#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""Do stuff with ISO 3166 alpha-2 country codes.
Reference: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
"""

from typing import Dict

def make_country_dict(
        csv_file:str = 'data/country_list.csv') -> Dict[str, str]:
    """Make a dictionary containing the ISO 3166 two-letter code
    as the key and the country name as the value.  The data is read
    from a csv file.
    """
    country_dict = {}
    with open(csv_file) as country_csv:
        for line in country_csv:
            key, value = line.strip().split(',')
            country_dict[key] = value
    return country_dict

country_dict = make_country_dict()

def is_valid_country(country:str) -> bool:
    return country.upper() in country_dict

def country_name_from_code(code:str) -> str:
    """Return the full country name in English"""
    # TODO: error handling if code is not found
    return country_dict[code.upper()]
