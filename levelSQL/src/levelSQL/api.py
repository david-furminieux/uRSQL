class LevelSQLException(Exception):
    '''
    a base class for all exceptions used within LevelSQL which are not std
    exceptions.
    '''

class SyntaxException(LevelSQLException):
    '''
    base class of all exceptions dealing with syntax and its inconsistencies.
    '''

class InconsistentStructure(SyntaxException): pass
    

class ASTVisitor(object):
    '''
    '''
