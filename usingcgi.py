#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

def called_from_cgi()->bool:
    """Return true if called from cgi, false if called directly"""
    # Reference https://stackoverflow.com/q/5077980
    req_meth_in_environ = 'REQUEST_METHOD' in os.environ
    true_str = "'REQUEST_METHOD' found in os.environ --> CGI was used."
    false_str = "'REQUEST_METHOD not found in os.environ --> CGI not used."
    logging.debug(true_str if req_meth_in_environ else false_str)
    return req_meth_in_environ
