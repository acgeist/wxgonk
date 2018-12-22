#!/usr/bin/env python3

import latlongcalcs
import unittest
import math

class LatLongTestCase(unittest.TestCase):
    """Tests for 'latlongcalcs.py'."""
    def test_hav_bad_input(self):
        """hav should fail if dataType is not numeric"""
        self.assertRaises(ValueError, lambda: latlongcalcs.hav('$'))
        self.assertRaises(ValueError, lambda: latlongcalcs.hav('ge'))
    def test_known_values_hav(self):
        #TODO: make a list of known values and iterate through it
        # Used Wolfram Alpha to check answers
        self.assertEqual(latlongcalcs.hav(0), 0)
        self.assertAlmostEqual(latlongcalcs.hav(math.pi/6), 0.066987298)
        self.assertAlmostEqual(latlongcalcs.hav(-math.pi/6), 0.066987298)
        self.assertAlmostEqual(latlongcalcs.hav(math.pi/4), 0.146446609)
        self.assertAlmostEqual(latlongcalcs.hav(-math.pi/4), 0.146446609)
        self.assertAlmostEqual(latlongcalcs.hav(math.pi/3), 0.25)
        self.assertAlmostEqual(latlongcalcs.hav(-math.pi/3), 0.25)
        self.assertAlmostEqual(latlongcalcs.hav(math.pi/2), 0.5)
        self.assertAlmostEqual(latlongcalcs.hav(-math.pi/2), 0.5)
        self.assertAlmostEqual(latlongcalcs.hav(math.pi*2), 0)
        self.assertAlmostEqual(latlongcalcs.hav(-math.pi*2), 0)
    def test_known_values_hdg(self):
        self.assertAlmostEqual(latlongcalcs.hdg_between_coords(
            36, 127, 37, 127), 0)
        self.assertAlmostEqual(latlongcalcs.hdg_between_coords(
            36, 126, 36, 127), 90, 0)
        self.assertAlmostEqual(latlongcalcs.hdg_between_coords(
            37, 127, 36, 127), 180)
        self.assertAlmostEqual(latlongcalcs.hdg_between_coords(
            36, 127, 36, 126), 270, 0)

if __name__ == '__main__':
    unittest.main()
