from ometa.runtime import ParseError
import unittest

from levelSQL.astnodes import (NullValue, IntegerValue, FloatValue,
    SummExpression, StringValue, Addition, Substraction,
    ProductExpression, Multiplication, Division, Modulo, VariableValue,
    LogicConstant)
from levelSQL.parser import SQLPrser


class ParserTest(unittest.TestCase):

    def _parse(self, rule, text, *args):
        parser = SQLPrser(text)
        method = getattr(parser, rule)
        return method(*args)

    def testVariables(self):
        
        result = self._parse('expr', 'a')
        self.assertIsInstance(result, VariableValue)
        self.assertEqual(result.getColumnName(), 'a')
        self.assertIsNone(result.getRelationName())

        result = self._parse('expr', 'a.b')
        self.assertIsInstance(result, VariableValue)
        self.assertEqual(result.getColumnName(), 'b')
        self.assertEqual(result.getRelationName(), 'a')

        self.assertRaises(ParseError, self._parse, 'expr', 'a.a.a')

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
        self.assertIsInstance(result, StringValue)
        self.assertEqual(result.getValue(), 'hello')

        result = self._parse('expr', '"\\"\\n"')
        self.assertIsInstance(result, StringValue)
        self.assertEqual(result.getValue(), '"\n')

    def testExprCompunds(self):
        
        result = self._parse('expr', ' 1 + 1 ')
        self.assertIsInstance(result, SummExpression)
        self.assertEqual(len(result.getElems()), 2)
        for elem in result.getElems():
            self.assertIsInstance(elem, Addition)
            self.assertEqual(elem.getArgument(), IntegerValue(1))
        
        result = self._parse('expr', '1-2')
        self.assertIsInstance(result, SummExpression)
        self.assertEqual(len(result.getElems()), 2)
        self.assertIsInstance(result.getElems()[0], Addition)
        self.assertEqual(result.getElems()[0].getArgument(), IntegerValue(1))
        self.assertIsInstance(result.getElems()[1], Substraction)
        self.assertEqual(result.getElems()[1].getArgument(), IntegerValue(2))

        result = self._parse('expr', '1*1')
        self.assertIsInstance(result, ProductExpression)
        self.assertEqual(len(result.getElems()), 2)
        for elem in result.getElems():
            self.assertIsInstance(elem, Multiplication)
            self.assertEqual(elem.getArgument(), IntegerValue(1))

        result = self._parse('expr', '1/2')
        self.assertIsInstance(result, ProductExpression)
        self.assertEqual(len(result.getElems()), 2)
        self.assertIsInstance(result.getElems()[0], Multiplication)
        self.assertEqual(result.getElems()[0].getArgument(), IntegerValue(1))
        self.assertIsInstance(result.getElems()[1], Division)
        self.assertEqual(result.getElems()[1].getArgument(), IntegerValue(2))

        result = self._parse('expr', '1%2')
        self.assertIsInstance(result, ProductExpression)
        self.assertEqual(len(result.getElems()), 2)
        self.assertIsInstance(result.getElems()[0], Multiplication)
        self.assertEqual(result.getElems()[0].getArgument(), IntegerValue(1))
        self.assertIsInstance(result.getElems()[1], Modulo)
        self.assertEqual(result.getElems()[1].getArgument(), IntegerValue(2))

        result = self._parse('expr', '1*2+3')
        self.assertIsInstance(result, ProductExpression)
        self.assertEqual(len(result.getElems()), 2)
        self.assertIsInstance(result.getElems()[0], Multiplication)
        self.assertEqual(result.getElems()[0].getArgument(), IntegerValue(1))
        self.assertIsInstance(result.getElems()[1].getArgument(), SummExpression)

        result = self._parse('expr', '1+2*3')
        self.assertIsInstance(result, ProductExpression)
        self.assertEqual(len(result.getElems()), 2)
        self.assertIsInstance(result.getElems()[0], Multiplication)
        self.assertIsInstance(result.getElems()[0].getArgument(), SummExpression)

    def testLogicConstants(self):
        
        result = self._parse('predicate', 'TRUE')
        self.assertIsInstance(result, LogicConstant)
        self.assertTrue(result.getValue())

        result = self._parse('predicate', 'FALSE')
        self.assertIsInstance(result, LogicConstant)
        self.assertFalse(result.getValue())

        result = self._parse('predicate', 'NULL')
        self.assertIsInstance(result, LogicConstant)
        self.assertIsNone(result.getValue())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()