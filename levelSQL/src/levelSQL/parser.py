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

constant = NULL | number | string

sign = PLUS | MINUS | -> ''

number = float | integer

exponent = ('e' | 'E') (PLUS | MINUS)? digit+

float = sign:s <digit*>:ds
        <( DOT digit+ exponent?
         | exponent
         )>:rest -> nodes.FloatValue(float(s+ds+rest))

integer = hexInt
        | octInt
        | binInt
        | sign:s decInt(s)
        
hexInt = '0x' <hexdigit+>:ds -> nodes.IntegerValue(int(ds, 16))

octInt = '0o' <octdigit+>:ds -> nodes.IntegerValue(int(ds, 8))

binInt = '0b' <bindigit+>:ds -> nodes.IntegerValue(int(ds, 2))

decInt :sign = <digit+>:ds -> nodes.IntegerValue(int(sign+ds))

hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x

octdigit = :x ?(x in '01234567') -> x

bindigit = :x ?(x in '01') -> x

string = ws DQUOTE (escapedChar | ~DQUOTE anything)*:c DQUOTE -> ''.join(c)

escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
                   |('/' -> '/')    |('b' -> '\b')
                   |('f' -> '\f')   |('n' -> '\n')
                   |('r' -> '\r')   |('t' -> '\t')
                   |('\'' -> '\'')  | escapedUnicode)
 
escapedUnicode = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16))

###############################################################################
#                                   TOKENS
#

NULL    = ws 'NULL' -> nodes.NullValue()

PLUS    = ws '+'
MINUS   = ws '-'
LPAREN  = ws '('
RPAREN  = ws ')'
DOT     = '.'
STAR    = ws '*'
SLASH   = ws '/'
PERCENT = ws '%'

DQUOTE = '"'
SQUOTE = '\''
'''

SQLPrser = makeGrammar(__GRAMMAR__, {'nodes': astnodes})
