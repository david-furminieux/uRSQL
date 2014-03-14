
class LevelSQLException(Exception):
    '''
    a base class for all exception used within LevelSQL which are not std
    exceptions.
    '''

class SyntaxException(LevelSQLException):
    '''
    base class of all exception dealing with syntax and its inconsistencies.
    '''

class InconsistentStructure(SyntaxException): pass
    

class ASTVisitor(object):
    '''
    '''
