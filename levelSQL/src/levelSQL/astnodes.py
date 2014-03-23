from levelSQL.api import InconsistentStructure

class ASTNode(object):
    '''
    the base class of object representing all elements of the AST.
    '''
    
    def accept(self, visitor):
        raise NotImplementedError(type(self))

class Statement(ASTNode):
    '''
    the base class of all explicit statements
    '''

class CreateStatement(Statement):
    '''
    a statement representing the creation of something.
    '''

class CreateViewStatement(CreateStatement):
    '''
    CREATE VIEW
    '''
    
    def __init__(self, name, mat, relation):
        super(CreateViewStatement, self).__init__()
        self._name = name
        self._materialized = mat
        self._relation = relation

    def accept(self, visitor):
        visitor.startCreateView(self._name, self._materialized)
        self._relation.accept(visitor)
        visitor.stopCreateView(self._name, self._materialized)


class CreateIndexStatement(CreateStatement):
    '''
    CREATE INDEX
    '''
    
    def __init__(self, name, rel, unique, exprLst, method):
        super(CreateIndexStatement, self).__init__()
        self._name = name
        self._relName = rel
        self._isUnique = unique
        self._elems = exprLst
        self._method = method
    
    def accept(self, visitor):
        self.startCreateIndex(self, self._name, self._relaName, self._isUnique,
                              self._method)
        self._elems.accept(visitor)
        self.stopCreateIndex(self, self._name, self._relaName, self._isUnique,
                             self._method)

class CreateTableStatement(CreateStatement):
    '''
    CREATE TABLE
    '''
    
    def __init__(self, name, elems, options):
        super(CreateTableStatement, self).__init__()

class CreateDatabaseStatement(CreateStatement):
    '''
    CREATE DATABASE
    '''
    
    def __init__(self, name):
        super(CreateDatabaseStatement, self).__init__()
        self._name = name

class DropStatement(Statement):
    '''
    the base statement for all DROP statements
    '''
    
    def __init__(self, lst):
        super(DropStatement, self).__init__()
        self._elems = lst
    
    def getElements(self):
        return self._elems

class DropTableStatement(DropStatement):
    '''
    DROP TABLE
    '''
    
    def __init__(self, relList):
        super(DropTableStatement, self).__init__(relList)

class DropDatabaseStatement(DropStatement):
    '''
    DROP DATABASE
    '''
    
    def __init__(self, dbLst):
        super(DropDatabaseStatement, self).__init__(dbLst)

class DropIndexStatement(DropStatement):
    '''
    DROP INDEX
    '''
    
    def __init__(self, idxList):
        super(DropIndexStatement, self).__init__(idxList)

class DropViewStatement(DropStatement):
    '''
    DROP VIEW
    '''
    
    def __init__(self, viewLst):
        super(DropViewStatement, self).__init__(viewLst)

class InsertStatement(Statement):
    
    def __init__(self, rel, cols, source):
        super(InsertStatement, self).__init__()

class ExplicitRelation(object):
    
    def __init__(self, lst):
        super(ExplicitRelation, self).__init__()
        self._lst = lst

class Selection(Statement): pass

class SimpleSelection(Selection):
    
    def __init__(self, rel, proj, selection):
        super(SimpleSelection, self).__init__()
#         if not isinstance(rel, Relation):
#             raise InconsistentStructure(type(rel))
        if selection is not None and not isinstance(selection, LogicNode):
            raise InconsistentStructure(type(selection))
        self._rel = rel
        self._proj = proj
        self._selection = selection

class Relation(ASTNode): pass

class SimpleRelation(Relation):
    '''
    represents a simple table name. no join union or anything else applied.
    '''
    
    def __init__(self, name):
        super(SimpleRelation, self).__init__()
        self._name = name

    def getName(self):
        return self._name

class Constant(ASTNode):

    def __init__(self, value):
        super(Constant, self).__init__()
        self._value = value

    def getValue(self):
        return self._value
    
    def getTypeName(self):
        raise NotImplementedError(type(self))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self._value != other.getValue():
            return False
        return True
    
    def __repr__(self):
        return '<'+str(self._value)+'::'+self.getTypeName()+'>'

