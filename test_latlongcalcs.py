#!/usr/bin/env python3

import scripts.latlongcalcs
import unittest

class LatLongTestCase(unittest.TestCase):
    """Tests for 'latlongcalcs.py'."""
    def test_hav_bad_input(self):
        """hav should fail if dataType is not numeric"""
        self.assertRaises(ValueError, hav('45'))

if __name__ == '__main__':
    unittest.main()
