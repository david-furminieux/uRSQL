from parsley import makeGrammar

from levelSQL import astnodes


__GRAMMAR__ = r'''

###############################################################################
#                              STATEMENTS
#
stmts = stmt+

stmt =
      ( selectStmt
      | insertStmt
#     | deleteStmt
#     | updateStmt
      | createStmt
      | dropStmt
      ):s
      SEMICOLON ws
      -> s

###############################################################################
#                           CREATE STATEMENT
#
createStmt = CREATE
           ( DATABASE databaseName:name -> nodes.CreateDatabaseStatement(name)
           | UNIQUE?:unique INDEX indexSpec(unique)
           | TEMPORARY?:temp TABLE tableSpec(temp)
           | MATERIALIZED?:mat VIEW viewName:name AS selectStmt:stmt
             -> nodes.CreateViewStatement(name, mat, stmt)
           )

tableSpec :temp = simpleRelation:name LPAREN tableElemList:elemLst RPAREN
                  (tableOptions)?:opts
                  -> nodes.CreateTableStatement(name, elemLst, opts)

tableElemList = tableElem (COMMA tableElem)*

tableElem = colName colType colConstraint?
          | tableConstraint

tableOptions = tableOption:head (COMMA tableOption)*:tail
               -> [head]+tail

tableOption = ws

colConstraint = (CONSTRAINT constraintName)?
                ( NOT NULL
                | NULL
                | CHECK LPAREN predicate RPAREN
                | DEFAULT expr
                | PRIMARY KEY
                | REFERENCES simpleRelation (LPAREN colName:name RPAREN -> name)?
                  (ON DELETE action)? (ON UPDATE action)?
                )+

action = IGNORE | CASCADE | SET NULL

tableConstraint = (CONSTRAINT constraintName)?
                ( CHECK LPAREN expr RPAREN
                | PRIMARY KEY LPAREN colNameList RPAREN
                | UNIQUE LPAREN colNameList RPAREN
                | PRIMARY KEY LPAREN colNameList RPAREN
                | FOREIGN KEY LPAREN colNameList RPAREN
                  REFERENCES simpleRelation LPAREN colNameList RPAREN
                  (ON DELETE action)? (ON UPDATE action)?
                )

indexSpec :unique = indexName?:idxName
          ON simpleRelation:rel LPAREN exprList:lst RPAREN
          (USING idxType)?:method
          -> nodes.CreateIndexStatement(idxName, rel, unique, lst, method)  
idxType = ws id:name

databaseName = ws id:name

indexName = ws id:name

viewName = ws id:name

colNameList = colName (COMMA colName)*

colName = ws id:name

constraintName = ws id:name

###############################################################################
#                           INSERT STATEMENT
#
insertStmt = INSERT INTO simpleRelation:rel
             (LPAREN idList:lst RPAREN -> lst)?:ids
             ( VALUES valuesList:lst -> nodes.ExplicitRelation(lst)
             | selectStmt
             ):source -> nodes.InsertStatement(rel, ids, source)

idList = ws id:id1 (COMMA ws id)*:lst -> [id1]+lst

valuesList = values:first (COMMA values)*:lst
             -> [first]+lst

values = LPAREN constantList:lst RPAREN -> lst

constantList = constant:c1 (COMMA constant)*:lst
               -> [c1]+lst
 
###############################################################################
#                            DROP STATEMENT
#
dropStmt = DROP
         ( DATABASE databaseNameList:lst -> nodes.DropDatabaseStatement(lst)
         | INDEX indexNameList:lst       -> nodes.DropIndexStatement(lst)
         | TABLE simpleRelList:lst       -> nodes.DropTableStatement(lst)
         | VIEW viewNameList:lst         -> nodes.DropViewStatement(lst) 
         )

databaseNameList = databaseName:db1 (COMMA databaseName)*:rest
                   -> db1 if len(rest)==0 else [db1]+rest

indexNameList = indexName:i1 (COMMA indexName)*:rest
                -> i1 if len(rest)==0 else [i1]+rest

simpleRelList = simpleRelation:r1 (COMMA simpleRelation)*:rest
                -> r1 if len(rest)==0 else [r1]+rest

viewNameList = viewName:v1 (COMMA viewName)*:rest

###############################################################################
#                           SELECT STATEMENT
#
selectStmt = selectFactor:f1 ((UNION|EXCEPT) ALL? selectFactor)*:rest
             -> f1 if len(rest)==0 else [f1]+rest

selectFactor = selectTerm:t1 (INTERSECT ALL? selectTerm)*:rest
               -> t1 if len(rest)==0 else [t1]+rest

selectTerm = ( simpleSelectStmt
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
#                                TYPES
#

colType = VARCHAR LPAREN length RPAREN
        | CHAR LPAREN length RPAREN
        | BIT LPAREN length RPAREN
        | NUMERIC LPAREN length (COMMA length)? RPAREN
        | DECIMAL LPAREN length (COMMA length)? RPAREN
        | INTEGER
        | INT
        | SMALLINT
        | FLOAT LPAREN length RPAREN
        | REAL 
        | DOUBLE PRECISION
        | DATETIME (WITH TIME ZONE)?
        | DATE 
        | TIMESTAMP (WITH TIME ZONE)?
        | TIME (WITH TIME ZONE)?
        | BOOL

length = <digit+>:ds -> int(ds)

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
             -> nodes.FunctionCall(name, lst)

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

ALL          = ws 'ALL'
AND          = ws 'AND'
AS           = ws 'AS'
ASC          = ws 'ASC'
BETWEEN      = ws 'BETWEEN'
BIT          = ws 'BIT'
BOOL         = ws 'BOOL'
BY           = ws 'BY'
CASCADE      = ws 'CASCADE'
CASE         = ws 'CASE'
CHAR         = ws 'CHAR'
CHECK        = ws 'CHECK'
CONSTRAINT   = ws 'CONSTRAINT'
CREATE       = ws 'CREATE'
DATABASE     = ws 'DATABASE'
DATE         = ws 'DATE'
DATETIME     = ws 'DATETIME'
DECIMAL      = ws 'DECIMAL'
DEFAULT      = ws 'DEFAULT'
DELETE       = ws 'DELETE'
DESC         = ws 'DESC'
DISTINCT     = ws 'DISTINCT'
DOUBLE       = ws 'DOUBLE'
DROP         = ws 'DROP'
EXCEPT       = ws 'EXCEPT'
FALSE        = ws 'FALSE' -> nodes.LogicValue(False)
FLOAT        = ws 'FLOAT'
FROM         = ws 'FROM'
GROUP        = ws 'GROUP'
HAVING       = ws 'HAVING'
IGNORE       = ws 'IGNORE'
IN           = ws 'IN'
INDEX        = ws 'INDEX'
INSERT       = ws 'INSERT'
INT          = ws 'INT'
INTO         = ws 'INTO'
INTEGER      = ws 'INTEGER'
INTERSECT    = ws 'INTERSECT'
IS           = ws 'IS'
KEY          = ws 'KEY'
LIKE         = ws 'LIKE'
MATERIALIZED = ws 'MATERIALIZED'
NOT          = ws 'NOT'
NULL         = ws 'NULL' -> nodes.NullValue()
NUMERIC      = ws 'NUMERIC'
ON           = ws 'ON'
OR           = ws 'OR'
ORDER        = ws 'ORDER'
PRECISION    = ws 'PRECISION'
PRIMARY      = ws 'PRIMARY'
REAL         = ws 'REAL'
REFERENCES   = ws 'REFERENCES'
ROLLUP       = ws 'ROLLUP'
SELECT       = ws 'SELECT'
SMALLINT     = ws 'SMALLINT'
TABLE        = ws 'TABLE'
TEMPORARY    = ws 'TEMPORARY'
TIME         = ws 'TIME'
TIMESTAMP    = ws 'TIMESTAMP'
TRUE         = ws 'TRUE'  -> nodes.LogicValue(True)
UNION        = ws 'UNION'
UNIQUE       = ws 'UNIQUE'
UPDATE       = ws 'UPDATE'
USING        = ws 'USING'
VALUES       = ws 'VALUES'
VARCHAR      = ws 'VARCHAR'
VIEW         = ws 'VIEW'
WHERE        = ws 'WHERE'
WITH         = ws 'WITH'
ZONE         = ws 'ZONE'

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
