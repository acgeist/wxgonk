import wxgonk
import unittest


"""
class KnownValues(unittest.TestCase):
    known_values = ((1, 'I'),
                    (3250, 'MMMCCL'),
                    (3940, 'MMMCMXL'),
                    (3999, 'MMMCMXCIX'))

    def test_to_roman_known_values(self):
        '''to_roman should give known result with known input'''
        for integer, numeral in self.known_values:
           result = roman1.to_roman(integer)
           self.assertEqual(numeral, result)

    def test_from_roman_known_values(self):
        '''from_roman should give known result with known input'''
        for integer, numeral in self.known_values:
            result = roman1.from_roman(numeral)
            self.assertEqual(integer, result)
"""

class makeUrlBadInput(unittest.TestCase):
    def test_data_type_not_string(self):
        '''makeUrl should fail if dataType is not a string'''
    def test_invalid_data_type(self):
        '''makeUrl should fail with an invalid data type'''
        self.assertRaises(wxgonk.InvalidDataType, wxgonk.makeUrl, 'obs', ['KSEA'])

if __name__ == '__main__':
    unittest.main()
