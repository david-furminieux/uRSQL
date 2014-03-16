from parsley import makeGrammar

from levelSQL import astnodes


__GRAMMAR__ = r'''

###############################################################################
#                              STATEMENTS
#

stmt =
      ( selectStmt
#     | insertStmt
#     | deleteStmt
#     | updateStmt
#     | createStmt
#     | dropStmt
      ):s
      SEMICOLON ws
      -> s
###############################################################################
#                           SELECT STATEMENT
#

selectStmt = selectFactor:f1 #((UNION|EXCEPT) ALL? selectFactor)*
             -> f1

selectFactor = selectTerm:t1 #(INTERSECT ALL? selectTerm)*:rest
             -> t1
selectTerm =
           ( simpleSelectStmt
           | LPAREN selectStmt:s RPAREN ->s
           ):s (AS ws id)?
           -> s

simpleSelectStmt = SELECT selectOptList projection:proj
                   FROM relation:rel
                   (WHERE predicate)?:selection 
                   #(GROUP BY exprList:gLst (WITH ROLLUP)?:rollup)?
                   #(HAVING predicate:having)?
                   #(ORDER BY ordering:ordering)?
                   -> nodes.SimpleSelection(rel, proj, selection)

selectOptList = (selectOpt)*

selectOpt = DISTINCT 

projection = STAR
           | renamedExprList

renamedExprList = renamedExpr (COMMA renamedExpr)*

renamedExpr = expr (AS ws id)?

relation = simpleRelation:r1
           (COMMA simpleRelation)*:lst -> [r1]+lst 

simpleRelation = ws id:name -> nodes.SimpleRelation(name)

ordering = orderExpr:e1 (COMMA orderExpr)*:rest -> [e1]+rest

orderExpr = expr (ASC|DESC)?

###############################################################################
#                                LOGIC
predicate = lfactor:f1 ( OR lfactor)*:lst ws
          -> f1 if len(lst)==0 else nodes.Disjunction([f1]+lst)

lfactor = negatedTerm:t1 ( AND negatedTerm)*:lst
        -> t1 if len(lst)==0 else nodes.Conjunction([t1]+lst)

negatedTerm = (NOT)*:negs lterm:t
            -> t if len(negs) % 2 == 0 else nodes.Negation(t)

lterm = TRUE
      | FALSE
      | LPAREN predicate:p RPAREN -> p
      | expr:e1 compOp:op expr:e2 -> op(e1, e2)
#       | expr:e1 BETWEEN expr:e2 AND expr:e3
#       | expr:e1 LIKE string
#       | expr:e1 IN LPAREN exprList RPAREN
#       | expr:e IS NOT? NULL
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
       -> f1 if len(lst)==0 else nodes.SummExpression([nodes.Addition(f1)]+lst)

exprOp = PLUS  -> nodes.Addition
       | MINUS -> nodes.Substraction

exprList = expr:e1 (COMMA expr:e -> e)*:lst
         | -> []

factor = term:t1 (factorOp:op term:t -> op(t))*:lst
         -> t1 if len(lst)==0 else nodes.ProductExpression(
                                      [nodes.Multiplication(t1)]+lst
                                   )

factorOp = STAR    -> nodes.Multiplication
         | SLASH   -> nodes.Division
         | PERCENT -> nodes.Modulo

term = ~(TRUE|FALSE)
     ws 
     ( functionCall
     | constant
     | path
#     | CASE (WHEN predicate THEN expr)+ (ELSE expr)? END
#     | CASE expr (WHEN expr THEN expr)+ (ELSE expr)? END
     | LPAREN expr:e RPAREN -> e
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

id = <('_'| letter) (letterOrDigit|'_'|'-')*>
ws =
   ( ' ' | '\t' | '\n' | '\r'
   | '#' ( ~'\n' anything)* '\n'
   )*

ALL       = ws 'ALL'
AND       = ws 'AND'
AS        = ws 'AS'
ASC       = ws 'ASC'
BETWEEN   = ws 'BETWEEN'
BY        = ws 'BY'
CASE      = ws 'CASE'
DESC      = ws 'DESC'
DISTINCT  = ws 'DISTINCT'
EXCEPT    = ws 'EXCEPT'
FALSE     = ws 'FALSE' -> nodes.LogicValue(False)
FROM      = ws 'FROM'
GROUP     = ws 'GROUP'
HAVING    = ws 'HAVING'
IN        = ws 'IN'
INTERSECT = ws 'INTERSECT'
IS        = ws 'IS'
LIKE      = ws 'LIKE'
NOT       = ws 'NOT'
NULL      = ws 'NULL' -> nodes.NullValue()
OR        = ws 'OR'
ORDER     = ws 'ORDER'
ROLLUP    = ws 'ROLLUP'
SELECT    = ws 'SELECT'
TRUE      = ws 'TRUE'  -> nodes.LogicValue(True)
UNION     = ws 'UNION'
WHERE     = ws 'WHERE'
WITH      = ws 'WITH'

GREATER       = ws '>'
GREATER_EQUAL = ws '>='
LESS          = ws '<'
LESS_EQUAL    = ws '<='
UNEQUAL1      = ws '!='
UNEQUAL2      = ws '<>'
EQUAL1        = ws '=='
EQUAL2        = ws '='
SIMILAR       = ws '><'

PLUS      = ws '+'
MINUS     = ws '-'
LPAREN    = ws '('
RPAREN    = ws ')'
DOT       = '.'
STAR      = ws '*'
SLASH     = ws '/'
PERCENT   = ws '%'
SEMICOLON = ws ';'
COMMA     = ws ','

DQUOTE = '"'
SQUOTE = '\''
'''

SQLPrser = makeGrammar(__GRAMMAR__, {'nodes': astnodes})
