import unittest
from levelSQL.parser import SQLPrser

class ParserTest(unittest.TestCase):

    def _parse(self, rule, text, *args):
        parser = SQLPrser(text)
        method = getattr(parser, rule)
        return method(*args)

    def testConstants(self):
        result = self._parse('expr', '1')
        print result

        result = self._parse('expr', '+1')
        print result

        result = self._parse('expr', '-1')
        print result

        result = self._parse('expr', '1.0')
        print result

        result = self._parse('expr', '.1')
        print result


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()