from ometa.runtime import ParseError
import unittest

from levelSQL.astnodes import NullValue, IntegerValue, FloatValue
from levelSQL.parser import SQLPrser


class ParserTest(unittest.TestCase):

    def _parse(self, rule, text, *args):
        parser = SQLPrser(text)
        method = getattr(parser, rule)
        return method(*args)

    def testConstants(self):
        
        result = self._parse('expr', 'NULL')
        self.assertIsInstance(result, NullValue)
        
        self.assertRaises(ParseError, self._parse, 'expr', 'TRUE')
        self.assertRaises(ParseError, self._parse, 'expr', 'FALSE')
        
        result = self._parse('expr', '1')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), 1)

        result = self._parse('expr', '+1')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), 1)

        result = self._parse('expr', '-1')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), -1)

        result = self._parse('expr', '0xa')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), 10)
        
        result = self._parse('expr', '0o10')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), 8)
        
        result = self._parse('expr', '0b10')
        self.assertIsInstance(result, IntegerValue)
        self.assertEqual(result.getValue(), 2)
        

        result = self._parse('expr', '1.0')
        self.assertIsInstance(result, FloatValue)
        self.assertEqual(result.getValue(), 1.0)

        result = self._parse('expr', '.1')
        self.assertIsInstance(result, FloatValue)
        self.assertEqual(result.getValue(), .1)

        result = self._parse('expr', '1e6')
        self.assertIsInstance(result, FloatValue)
        self.assertEqual(result.getValue(), 1000000.0)

        result = self._parse('expr', ' "hello"')



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()