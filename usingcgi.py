#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def called_from_cgi()->bool:
    """Return true if called from cgi, false if called directly"""
    # Reference https://stackoverflow.com/q/5077980
    return 'REQUEST_METHOD' in os.environ