class LogicNode(ASTNode): pass

class LogicalCompound(LogicNode):

    def __init__(self, lst):    
        super(LogicalCompound, self).__init__()
        if not isinstance(lst, list):
            raise InconsistentStructure()
        for elem in lst:
            if not isinstance(elem, LogicNode):
                raise InconsistentStructure(type(elem))
        self._elems = lst
    
    def getElems(self):
        return self._elems

class Conjunction(LogicalCompound): pass

class Disjunction(LogicalCompound): pass

class Negation(LogicNode):
    
    def __init__(self, value):
        if not isinstance(value, LogicNode):
            raise InconsistentStructure(type(value))
        super(Negation, self).__init__()
        self._value = value

class Comparison(LogicNode):

    def __init__(self, lexpr, rexpr):
        super(Comparison, self).__init__()
        if not isinstance(lexpr, ExpressionNode):
            raise InconsistentStructure(type(lexpr))
        if not isinstance(rexpr, ExpressionNode):
            raise InconsistentStructure(type(rexpr))
        self._lexpr = lexpr
        self._rexpr = rexpr

class Similarity(Comparison): pass

class Greater(Comparison): pass

class GreaterEqual(Comparison): pass

class Unequality(Comparison): pass

class Equality(Comparison): pass

class LogicConstant(Constant, LogicNode): pass

class LogicValue(LogicConstant):
    '''
    an instance of this represent the constant TRUE of FALSE.
    '''
    
    def __init__(self, value):
        super(LogicValue, self).__init__(bool(value))

    def getTypeName(self):
        return 'BOOL'

class ExpressionNode(ASTNode):
    '''
    all nodes of this types can participate in building an expression.
    '''

class CompoundExpressionNode(ExpressionNode):
    
    def __init__(self, lst):
        super(CompoundExpressionNode, self).__init__()
        if not isinstance(lst, list):
            raise InconsistentStructure()
        for elem in lst:
            if not isinstance(elem, ArithmeticOperator):
                raise InconsistentStructure(type(elem))
        self._elems = lst
    
    def getElems(self):
        return self._elems

class SummExpression(CompoundExpressionNode): pass
    
class ProductExpression(CompoundExpressionNode): pass
    
class VariableValue(ExpressionNode):
    
    def __init__(self, relName, colName):
        super(VariableValue, self).__init__()
        if colName is None:
            colName, relName = relName, colName
        self._relName = relName
        self._colName = colName
    
    def getColumnName(self):
        return self._colName
    
    def getRelationName(self):
        return self._relName 

class FunctionCall(ExpressionNode):
    
    def __init__(self, funcName, exprList):
        super(FunctionCall, self).__init__()
        self._funcName = funcName
        self._args = exprList

class ConstantExpression(Constant, ExpressionNode):
    '''
    a leaf element in an expression, this is to be seen as a contant for the
    elements.
    '''

class NullValue(ConstantExpression, LogicConstant):
    '''
    a representation for the 'NULL' value.
    '''
    def __init__(self):
        super(NullValue, self).__init__(None)

    def getTypeName(self):
        return 'NULL'

class IntegerValue(ConstantExpression):
    '''
    an integer constant.
    '''
    
    def __init__(self, value):
        super(IntegerValue, self).__init__(int(value))

    def getTypeName(self):
        return 'INT'

class FloatValue(ConstantExpression):
    '''
    a float constant.
    '''
    
    def __init__(self, value):
        super(FloatValue, self).__init__(float(value))

    def getTypeName(self):
        return 'FLOAT'

class StringValue(ConstantExpression):
    '''
    a float constant
    '''

    def getTypeName(self):
        return 'STR'

class Operator(ASTNode): pass

class ArithmeticOperator(Operator):
    
    def __init__(self, arg):
        if not isinstance(arg, ExpressionNode):
            raise TypeError(type(arg))
        super(ArithmeticOperator, self).__init__()
        self._arg = arg
    
    def getArgument(self):
        return self._arg

class Addition(ArithmeticOperator): pass

class Substraction(ArithmeticOperator): pass

class Multiplication(ArithmeticOperator): pass

class Division(ArithmeticOperator): pass

class Modulo(ArithmeticOperator): pass
