from parsley import makeGrammar

from levelSQL import astnodes


__GRAMMAR__ = r'''

###############################################################################
#                                  LOGIC
predicate = lfactor:f1 ( AND lfactor)*:lst ws
          -> f1 if len(lst)==0 else nodes.Conjunction([f1]+lst)

lfactor = negatedTerm:t1 ( OR negatedTerm)*:lst
        -> t1 if len(lst)==0 else nodes.Disjunction([t1]+lst)

negatedTerm = (NOT)*:negs lterm:t
            -> t if len(negs) % 2 == 0 else nodes.Negation(t)

lterm = TRUE
      | FALSE
      | expr:e1 compOp:op expr:e2 -> op(e1, e2)
      | NULL

compOp = SIMILAR       -> nodes.Similarity
       | GREATER_EQUAL -> nodes.GreaterEqual
       | GREATER       -> nodes.Greater
       | UNEQUAL2      -> nodes.Unequality
       | LESS_EQUAL    -> lambda x,y: nodes.GreaterEqual(y,x)
       | LESS          -> lambda x,y: nodes.Greater(y,x)
       | UNEQUAL1      -> nodes.Unequality
       | EQUAL1        -> nodes.Equality
       | EQUAL2        -> nodes.Equality

###############################################################################
#                                EXPRESSIONS
#
expr = factor:f1 ( exprOp:op factor:f -> op(f))*:lst ws
     -> f1 if len(lst)==0 else nodes.ProductExpression(
                                 [nodes.Multiplication(f1)]+lst
                               )

exprList = expr:e1 (COMMA expr:e -> e)* lst
         | -> []

exprOp = STAR    -> nodes.Multiplication
       | SLASH   -> nodes.Division
       | PERCENT -> nodes.Modulo

factor = term:t1 (factorOp:op term:t -> op(t))*:lst
       -> t1 if len(lst)==0 else nodes.SummExpression([nodes.Addition(t1)]+lst)

factorOp = PLUS  -> nodes.Addition
         | MINUS -> nodes.Substraction

term = ~(TRUE|FALSE) 
     ( functionCall
     | constant
     | path
     )
functionCall = id:name LPAREN exprList:lst RPAREN

path = id:i1 (DOT id)?:i2 -> nodes.VariableValue(i1, i2)

constant = NULL | number | string

sign = PLUS | MINUS | -> ''

number = float | integer

exponent = ('e' | 'E') (PLUS | MINUS)? digit+

float = ws sign:s <digit*>:ds
        <( DOT digit+ exponent?
         | exponent
         )>:rest -> nodes.FloatValue(float(s+ds+rest))

integer = ws
        ( hexInt
        | octInt
        | binInt
        | sign:s decInt(s)
        )

hexInt = '0x' <hexdigit+>:ds -> nodes.IntegerValue(int(ds, 16))

octInt = '0o' <octdigit+>:ds -> nodes.IntegerValue(int(ds, 8))

binInt = '0b' <bindigit+>:ds -> nodes.IntegerValue(int(ds, 2))

decInt :sign = <digit+>:ds -> nodes.IntegerValue(int(sign+ds))

hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x

octdigit = :x ?(x in '01234567') -> x

bindigit = :x ?(x in '01') -> x

string = ws DQUOTE (escapedChar | ~DQUOTE anything)*:c DQUOTE
       -> nodes.StringValue(''.join(c))

escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
                   |('/' -> '/')    |('b' -> '\b')
                   |('f' -> '\f')   |('n' -> '\n')
                   |('r' -> '\r')   |('t' -> '\t')
                   |('\'' -> '\'')  | escapedUnicode)
 
escapedUnicode = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16))

###############################################################################
#                                   TOKENS
#

AND   = ws 'AND'
FALSE = ws 'FALSE' -> nodes.LogicValue(False)
NOT   = ws 'NOT'
OR    = ws 'OR'
TRUE  = ws 'TRUE'  -> nodes.LogicValue(True)

NULL    = ws 'NULL' -> nodes.NullValue()

id = <('_'| letter) (letterOrDigit|'_'|'-')*>

GREATER       = ws '>'
GREATER_EQUAL = ws '>='
LESS          = ws '<'
LESS_EQUAL    = ws '<='
UNEQUAL1      = ws '!='
UNEQUAL2      = ws '<>'
EQUAL1        = ws '=='
EQUAL2        = ws '='
SIMILAR       = ws '><'

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
