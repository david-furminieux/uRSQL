from parsley import makeGrammar

from levelSQL import astnodes


__GRAMMAR__ = r'''

###############################################################################
#                                EXPRESSIONS
#
expr = factor:f1 ( (STAR|SLASH|PERCENT) factor)*:lst
     -> f1 if len(lst)==0 else [f1]+lst

factor = term:t1 ( (PLUS|MINUS) term)*:lst
       -> t1 if len(lst)==0 else [t1]+lst
       
term = constant

constant = NULL
         | number
         | string
         
sign = PLUS
     | MINUS
     | -> ''

number = <sign>:s
       ( intPart:ds
         (floatPart(s ds)
         | -> int(s + ds)
         )
       )
intPart = (digit1_9:first digits:rest -> first + rest) | digit


# integer = sign:s <digit+>:v -> s*int(v)
# 
# float = sign:s <digit* DOT digit+>:v -> s*float(v) 

# value = ws (string | number | object | array
#            | 'true'  -> True
#            | 'false' -> False
#            | 'null'  -> None)
# string = '"' (escapedChar | ~'"' anything)*:c '"' -> ''.join(c)
# escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
#                    |('/' -> '/')    |('b' -> '\b')
#                    |('f' -> '\f')   |('n' -> '\n')
#                    |('r' -> '\r')   |('t' -> '\t')
#                    |('\'' -> '\'')  | escapedUnicode)
# hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x
# escapedUnicode = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16))
# digit = :x ?(x in '0123456789') -> x
# digits = <digit*>
# digit1_9 = :x ?(x in '123456789') -> x
# floatPart :sign :ds = <('.' digits exponent?) | exponent>:tail
#                     -> float(sign + ds + tail)
# exponent = ('e' | 'E') ('+' | '-')? digits


###############################################################################
#                                   TOKENS
#

NULL    = ws 'NULL' -> nodes.NullValue()

PLUS    = ws '+'
MINUS   = ws '-'
LPAREN  = '('
RPAREN  = ')'
DOT     = '.'
STAR    = '*'
SLASH   = '/'
PERCENT = '%'

DQUOTE = '"'
SQUOTE = '\''
'''

SQLPrser = makeGrammar(__GRAMMAR__, {'nodes', astnodes})
