
class ASTNode(object): pass

class ExpressionNode(ASTNode): pass

class ConstantNode(ASTNode):
    
    def __init__(self, value):
        super(ConstantNode, self).__init__()
        self._value = value

    def getValue(self):
        return self._value

class NullValue(ConstantNode):
    
    def __init__(self):
        super(NullValue, self).__init__(None)

class IntegerValue(ConstantNode):
    
    def __init__(self, value):
        super(IntegerValue, self).__init__(int(value))

class FloatValue(ConstantNode):
    
    def __init__(self, value):
        super(FloatValue, self).__init__(float(value))
